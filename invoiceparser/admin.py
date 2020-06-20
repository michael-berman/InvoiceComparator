from django.contrib import admin

# Register your models here.

from .models import Supplier, InvoiceItem

admin.site.register(Supplier)
admin.site.register(InvoiceItem)
