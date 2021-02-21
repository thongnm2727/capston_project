function validate() {
    var campaignName = document.getElementById("validationCustom01");
    var description = document.getElementById("validationCustom02");
    var budget = document.getElementById("validationCustom03");
    var destinationUrl = document.getElementById("validationCustom04");

    if (campaignName == null) {
        document.getElementById("mess1").innerHTML = "Must fill in here";
    }
    if (description == null) {
        document.getElementById("mess2").innerHTML = "Must fill in here";
    }
    if (destinationUrl == null) {
        document.getElementById("mess4").innerHTML = "Must fill in here";
    }
    if (budget == null || isNaN(budget)) {
        document.getElementById("mess3").innerHTML = "Must fill in number here";
    }
}

