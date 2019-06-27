$(document).ready(function(){
    var token = getCookie('user_token');
    console.log(token);
    if (!token) {
        window.location.href="/frontend/client/login.html";
    }
    var form = $('#agentform');
    console.log($(form).attr("action"));
    $.ajax({
        url: $(form).attr("action"),
        type: "GET",
        beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
        success: function(msg) { 
            //alert('Success!' + token); 
            console.log(msg);
            document.getElementById("agentip").value = msg.message[0].agent_ip;
        },
        error: function(xhr){console.log("hi " + xhr.responseJSON.message, xhr);}
    });
    
    $(document).on("click", "#submit",function(){
        var data = document.getElementById("agentform");
        //console.log(form);
        var vm_ip = data.agent_ip.value;
        $.ajax({
            url: $(form).attr("action"),
            type: $(form).attr("method"),
            data: JSON.stringify({
                agent_ip: vm_ip
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