from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import io
import re
import ocrmypdf
from shutil import copyfile
import pdfplumber

from .service_delta import parse_delta_invoice
from .service_johnstone import parse_johnstone_invoice


def save_line_items(invoice_file):
    invoice_text = convert_with_ocr(invoice_file)
    if os.path.exists(invoice_file.name):
        os.remove(invoice_file.name)

    # Regular expressions
    delta_re = re.compile(r'(?i)^DELTA')
    johnstone_re = re.compile(r'(?i)(JOHNSTONE)')

    lines = invoice_text.split("\n")
    for i in range(len(lines)):
        line = lines[i]

        if delta_re.match(line):
            return parse_delta_invoice(invoice_text)

        if johnstone_re.match(line):
            return parse_johnstone_invoice(invoice_text)


def convert_with_ocr(invoice_file):

    try:
        ocrmypdf.ocr(invoice_file.file, invoice_file.name, deskew=True)
        temp_file = open(invoice_file.name, "r")

        with pdfplumber.load(temp_file.buffer) as pdf:
            page = pdf.pages[0]
            return page.extract_text()
    except Exception:
        with pdfplumber.load(invoice_file.file) as pdf:
            page = pdf.pages[0]
            return page.extract_text()
