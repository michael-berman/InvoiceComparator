import os
import re
import ocrmypdf
import pdfplumber

from .service_delta import parse_delta_invoice
from .service_johnstone import parse_johnstone_invoice
from .service_carrier import parse_carrier_invoice
from .service_capco import parse_capco_invoice
from .service_ferguson import parse_ferguson_invoice

from .models import Supplier


def save_line_items(invoice_file):
    invoice_text = convert_with_ocr(invoice_file)
    if os.path.exists(invoice_file.name):
        os.remove(invoice_file.name)

    # Regular expressions
    delta_re = re.compile(r'(?i)DELTA')
    johnstone_re = re.compile(r'(?i)(JOHNSTONE)')
    carrier_re = re.compile(r'(?i)(Distributor Corporation of New England)')
    capco_re = re.compile(r'(?i)(capco)')
    ferguson_re = re.compile(r'(?i)(ferguson)')

    meta_data = {}
    lines = invoice_text.split("\n")
    for i in range(len(lines)):
        line = lines[i]
        supplier = ""

        if delta_re.match(line):
            meta_data = parse_delta_invoice(invoice_text)
            supplier = "delta"

        if johnstone_re.match(line):
            meta_data = parse_johnstone_invoice(invoice_text)
            supplier = "johnstone"

        if carrier_re.match(line):
            meta_data = parse_carrier_invoice(invoice_text)
            supplier = "carrier"

        if capco_re.match(line):
            meta_data = parse_capco_invoice(invoice_text)
            supplier = "capco"

        if ferguson_re.match(line):
            meta_data = parse_ferguson_invoice(invoice_text)
            supplier = "ferguson"

        if supplier:
            meta_data["supplier_id"] = Supplier.objects.filter(
                supplier_name__icontains=supplier)[0].id
            # create item and price keys
            for i in range(len(meta_data['line_items'])):
                item, price = meta_data['line_items'][i]
                item_key = "item" + str(i + 1)
                price_key = "price" + str(i + 1)
                meta_data['line_items'][i] = (
                    item_key, item.strip(), price_key, price.strip())
            break

    return meta_data


def convert_with_ocr(invoice_file):

    try:
        ocrmypdf.ocr(invoice_file.file, invoice_file.name,
                     deskew=True, force_ocr=True)
        temp_file = open(invoice_file.name, "r")

        with pdfplumber.load(temp_file.buffer) as pdf:
            page = pdf.pages[0]
            return page.extract_text()
    except Exception:
        with pdfplumber.load(invoice_file.file) as pdf:
            page = pdf.pages[0]
            return page.extract_text()
