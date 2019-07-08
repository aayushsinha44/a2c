var token = getCookie('user_token');
// code on loading 
$(window).on("load", function(){
    console.log(token);
    if (!token) {
        window.location.href="/frontend/client/login.html";
    }
    var form = $('#vmform');
    var flag = 0;
    $.ajax({
        url: "http://172.21.212.180:8000/get_services/",
        type: "GET",
        beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
        success: function(msg) {
            console.log(msg);
            document.getElementById("kubeser").innerHTML = msg.message.split(" ");
        },
        error: function(xhr){console.log(xhr.responseJSON.message, xhr);}
    });
});

// $(document).ready(function(){
//     var token = getCookie('user_token');
//     console.log(token);
//     if (!token) {
//         window.location.href="/frontend/client/login.html";
//     }
//     var form = $('#doc_reg');
//     $.ajax({
//         url: $(form).attr("action"),
//         type: "GET",
//         beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
//         success: function(msg) { 
//             //alert('Success!' + token); 
//             console.log(msg);
//             document.getElementById("regis").value = msg.message.docker_registry;
//             document.getElementById("uname").value = msg.message.docker_registry_username;
//             document.getElementById("pwd").value = msg.message.docker_registry_password;
//         },
//         error: function(xhr){console.log(xhr.responseJSON.message, xhr);}
//     });

//     $(document).on("click", "#submit",function(){
//         var data = document.getElementById("doc_reg");
//         //console.log(form);
//         var registry = data.registry.value;
//         var username = data.username.value;
//         var password = data.pswd.value;

//         $.ajax({
//             url: $(form).attr("action"),
//             type: $(form).attr("method"),
//             data: JSON.stringify({
//                 docker_registry_username: username,
//                 docker_registry_password: password,
//                 docker_registry: registry
//             }),
//             beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
//             dataType: 'json',
//             success: function (data) {
//                 console.info(data);
//                 window.location.href="/frontend/client/dashboard.html";
//             },
//             error: function(xhr){console.log("hi" + xhr.responseJSON.message, xhr);}
//         });
//     });
// });