from django.shortcuts import render
from django.http import HttpResponse

from .models import Supplier

# Create your views here.


def upload(request):
    return HttpResponse("You're looking at the upload request")


def detail(request):
    return HttpResponse("You're looking at the detail request")


def get_supplier(request, document_id):
    supplier_list = Supplier.objects.order_by('supplier_name')
    output = ', '.join([s.supplier_name for s in supplier_list])
    return HttpResponse(output)
