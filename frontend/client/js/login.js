$(document).ready(function(){
    var x = getCookie('user_token');
    console.log(x)
    if (x) {
        window.location.href="/frontend/client/dashboard.html";
    }

    $(document).on("click", "#submit",function(){
        var form = $('#login');
        var data = document.getElementById("login");
        //console.log(form);
        var username = data.username.value;
        var password = data.pswd.value;

        $.post($(form).attr("action"), JSON.stringify({
            username: username,
            password: password
        }))
        .done(function(msg){
            token = msg.token; 
            setCookie("user_token",token,30);
            window.location.href = "/frontend/client/dashboard.html";
            console.log(msg.token)
        })
        .fail(function(xhr, status, error) {
            document.getElementById("error").innerHTML = xhr.responseJSON.message;
            console.log(status, error, xhr);
            
        });
    });
});