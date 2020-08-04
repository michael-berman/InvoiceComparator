from django.urls import path

from . import views

app_name = 'invoiceparser'
urlpatterns = [
    path('', views.index, name='index'),
    path('compare', views.compare, name='compare'),
    path('<int:supplier_id>/', views.load_invoice_items, name='load_invoice_items'),
    path('<int:supplier_id>/create/', views.create, name='create'),
    path('upload', views.upload_file, name="upload"),
]
