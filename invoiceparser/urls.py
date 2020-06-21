from django.urls import path

from . import views

urlpatterns = [
    path('', views.upload, name='upload'),
    path('supplier', views.detail, name='detail'),
    path('<int:document_id>/', views.get_supplier, name='get_supplier')
]
