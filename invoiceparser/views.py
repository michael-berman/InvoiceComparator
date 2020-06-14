from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the invoice parser index.")


def get(request):
    return HttpResponse("this is get")
