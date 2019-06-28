$(document).ready(function(){
    $(document).on("click", "#logout", function(){
        logout();
    });
});
function logout(){
    eraseCookie('user_token');
    document.location.href = "/frontend/client/login.html";
}