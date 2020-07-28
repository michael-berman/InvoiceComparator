import re


def parse_johnstone_invoice(invoice_text):
    # Regular expressions for parsing
    date_re = re.compile(r'([0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9])')
    description_re = re.compile(r'(?i)(Description)')
    each_re = re.compile(r'(?i)(^.+ea  \d+ea(.*))')
    first_half_line_item_re = re.compile(r'(?i)()')
    # first_half_2_line_item_re = re.compile(r'(?i)(\d+ea  \d+eaj](.*))')
    second_half_line_item_re = re.compile(r'(?i)(?:(?! \d+.\d+\/ea).)*')
    price_raw_re = re.compile(r'(?i)\d+.\d+\/ea')
    price_re_without_ea = re.compile(r'(?i)(?:(?!\/ea).)*')
    subtotal_re = re.compile(r'(?i)(Subtotal)')

    meta_data = []
    line_items = []
    ship_date = ""
    invoice_number = ""

    invoice_date_found = False
    lines = invoice_text.split("\n")
    for i in range(len(lines)):
        line = lines[i]
        if date_re.match(line) and invoice_date_found is False:
            date, invoice_number = line.split(" ")

            # OCR is reading S as $
            meta_data.append("Invoice Date: " + date)
            meta_data.append("Invoice Number: " + invoice_number)
            invoice_date_found = True

        if description_re.search(line):

            # start scanning for description lines
            current_item = ""
            current_price = ""
            for j in range(i + 1, len(lines)):
                description_line = lines[j]

                if subtotal_re.search(description_line):
                    line_items.append((current_item, current_price))
                    break

                if each_re.search(description_line):
                    # for one liners
                    # if current_item and current_price:
                    #     line_items.append((current_item, current_price))

                    # check first with eaj
                    if first_half_line_item_re.search(description_line):
                        current_item = first_half_line_item_re.search(
                            description_line).group(2)
                        current_item = second_half_line_item_re.search(
                            current_item).group(0).strip()
                    elif first_half_2_line_item_re.search(description_line):
                        current_item = first_half_line_item_re.search(
                            description_line).group(2)
                        current_item = second_half_line_item_re.search(
                            current_item).group(0).strip()

                    if price_raw_re.search(description_line):
                        current_price = re.search(
                            price_raw_re, description_line).group(0)
                        current_price = re.search(
                            price_re_without_ea, current_price).group(0)
                elif description_line.strip() != "":
                    current_item += " " + description_line
                    # meta_data.append("Description: " + current_item)
                    line_items.append((current_item, current_price))

            break

    for line_item in line_items:
        item, price = line_item
        meta_data.append(item + " : " + price)
    return meta_data
