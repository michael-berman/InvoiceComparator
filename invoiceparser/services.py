import os
import io
import re
import ocrmypdf
import pdfplumber

from .service_delta import parse_delta_invoice


def save_line_items(invoice_file):
    invoice_text = convert_with_ocr(invoice_file)
    os.remove(invoice_file.name)

    # Regular expressions
    delta_re = re.compile(r'^DELTA')

    lines = invoice_text.split("\n")
    for i in range(len(lines)):
        line = lines[i]

        if delta_re.match(line):
            return parse_delta_invoice(invoice_text)


def convert_with_ocr(invoice_file):
    ocrmypdf.ocr(invoice_file.file, invoice_file.name, deskew=True)
    temp_file = open(invoice_file.name, "r")

    with pdfplumber.load(temp_file.buffer) as pdf:
        page = pdf.pages[0]
        return page.extract_text()
