$(document).ready(function(){
    var x = getCookie('user_token');
    console.log(x)
    if (!x) {
        window.location.href="/frontend/client/login.html";
    }

    
    //$(document).on("click", "#vm",function(){
    //    window.location.href = "/frontend/client/dockerCred.html";
    //});
});