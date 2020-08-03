from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse


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
        invoice = Invoice.objects.get(
            invoice_number=request.POST['invoice_number'])

        if invoice:
            raise KeyError("This Invoice has already been uploaded.")
        invoice = Invoice(supplier=supplier,
                          invoice_number=request.POST['invoice_number'],
                          invoice_date=parse_date(request.POST['invoice_date']))
        invoice.save()

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

    return HttpResponseRedirect(reverse('invoiceparser:detail', args=(supplier_id,)))


def upload_file(request):
    if request.method == 'POST':
        invoice_file = request.FILES['invoice']
        if request.FILES['invoice']:
            meta_data = save_line_items(invoice_file)

    supplier_list = Supplier.objects.order_by('id')
    context = {
        'supplier_list': supplier_list,
        'extracted_text': meta_data,
        'file_name': invoice_file.name
    }
    return render(request, 'invoiceparser/index.html', context)
