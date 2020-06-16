from django.db import models

# Create your models here.


class Supplier(models.Model):
    supplier_name = models.CharField(max_length=300)
    supplier_location = models.CharField(max_length=1000)


class InvoiceItem(models.Model):
    supplier_id = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    price = models.DecimalField()
    ship_date = models.DateTimeField()
