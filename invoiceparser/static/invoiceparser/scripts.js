$('#invoiceFileInput').on('change', function () {
    //get the file name
    var fileName = $(this).val();
    //replace the "Choose a file" label
    console.log($(this))
    $(this).next('.custom-file-label').html(fileName);
})