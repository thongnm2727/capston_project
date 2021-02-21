$(document).ready(function () {
    var d = new Date();
    var month = d.getMonth() + 1;
    var year = d.getFullYear();

    $("#month").val(month);
    $("#year").val(year);

});