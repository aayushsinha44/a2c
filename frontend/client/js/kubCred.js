$(document).ready(function(){
    var token = getCookie('user_token');
    console.log(token);
    if (!token) {
        window.location.href="/frontend/client/login.html";
    }
    var form = $('#kube');
    $.ajax({  
        url: $(form).attr("action"),
        type: "GET",
        beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
        success: function(msg) { 
            //alert('Success!' + token); 
            console.log(msg);
            document.getElementById("kubefile").value = msg.message.kube_conf_file;
        },
        error: function(xhr){console.log("hi " + xhr.responseJSON.message, xhr);}
    });
    
    $(document).on("click", "#submit",function(){
        var data = document.getElementById("kube");
        //console.log(form);
        var conf_file = data.kubeconf.value;
        $.ajax({
            url: $(form).attr("action"),
            type: $(form).attr("method"),
            data: JSON.stringify({
                kube_conf_file: conf_file
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