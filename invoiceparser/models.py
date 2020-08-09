from django.db import models

# Create your models here.


class Supplier(models.Model):
    supplier_name = models.CharField(max_length=300)
    supplier_location = models.CharField(max_length=1000)

    def __str__(self):
        return self.supplier_name


class Invoice(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20)
    invoice_date = models.DateField()
    invoice_file = models.FileField(blank=True)

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=1000)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.description
