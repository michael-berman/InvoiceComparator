import re


def parse_johnstone_invoice(invoice_text):
    # Regular expressions for parsing
    date_re = re.compile(r'([0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9])')
    invoice_number_re = re.compile(r'(\d+\-.+)')
    description_re = re.compile(r'(?i)(Description)')
    each_re = re.compile(r'(?i)(ea)')
    first_half_line_item_re = re.compile(r'(?i)(.+ea  \d+ea(.*))')
    first_half_2_line_item_re = re.compile(r'(?i)(\d+ea  \d+eaj](.*))')
    first_half_3_line_item_re = re.compile(r'(?i)^(.*?)(\d+.\d+\/ea)')
    second_half_line_item_re = re.compile(r'(?i)(?:(?! \d+.\d+\/ea).)*')
    second_half_2_line_item_re = re.compile(r'(?i)\|(.*)')
    price_raw_re = re.compile(r'(?i)\d+.\d+\/ea')
    price_re_without_ea = re.compile(r'(?i)(?:(?!\/ea).)*')
    subtotal_re = re.compile(r'(?i)(Subtotal)')

    meta_data = {}
    line_items = []
    invoice_date = ""
    invoice_number = ""

    invoice_date_found = False
    invoice_number_found = False
    lines = invoice_text.split("\n")
    for i in range(len(lines)):
        line = lines[i]
        if date_re.search(line) and invoice_date_found is False:
            invoice_date = date_re.search(line).group(0)
            invoice_date_found = True

        if invoice_number_re.search(line) and invoice_number_found is False:
            invoice_number = invoice_number_re.search(line).group(0)
            invoice_number_found = True

        if description_re.search(line):

            # start scanning for description lines
            current_item = ""
            current_price = ""
            for j in range(i + 1, len(lines)):
                description_line = lines[j]

                if subtotal_re.search(description_line):
                    # johnstone has a line before the description from OCR
                    line_items.append((current_item[1:], current_price))
                    break

                if each_re.search(description_line):
                    # for one liners
                    if current_item and current_price:
                        line_items.append((current_item[1:], current_price))

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
                    elif first_half_3_line_item_re.search(description_line):
                        current_item = first_half_3_line_item_re.search(
                            description_line).group(1)
                        current_item = second_half_2_line_item_re.search(
                            current_item).group(1).strip()

                    if price_raw_re.search(description_line):
                        current_price = re.search(
                            price_raw_re, description_line).group(0)
                        current_price = re.search(
                            price_re_without_ea, current_price).group(0)

                    # line_items.append((description_line, current_price))
                elif description_line.strip() != "":
                    current_item += " " + description_line
                # meta_data.append("Description: " + current_item)

            break

    meta_data["invoice_date"] = invoice_date
    meta_data["invoice_number"] = invoice_number
    meta_data["line_items"] = line_items
    return meta_data
