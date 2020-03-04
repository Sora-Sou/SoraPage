window.onload = function () {
    // 邮件必填
    var emailInput = document.getElementsByClassName("vmail")[0];
    var button = document.getElementsByClassName("vsubmit")[0];
    if (emailInput.value == "") {
        button.setAttribute("disabled", true);
        button.innerHTML = "邮箱还没填呢";
        emailInput.oninput = checkEmailInput;
    } else {
        emailInput.oninput = checkEmailInput;
    }
    function checkEmailInput() {
        if (emailInput.value != "") {
            button.removeAttribute("disabled");
            button.innerHTML = "回复";
        } else {
            button.setAttribute("disabled", true);
            button.innerHTML = "邮箱还没填呢";
        }
    };
    // 自定义头像
    var avatar = setInterval(changeAvatar, 100);
    function changeAvatar() {
        $(".vnick").text(function (index, name) {
            if(name=="Sora"){
                $(this).css("color","red");
                $(this).closest(".vcard").children(".vimg").attr("src","/wholeSite/img/icon.png").css("border","none");
            }else{
                $(this).closest(".vcard").children(".vimg").attr("src","/wholeSite/img/avatar.png").css("border","none");
            }
        })
    }
}
