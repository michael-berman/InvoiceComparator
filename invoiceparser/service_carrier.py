import re


def parse_carrier_invoice(invoice_text):
    # Regular expressions for parsing
    date_re = re.compile(r'([0-9][0-9]/[0-9][0-9]/[0-9][0-9])')
    invoice_number_re = re.compile(
        r'([0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9])')
    description_re = re.compile(r'^ DESCRIPTION')
    each_re = re.compile(r'(?i)(each)')
    price_re = re.compile(r'(?i)(\d+\.[0-9][0-9])')
    first_half_line_item_re = re.compile(r'.+?(?= \d+ )')
    second_half_line_item_re = re.compile(r'\d+ (.*)')
    # line_item_re = re.compile(r'(\b\d \s+\K\S+)')
    final_line_re = re.compile(r'(?i)(Lines)')

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

        if each_re.search(line):

            # start scanning for description lines
            current_item = ""
            current_price = ""
            for j in range(i, len(lines)):
                description_line = lines[j]

                # meta_data.append(description_line)

                if final_line_re.search(description_line):
                    # in case there's a last item that isn't added
                    if current_item:
                        line_items.append((current_item, current_price))
                    break

                if each_re.search(description_line):
                    if current_item:
                        line_items.append((current_item, current_price))

                    current_item = first_half_line_item_re.search(
                        description_line).group(0)
                    current_item = second_half_line_item_re.search(
                        current_item).group(1)

                    if price_re.search(description_line):
                        current_price = re.search(
                            price_re, description_line).group(0)
                elif description_line.strip() != "":
                    current_item += " " + description_line
                    # meta_data.append("Description: " + current_item)
            break

    meta_data["invoice_date"] = invoice_date
    meta_data["invoice_number"] = invoice_number
    meta_data["line_items"] = line_items
    return meta_data
