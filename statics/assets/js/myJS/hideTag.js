// function showTable() {
//   document.getElementById('hiddenTables').style.display = "block";
// }
// function hideTable(){
// document.getElementById('hiddenTables').style.display = "none";
// }
function showTable() {
    var x = document.getElementById("hiddenTables");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}