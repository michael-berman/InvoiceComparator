# Generated by Django 3.0.7 on 2020-08-05 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoiceparser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='invoice_file',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]