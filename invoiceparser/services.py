import os
import re
from datetime import datetime
from django.utils.formats import get_format
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image
import pytesseract
import ghostscript
import locale
import boto3
from decouple import config
import cv2
import numpy

from .models import Supplier

from .service_delta import parse_delta_invoice
from .service_johnstone import parse_johnstone_invoice
from .service_carrier import parse_carrier_invoice
from .service_capco import parse_capco_invoice
from .service_ferguson import parse_ferguson_invoice


def save_line_items(invoice_file):

    if not os.path.exists('temp/'):
        os.makedirs('temp/')

    # save file locally first for aws
    folder = 'temp/'
    fs = FileSystemStorage(location=folder)
    filename = fs.save(invoice_file.name, invoice_file)
    temp_pdf_path = 'temp/' + invoice_file.name

    # Save to AWS
    upload_to_AWS(temp_pdf_path, invoice_file.name)

    # convert pdf to img
    temp_jpg_path = temp_pdf_path.replace("pdf", "jpg")
    pdf2jpeg(temp_pdf_path, temp_jpg_path)

    '''
        This section is to preprocess the image for better extraction of text
    '''
    img = cv2.imread(temp_jpg_path)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    # kernel = numpy.ones((1, 1), numpy.uint8)
    # img = cv2.dilate(img, kernel, iterations=1)
    # img = cv2.erode(img, kernel, iterations=1)

    # Apply blur to smooth out the edges
    # img = cv2.GaussianBlur(img, (5, 5), 0)

    img = cv2.bilateralFilter(img, 9, 75, 75)

    # Recognize text with tesseract for python
    invoice_text = pytesseract.image_to_string(img)
    # extract text from img
    # invoice_text = str(
    #     ((pytesseract.image_to_string(Image.open(save_path)))))

    # delete pdf and img after extraction is complete
    if os.path.isfile(temp_pdf_path):
        os.remove(temp_pdf_path)

    if os.path.isfile(temp_jpg_path):
        os.remove(temp_jpg_path)

    # Regular expressions
    delta_re = re.compile(r'(?i)DELTA')
    johnstone_re = re.compile(r'(?i)(JOHNSTONE)')
    carrier_re = re.compile(r'(?i)(New England)')
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
