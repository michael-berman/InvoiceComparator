from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import os
import io
import ocrmypdf
import pdfplumber
import pandas as pd
from tempfile import TemporaryFile


from .models import Supplier, InvoiceItem


def index(request):
    supplier_list = Supplier.objects.order_by('supplier_name')
    context = {
        'supplier_list': supplier_list
    }
    return render(request, 'invoiceparser/index.html', context)


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
        description = request.POST['description']
        price = request.POST['price']
        ship_date = request.POST['ship_date']

        new_invoice_item = InvoiceItem(
            supplier=supplier, description=description, price=price, ship_date=ship_date)
        new_invoice_item.save()
    except:
        context = {
            'supplier': supplier,
            'suppliers': Supplier.objects.order_by('supplier_name'),
            'error_message': "You must fill out all fields"
        }
        return render(request, 'invoiceparser/detail.html', context)

    return HttpResponseRedirect(reverse('invoiceparser:detail', args=(supplier_id,)))


def upload_file(request):
    if request.method == 'POST':
        invoice_file = request.FILES['invoice']
        if request.FILES['invoice']:
            invoice_text = _extract_text(invoice_file)

    supplier_list = Supplier.objects.order_by('supplier_name')
    context = {
        'supplier_list': supplier_list,
        'extracted_text': invoice_text
    }
    return render(request, 'invoiceparser/index.html', context)


def _extract_text(invoice_file):
    # Open a PDF file.
    # path = '/Users/michaelberman/Documents/unread_invoice.pdf'
    print(invoice_file.name)
    new_file = None

    with TemporaryFile() as f:
        f.write(invoice_file.read())

        ocrmypdf.ocr(invoice_file, invoice_file.name, deskew=True)
        with pdfplumber.load(invoice_file) as pdf:
            page = pdf.pages[0]
            return page.extract_text()
