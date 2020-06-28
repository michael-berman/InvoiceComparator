from django.contrib import admin

# Register your models here.

from .models import Supplier, InvoiceItem


class SupplierAdmin(admin.ModelAdmin):
    fields = ['supplier_name', 'supplier_location']
    list_display = ('supplier_name', 'supplier_location')
    search_fields = ['supplier_name']


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
    list_display = ('description', 'supplier', 'price', 'ship_date')
    list_filter = ['ship_date', 'price', 'supplier']
    search_fields = ['description']


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(InvoiceItem, InvoiceItemAdmin)
