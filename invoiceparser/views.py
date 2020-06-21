from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader

from .models import Supplier

# Create your views here.


def index(request):
    supplier_list = Supplier.objects.order_by('supplier_name')
    context = {
        'supplier_list': supplier_list
    }
    return render(request, 'invoiceparser/index.html', context)


def detail(request, supplier_id):
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
    except Supplier.DoesNotExist:
        raise Http404("Supplier does not exist")

    context = {
        'supplier': supplier
    }
    return render(request, 'invoiceparser/detail.html', context)
