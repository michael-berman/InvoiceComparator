from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'invoiceparser'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name="upload"),
    path('compare', views.compare, name='compare'),
    path('invoice_list', views.invoice_list, name='invoice_list'),
    path('<int:supplier_id>/', views.detail, name='detail'),
    path('<int:supplier_id>/create/', views.create, name='create'),
    path('upload_file', views.upload_file, name="upload_file"),
    path('ajax/invoiceitems/<int:supplier_id>/',
         views.load_invoice_items, name="load_invoice_items"),
    path('ajax/invoiceitems/<int:supplier_id>/<str:search>',
         views.load_invoice_items, name="load_invoice_items"),
    path('ajax/invoices/<int:supplier_id>/',
         views.load_invoices, name="load_invoices"),
]
