import os
import re
from datetime import datetime
from django.utils.formats import get_format
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image
import pandas as pd
import pytesseract
import ghostscript
import locale
import boto3
from decouple import config
import cv2
import numpy as np

import ocrmypdf
import pdfplumber
from subprocess import Popen, PIPE, check_output

from .models import Supplier

from .service_delta import parse_delta_invoice
from .service_johnstone import parse_johnstone_invoice
from .service_carrier import parse_carrier_invoice
from .service_capco import parse_capco_invoice
from .service_ferguson import parse_ferguson_invoice


def save_line_items(invoice_file):

    folder = settings.UPLOAD_PATH
    if not os.path.exists(folder):
        os.makedirs(folder)

    # save file locally first for aws
    folder = folder
    fs = FileSystemStorage(location=folder)
    filename = fs.save(invoice_file.name, invoice_file)
    temp_pdf_path = folder + filename

    print("-----------------------")
    print("FILE: ")
    print(fs)
    print("-----------------------")
    print("FileName:")
    print(filename)
    print("-----------------------")

    # Save to AWS
    upload_to_AWS(temp_pdf_path, invoice_file.name)

    print("-----------------------")
    print("File uploaded to AWS")
    print("-----------------------")

    invoice_text = ''
    try:
        ocrmypdf.ocr(temp_pdf_path, temp_pdf_path, force_ocr=True)
        print("-----------------------")
        print("File has been ocr'd")
        print("-----------------------")
        temp_file = open(temp_pdf_path, "r")
        print("-----------------------")
        print("File has been opened.")
        print("-----------------------")
        with pdfplumber.load(temp_file.buffer) as pdf:
            page = pdf.pages[0]
            invoice_text = page.extract_text()
        print("-----------------------")
        print("Text has been extracted.")
        print("-----------------------")
    except Exception as err:
        print("Add error catch from here. " + err)
        with pdfplumber.load(temp_pdf_path) as pdf:
            page = pdf.pages[0]
            invoice_text = page.extract_text()

    # process_args = ['ocrmypdf', temp_pdf_path, temp_pdf_path,
    #                 '--force-ocr']

    # process = Popen(process_args)
    # out = check_output(process_args)

    # delete pdf and img after extraction is complete
    if os.path.isfile(temp_pdf_path):
        os.remove(temp_pdf_path)

    print("-----------------------")
    print("File has been deleted.")
    print("-----------------------")

    # Regular expressions
    delta_re = re.compile(r'(?i)DELTA')
    johnstone_re = re.compile(r'(?i)(JOHNSTONE)')
    carrier_re = re.compile(r'(?i)(Distributor Corp.)')
    capco_re = re.compile(r'(?i)(capco)')
    ferguson_re = re.compile(r'(?i)(ferguson)')

    meta_data = {}
    lines = invoice_text.split("\n")
    for i in range(len(lines)):
        line = lines[i]
        supplier = ""

        if delta_re.search(line):
            meta_data = parse_delta_invoice(invoice_text)
            supplier = "delta"

        if johnstone_re.search(line):
            meta_data = parse_johnstone_invoice(invoice_text)
            supplier = "johnstone"

        if carrier_re.search(line):
            meta_data = parse_carrier_invoice(invoice_text)
            supplier = "carrier"

        if capco_re.search(line):
            meta_data = parse_capco_invoice(invoice_text)
            supplier = "capco"

        if ferguson_re.search(line):
            meta_data = parse_ferguson_invoice(invoice_text)
            supplier = "ferguson"

        if supplier:
            meta_data["supplier_id"] = Supplier.objects.filter(
                supplier_name__icontains=supplier)[0].id
            meta_data["invoice_date"] = meta_data["invoice_date"].strip()
            meta_data["invoice_number"] = meta_data["invoice_number"].strip()
            # create item and price keys
            for i in range(len(meta_data['line_items'])):
                item, price = meta_data['line_items'][i]
                item_key = "item" + str(i + 1)
                price_key = "price" + str(i + 1)
                meta_data['line_items'][i] = (
                    item_key, item.strip(), price_key, price.strip())
            break

    return meta_data


def parse_date(date_str):
    """Parse date from string by DATE_INPUT_FORMATS of current language"""
    for item in get_format('DATE_INPUT_FORMATS'):
        try:
            return datetime.strptime(date_str, item).date()
        except (ValueError, TypeError):
            continue

    return None


def upload_to_AWS(temp_pdf_path, invoice_file_name):
    s3 = boto3.resource('s3', aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
    s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).upload_file(
        temp_pdf_path, invoice_file_name,
        ExtraArgs={'ACL': 'public-read'})


def pdf2jpeg(pdf_input_path, jpeg_output_path):
    args = ["pef2jpeg",  # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=jpeg",
            "-r144",
            "-sOutputFile=" + jpeg_output_path,
            pdf_input_path]

    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    with ghostscript.Ghostscript(*args) as g:
        ghostscript.cleanup()


def preprocess_and_extract(temp_jpg_path):
    '''
        This section is to preprocess the image for better extraction of text
    '''

    img = cv2.imread(temp_jpg_path)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    #  Apply threshold to get image with only black and white
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Recognize text with tesseract for python
    return pytesseract.image_to_string(img, lang="eng")
