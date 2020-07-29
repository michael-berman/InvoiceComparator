import re


def parse_delta_invoice(invoice_text):
    # Regular expressions for parsing
    date_re = re.compile(r'([0-9][0-9]/[0-9][0-9]/[0-9][0-9])')
    description_re = re.compile(r'^ DESCRIPTION')
    each_re = re.compile(r'\dEA')
    price_re = re.compile(r'(?i)([0-9]{1,3}\.[0-9][0-9][0-9]ea)')
    line_item_re = re.compile(r'(?:(?!\dEA).)*')
    final_line_re = re.compile(r'(?i)(Thank)')

    meta_data = []
    line_items = []
    ship_date = ""
    invoice_number = ""

    invoice_date_found = False
    lines = invoice_text.split("\n")
    for i in range(len(lines)):
        line = lines[i]

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
            current_price = ""
            for j in range(i + 1, len(lines)):
                description_line = lines[j]

                if final_line_re.search(description_line):
                    break

                if each_re.search(description_line):
                    current_item = re.search(
                        line_item_re, description_line).group(0).strip()

                    if price_re.search(description_line):
                        current_price = re.search(
                            price_re, description_line).group(0)
                elif description_line.strip() != "":
                    current_item += " " + description_line
                    # meta_data.append("Description: " + current_item)
                    line_items.append((current_item, current_price))

            break

    for line_item in line_items:
        item, price = line_item
        meta_data.append(item + " : " + price)
    return meta_data