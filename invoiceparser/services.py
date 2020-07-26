import os
import io
import re
import ocrmypdf
import pdfplumber

from .models import Supplier, InvoiceItem


def save_line_items(invoice_file):
    invoice_text = _extract_text(invoice_file)

    meta_data = []

    ship_date = ""
    invoice_number = ""

    # Regular expressions
    delta_re = re.compile(r'^DELTA')
    date_re = re.compile(r'([0-9][0-9]/[0-9][0-9]/[0-9][0-9])')
    description_re = re.compile(r'^ DESCRIPTION')
    each_re = re.compile(r'\dEA')
    line_item_re = re.compile(r'(?:(?!\dEA).)*')

    invoice_date_found = False
    lines = invoice_text.split("\n")
    for i in range(len(lines)):
        line = lines[i]

        if delta_re.match(line):
            meta_data.append("Company: Delta")

        if date_re.match(line) and invoice_date_found is False:
            date, invoice_number = line.split("|")

            # OCR is reading S as $
            invoice_number = invoice_number.replace("$", "S")
            meta_data.append("Invoice Date: " + date)
            meta_data.append("Invoice Number: " + invoice_number)
            invoice_date_found = True

        if description_re.match(line):

            # start scanning for description lines
            current_item = ""
            for j in range(i + 1, len(lines)):
                description_line = lines[j]

                if description_line.strip() == "":
                    break

                if each_re.search(description_line):
                    current_item = re.search(
                        line_item_re, description_line).group(0).strip()
                else:
                    current_item += " " + description_line
                    meta_data.append("Description: " + current_item)

            break

    # os.remove(invoice_file.name)
    return meta_data


def _extract_text(invoice_file):
    # Open a PDF file.
    # path = '/Users/michaelberman/Documents/unread_invoice.pdf'
    # with TemporaryFile() as f:
    # f.write(invoice_file.read())

    # ocrmypdf.ocr(invoice_file.file, invoice_file.name, deskew=True)
    temp_file = open(invoice_file.name, "r")

    with pdfplumber.load(temp_file.buffer) as pdf:
        page = pdf.pages[0]
        return page.extract_text()
