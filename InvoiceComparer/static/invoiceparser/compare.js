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
    $("#dropdownMenuButton1:first-child").data('id', $(this).data("id"));
    $.ajax({
        url: "/ajax/invoiceitems/" + $(this).data("id"),
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

$('#searchText1').on('input', function () {
    const supplier_id = $("#dropdownMenuButton1:first-child").data('id');
    $.ajax({
        url: "/ajax/invoiceitems/" + supplier_id + "/" + $(this).val(),
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
    $("#dropdownMenuButton2:first-child").data('id', $(this).data("id"));
    $.ajax({
        url: "/ajax/invoiceitems/" + $(this).data("id"),
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

$('#searchText2').on('input', function () {
    const supplier_id = $("#dropdownMenuButton2:first-child").data('id');
    $.ajax({
        url: "/ajax/invoiceitems/" + supplier_id + "/" + $(this).val(),
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