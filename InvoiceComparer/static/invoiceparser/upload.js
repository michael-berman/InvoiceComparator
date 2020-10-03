$('.delete-button').click(function () {
    $(this).parent().parent().remove();
})

$('#parsed-add-line-button').click(function () {
    var numItems = $('.parsed-item').length
    const container = $("#new-line-items");
    const countEl = container.children().length;
    container.append(`
    <div class="input-group mb-3">
        <div class="input-group-prepend">
            <span class="input-group-text">Invoice Description and Price</span>
        </div>
        <textarea type="text" class="form-control" name="item${numItems + countEl + 1}"></textarea>
        <textarea type="text" class="form-control col-sm-3" name="price${numItems + countEl + 1}"></textarea>
        <div class="input-group-append">
            <button class="btn btn-danger delete-line-button" type="button">Delete</button>
        </div>
    </div>`)
})