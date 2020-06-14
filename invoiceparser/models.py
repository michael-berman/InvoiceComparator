from django.db import models

# Create your models here.


class InvoiceItem(models.Model):
    item_id = models.Index()
    description_text = models.CharField(max_length=1000)
    price = models.DecimalField()
    ship_date = models.DateTimeField()


class Supplier(models.Model):
    supplier_id = models.Index()
    supplier_name = models.CharField(max_length=200)
