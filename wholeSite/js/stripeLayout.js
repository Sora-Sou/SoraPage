$(document).ready(function () {
    var length = $("#passage").children("section").length;
    if (length % 2 == 0) {
        for (var i = 1; i < length; i += 2) {
            $("#passage").children("section")[i].style["background-color"] = "rgb(240, 240, 240)";
        }
    } else {
        for (var i = 0; i < length; i += 2) {
            $("#passage").children("section")[i].style["background-color"] = "rgb(240, 240, 240)";
        }
    }
})