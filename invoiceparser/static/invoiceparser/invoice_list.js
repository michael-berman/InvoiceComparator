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