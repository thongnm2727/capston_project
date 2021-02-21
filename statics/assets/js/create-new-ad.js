function setSize() {
    var e = document.getElementById("ddlViewBy");
    var strUser = e.options[e.selectedIndex].value;
    var size = strUser.split("x");
    var widthDiv = size[0];
    var heightDiv = size[1];
    document.getElementById("prewImage").style.backgroundColor = "gray";
    document.getElementById("prewImage").style.width = widthDiv + "px";
    document.getElementById("prewImage").style.height = heightDiv + "px";
}

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
    }
}

$("#imgInp").change(function () {
    readURL(this);
});

$('#alert-success-1').on('click', function () {
    v = document.getElementById("imgInp");
    c = document.getElementById("ddlViewBy");

    if (v.value == null && c.value == null) return false;
    if (v.value == "" || c.value == "") {
        swal({
            type: 'error',
            title: 'Create Failed!',
            text: 'Please select an Ad size and upload a banner image!',
            confirmButtonText: 'Got it!',
            buttonsStyling: false,
            confirmButtonClass: 'btn btn-lg btn-danger'
        });
        return false;
    }
    // swal("Awesome!", "You create ads success");
});

