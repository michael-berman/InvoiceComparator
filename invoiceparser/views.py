from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import Supplier, InvoiceItem

# Create your views here.


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
