$(document).ready(function(){
    var token = getCookie('user_token');
    console.log(token);
    if (!token) {
        window.location.href="/frontend/client/login.html";
    }
    var form = $('#doc_reg');
    $.ajax({
        url: $(form).attr("action"),
        type: "GET",
        beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
        success: function(msg) { 
            //alert('Success!' + token); 
            console.log(msg);
            document.getElementById("registry").value = msg.message.docker_registry;
            document.getElementById("uname").value = msg.message.docker_registry_username;
            document.getElementById("pwd").value = msg.message.docker_registry_password;
        },
        error: function(xhr){console.log("hi" + xhr.responseJSON.message, xhr);}
    });

    $(document).on("click", "#submit",function(){
        var data = document.getElementById("doc_reg");
        //console.log(form);
        var registry = data.registry.value;
        var username = data.username.value;
        var password = data.pswd.value;

        $.ajax({
            url: $(form).attr("action"),
            type: $(form).attr("method"),
            data: JSON.stringify({
                docker_registry_username: username,
                docker_registry_password: password,
                docker_registry: registry
            }),
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            dataType: 'json',
            success: function (data) {
                console.info(data);
            },
            error: function(xhr){console.log("hi" + xhr.responseJSON.message, xhr);}
        });
    });
});