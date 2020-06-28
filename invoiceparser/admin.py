from django.contrib import admin

# Register your models here.

from .models import Supplier, InvoiceItem


class SupplierAdmin(admin.ModelAdmin):
    fields = ['supplier_name', 'supplier_location']


class InvoiceItemAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Supplier', {
            "fields": (
                ['supplier']
            ),
        }),
        ('Invoice Item Information', {
            'fields': (
                ['description', 'price', 'ship_date']
            )})
    ]


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(InvoiceItem, InvoiceItemAdmin)
