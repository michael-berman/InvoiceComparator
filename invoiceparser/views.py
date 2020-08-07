import os
import tempfile
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import boto3
from decouple import config

from .models import Supplier, Invoice, InvoiceItem
from .services import save_line_items, parse_date


def index(request):
    supplier_list = Supplier.objects.order_by('id')
    context = {
        'supplier_list': supplier_list,
        'extracted_text': {},
        'file_name': ''
    }
    return render(request, 'invoiceparser/index.html', context)


def compare(request):
    supplier_list = Supplier.objects.order_by('id')
    context = {
        'supplier_list': supplier_list
    }
    return render(request, 'invoiceparser/compare.html', context)


def detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    suppliers = Supplier.objects.order_by('supplier_name')

    context = {
        'supplier': supplier,
        'suppliers': suppliers
    }
    return render(request, 'invoiceparser/detail.html', context)


def create(request, supplier_id):
    try:
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        try:
            invoice = Invoice.objects.get(
                invoice_number=request.POST['invoice_number'])
        except Invoice.DoesNotExist:
            invoice = None

        if invoice:
            raise KeyError("This Invoice has already been uploaded.")

        old_invoice_name = request.POST['old_invoice_name']
        new_invoice_name = request.POST['new_invoice_name']

        invoice = Invoice(supplier=supplier,
                          invoice_number=request.POST['invoice_number'],
                          invoice_date=parse_date(
                              request.POST['invoice_date']),
                          invoice_file=new_invoice_name)
        invoice.save()

        file_path = settings.BASE_DIR + '/' + old_invoice_name

        s3 = boto3.resource('s3')
        s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).upload_file(
            settings.BASE_DIR + '/' + old_invoice_name, new_invoice_name,
            ExtraArgs={'ACL': 'public-read'})

        if os.path.isfile(file_path):
            os.remove(file_path)

        i = 1
        while 'item' + str(i) in request.POST:
            item = request.POST['item' + str(i)]
            price = request.POST['price' + str(i)]
            InvoiceItem.objects.create(invoice=invoice,
                                       description=item,
                                       price=Decimal(price))
            i += 1

    except Exception as e:
        context = {
            'supplier': supplier,
            'suppliers': Supplier.objects.order_by('supplier_name'),
            'error_message': e.args[0]
        }
        return render(request, 'invoiceparser/detail.html', context)

    supplier_list = Supplier.objects.order_by('id')
    context = {
        'supplier_list': supplier_list,
        'extracted_text': {},
        'file_name': ''
    }
    return render(request, 'invoiceparser/index.html', context)


def upload_file(request):
    if request.method == 'POST':
        invoice_file = request.FILES.get('invoice')
        if request.FILES['invoice']:
            # s3 = boto3.resource('s3')
            # s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).upload_fileobj(
            #     invoice_file, invoice_file.name)

            meta_data = save_line_items(invoice_file)

            # # save file locally first for aws
            with open(invoice_file.name, 'wb+') as f:
                for chunk in invoice_file.chunks():
                    f.write(chunk)

            # data = open('test.txt', 'rb')

    supplier_list = Supplier.objects.order_by('id')
    context = {
        'supplier_list': supplier_list,
        'extracted_text': meta_data,
        'file_name': invoice_file.name,
    }
    return render(request, 'invoiceparser/index.html', context)


def load_invoice_items(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    invoices = Invoice.objects.filter(supplier=supplier)
    invoice_items = InvoiceItem.objects.filter(
        invoice__in=invoices.values('id')).order_by('description').values("description", "price")
    invoice_items_obj = {
        "list": invoice_items
    }
    return JsonResponse({"invoice_items": list(invoice_items)}, status=200)
