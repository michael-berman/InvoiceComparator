$(".supplier-select-item").click(function () {
    $("#dropdownMenuButton4:first-child").text($(this).text());
    $("#dropdownMenuButton4:first-child").val($(this).text());
    $("#dropdownMenuButton4:first-child").data('id', $(this).data("id"));
});

$('#add-line-button').click(function () {
    const container = $("#line-item-container");
    const countEl = container.children().length;
    container.append(`
    <div class="input-group mb-3">
        <div class="input-group-prepend">
            <span class="input-group-text">Invoice Description and Price</span>
        </div>
        <textarea type="text" class="form-control" name="item${countEl + 1}"></textarea>
        <textarea type="text" class="form-control col-sm-3" name="price${countEl + 1}"></textarea>
        <div class="input-group-append">
            <button class="btn btn-danger delete-line-button" type="button">Delete</button>
        </div>
    </div>`)
})

$(document).on('click', '.delete-line-button', function () {
    // $($('.delete-line-button')[0]).parent().parent().remove()
    $(this).parent().parent().remove();
})

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$('.save-line-button').click(function () {
    const supplier_id = $("#dropdownMenuButton4:first-child").data('id');

    if (!supplier_id) {
        alert("Please select Supplier.")
    }

    let data = {};
    data["items-only"] = true;
    [...Array(11).keys()].forEach(num => {
        if ($(`textarea[name="item${num}"]`)[0] !== undefined) {
            data["item" + num] = $(`textarea[name="item${num}"]`).val();
            data["price" + num] = $(`textarea[name="price${num}"]`).val();
        }
    })
    $.ajax({
        type: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        url: `/${supplier_id}/create/`,
        data,
        success: function (res) {
            console.log(res)
            //empty out the line item container 
            const container = $("#line-item-container");
            container.empty()

            // reset supplier select
            $("#dropdownMenuButton4:first-child").text($(this).text());
            $("#dropdownMenuButton4:first-child").val($(this).text());
            $("#dropdownMenuButton4:first-child").data('id', $(this).data("id"));
        }
    });
})