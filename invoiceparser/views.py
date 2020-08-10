import os
import tempfile
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
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
        'supplier_list': supplier_list
    }
    return render(request, 'invoiceparser/index.html', context)


def upload(request):
    supplier_list = Supplier.objects.order_by('id')
    context = {
        'supplier_list': supplier_list,
        'extracted_text': {},
        'file_name': ''
    }
    return render(request, 'invoiceparser/upload.html', context)


def compare(request):
    supplier_list = Supplier.objects.order_by('supplier_name')
    context = {
        'supplier_list': supplier_list
    }
    return render(request, 'invoiceparser/compare.html', context)


def invoice_list(request):
    supplier_list = Supplier.objects.order_by('supplier_name')
    context = {
        'supplier_list': supplier_list
    }
    return render(request, 'invoiceparser/invoice_list.html', context)


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
        invoice = None
        try:
            if 'invoice_number' in request.POST:
                invoice = Invoice.objects.get(
                    invoice_number=request.POST['invoice_number'])
        except Invoice.DoesNotExist:
            invoice = None

        if invoice:
            raise KeyError("This Invoice has already been uploaded.")

        if 'items-only' not in request.POST:
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

        for i in range(10):
            if 'item' + str(i) in request.POST:
                item = request.POST['item' + str(i)]
                price = request.POST['price' + str(i)]
                InvoiceItem.objects.create(supplier=supplier,
                                           invoice=invoice,
                                           description=item,
                                           price=Decimal(price))

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
    # return HttpResponseRedirect('invoiceparser/compare.html')
    # return render(request, 'invoiceparser/compare.html')
    return redirect('/invoiceparser/compare')


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
        'supplier_list': list(supplier_list),
        'extracted_text': meta_data,
        'file_name': invoice_file.name,
    }

    return render(request, 'invoiceparser/upload.html', context)


def load_invoice_items(request, supplier_id, search=''):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    invoices = Invoice.objects.filter(supplier=supplier)
    invoice_items = InvoiceItem.objects.filter(
        invoice__in=invoices.values('id')).order_by('description').values("id", "description", "price")
    if search:
        invoice_items = invoice_items.filter(description__icontains=search)
    return JsonResponse({"invoice_items": list(invoice_items)}, status=200)


def load_invoices(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    invoices = Invoice.objects.filter(supplier=supplier).order_by("invoice_date").values(
        "invoice_number", "invoice_date", "invoice_file")

    invoice_list = list(invoices)
    for invoice in invoice_list:
        invoice["invoice_file"] = settings.MEDIA_URL + invoice["invoice_file"]
    return JsonResponse({"invoices": list(invoices)}, status=200)


def search_invoice_items(request, supplier_id, search):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    invoices = Invoice.objects.filter(supplier=supplier)
    invoice_items = InvoiceItem.objects.filter(supplier=supplier).order_by(
        'description').values("id", "description", "price")
    return JsonResponse({"invoice_items": list(invoice_items)}, status=200)
