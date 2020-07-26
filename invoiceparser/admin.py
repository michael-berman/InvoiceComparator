from django.contrib import admin

# Register your models here.

from .models import Supplier, InvoiceItem


class SupplierAdmin(admin.ModelAdmin):
    fields = ['supplier_name', 'supplier_location']
    list_display = ('supplier_name', 'supplier_location')
    search_fields = ['supplier_name']


class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Supplier', {
            "fields": (
                ['supplier']
            ),
        }),
        ('Invoice Information', {
            'fields': (
                ['invoice_number', 'invoice_date']
            )})
    ]
    list_display = ('invoice_number', 'invoice_date')
    list_filter = ['invoice_number', 'invoice_date']
    search_fields = ['invoice_number']


class InvoiceItemAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Invoice', {
            "fields": (
                ['invoice_number']
            ),
        }),
        ('Invoice Item Information', {
            'fields': (
                ['description', 'price']
            )})
    ]
    list_display = ('description', 'invoice', 'price')
    list_filter = ['price', 'invoice']
    search_fields = ['description']


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(InvoiceItem, InvoiceItemAdmin)
