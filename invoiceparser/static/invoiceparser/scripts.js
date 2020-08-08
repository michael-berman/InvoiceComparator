$('#invoiceFileInput').on('change', function () {
    //get the file name
    var fileName = $(this).val();
    //replace the "Choose a file" label
    console.log($(this))
    $(this).next('.custom-file-label').html(fileName);
})


// ajax calls for get invoice items list
$(".first-suppler-select-item").click(function () {
    $("#dropdownMenuButton1:first-child").text($(this).text());
    $("#dropdownMenuButton1:first-child").val($(this).text());
    $.ajax({
        url: "/invoiceparser/ajax/" + $(this).data("id"),
        success: function (data) {
            console.log(data)
            const invoice_items = data.invoice_items;
            var table = $('#firstTable');
            $('#firstTable').empty();
            for (let i = 0; i < invoice_items.length; i++)
                table.append('<tr><td>' + invoice_items[i].description + '</td><td>' + invoice_items[i].price + '</td></tr>')
        }
    });

});

$(".second-suppler-select-item").click(function () {
    $("#dropdownMenuButton2:first-child").text($(this).text());
    $("#dropdownMenuButton2:first-child").val($(this).text());
    $.ajax({
        url: "/invoiceparser/ajax/" + $(this).data("id"),
        success: function (data) {
            console.log(data)
            const invoice_items = data.invoice_items;
            var table = $('#secondTable');
            $('#secondTable').empty();
            for (let i = 0; i < invoice_items.length; i++)
                table.append('<tr><td>' + invoice_items[i].description + '</td><td>' + invoice_items[i].price + '</td></tr>')
        }
    });

});