var token = getCookie('user_token');


$(document).ready(function(){
    $(document).on("click", "#start", function(){
        console.log(token);
        $.ajax({
            url: "http://172.21.212.180:8000/track/30",
            type: "GET",
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            success: function(msg) { 
                //alert('Success!' + token);
                console.log(msg);
            },
            error: function(xhr){console.log(xhr.responseJSON.message, xhr);}
        });
    });
});

$(document).ready(function(){
    $(document).on("click", "#startp", function(){
        console.log(token);
        $.ajax({
            url: "http://172.21.212.180:8000/get_services/",
            type: "GET",
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            success: function(msg) { 
                //alert('Success!' + token);
                console.log(msg);
            },
            error: function(xhr){console.log(xhr.responseJSON.message, xhr);}
        });
    });
});

function makeCookie(n){
    setCookie("poolid", n, 1);
}