function vidPlay() {
    $("#video1").get(0).play();
}

function vidPause() {
    $("#video1").get(0).pause();
}
$(document).ready(function () {
    $("#textToggler").click(function () {
        $(".toggleText").toggle();
    });
});
var id_ads;

function toggleImage(id_ads) {
    $(".hiddenclickimg").toggle();
}