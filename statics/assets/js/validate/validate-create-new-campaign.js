function validateForm() {
    var campaignName = document.forms["myForm"]["cp_name"].value();
    var description = document.forms["myForm"]["description"].value();
    var budget = document.forms["myForm"]["budget"].value();
    var destination_url = document.forms["myForm"]["destination_url"].value();
    if (isNaN(budget)) {
        document.getElementById("validationCustom03").innerHTML = budget.validationMessage;
    }
}