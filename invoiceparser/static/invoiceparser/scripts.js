$('#invoiceFileInput').on('change', function () {
    //get the file name
    var fileName = $(this).val();
    //replace the "Choose a file" label
    console.log($(this))
    $(this).next('.custom-file-label').html(fileName);
})


// ajax calls for get invoice items list
$(".first-suppler-select-invoice-item").click(function () {
    $("#dropdownMenuButton1:first-child").text($(this).text());
    $("#dropdownMenuButton1:first-child").val($(this).text());
    $.ajax({
        url: "/invoiceparser/ajax/invoiceitems/" + $(this).data("id"),
        success: function (data) {
            console.log(data)
            const invoice_items = data.invoice_items;
            var table = $('#firstTable tbody');
            $('#firstTable tbody').empty();
            for (let i = 0; i < invoice_items.length; i++)
                table.append('<tr><td>' + invoice_items[i].description + '</td><td>' + invoice_items[i].price + '</td></tr>')
        }
    });

});

$(".second-suppler-select-invoice-item").click(function () {
    $("#dropdownMenuButton2:first-child").text($(this).text());
    $("#dropdownMenuButton2:first-child").val($(this).text());
    $.ajax({
        url: "/invoiceparser/ajax/invoiceitems/" + $(this).data("id"),
        success: function (data) {
            console.log(data)
            const invoice_items = data.invoice_items;
            var table = $('#secondTable tbody');
            $('#secondTable tbody').empty();
            for (let i = 0; i < invoice_items.length; i++)
                table.append('<tr><td>' + invoice_items[i].description + '</td><td>' + invoice_items[i].price + '</td></tr>')
        }
    });

});

$(".first-suppler-select-invoice").click(function () {
    $("#dropdownMenuButton3:first-child").text($(this).text());
    $("#dropdownMenuButton3:first-child").val($(this).text());
    $.ajax({
        url: "/invoiceparser/ajax/invoices/" + $(this).data("id"),
        success: function (data) {
            console.log(data)
            const invoices = data.invoices;
            var table = $('#invoiceTable tbody');
            $('#invoiceTable tbody').empty();
            for (let i = 0; i < invoices.length; i++)
                table.append('<tr><td>' + invoices[i].invoice_date +
                    '</td><td>' + invoices[i].invoice_number +
                    '</td><<td><a href="' + invoices[i].invoice_file + '">Download</a></td></tr>')
        },
        error: function (err) {
            console.log(err)
        }
    });

});