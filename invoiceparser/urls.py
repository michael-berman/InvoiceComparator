from django.urls import path

from . import views

app_name = 'invoiceparser'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:supplier_id>/', views.detail, name='detail'),
    path('<int:supplier_id>/create/', views.create, name='create'),
    path('upload', views.upload_file, name="upload")
]
