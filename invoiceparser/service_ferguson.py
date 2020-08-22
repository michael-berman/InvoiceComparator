import re


def parse_ferguson_invoice(invoice_text):
    # Regular expressions for parsing
    date_re = re.compile(r'(\d{2}\/\d{2}\/\d{2})')
    invoice_number_re = re.compile(r'\d{7}')
    description_re = re.compile(r'(?i)(description)')
    each_re = re.compile(r'(?i)(ea)')
    price_re = re.compile(r'(?i)(\d{0,4}\.\d{3})')
    first_half_line_item_re = re.compile(r'(?i)(.+?(?=\d{1,3}\.\d{1,3}))')
    second_half_line_item_re = re.compile(r'\| (.*)')
    line_item_re = re.compile(r'((?:(?!(\d+  \d{1,4}\.\d{3})).)*)')
    final_line_re = re.compile(r'(?i)(sub-total)')

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

            # OCR is reading S as $
            invoice_number = invoice_number.replace("$", "S")
            invoice_number_found = True

        if description_re.search(line):

            # start scanning for description lines
            current_item = ""
            current_price = ""
            for j in range(i + 1, len(lines)):
                description_line = lines[j]

                if final_line_re.search(description_line):
                    if current_item:
                        line_items.append((current_item, current_price))
                    break

                if each_re.search(description_line):
                    if current_item:
                        line_items.append((current_item, current_price))

                    current_item = first_half_line_item_re.search(
                        description_line).group(0)
                    try:
                        current_item = second_half_line_item_re.search(
                            current_item).group(1)
                    except Exception:
                        print("Error has occured")

                    if price_re.search(description_line):
                        current_price = price_re.search(
                            description_line).group(0)
                    # else:
                        # current_item =
                elif description_line.strip() != "":
                    current_item += " " + description_line
                    # meta_data.append("Description: " + current_item)
                    # line_items.append((current_item, current_price))

            break

    meta_data["invoice_date"] = invoice_date
    meta_data["invoice_number"] = invoice_number
    meta_data["line_items"] = line_items
    return meta_data
