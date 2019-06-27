$(document).ready(function(){
    var token = getCookie('user_token');
    console.log(token);
    if (!token) {
        window.location.href="/frontend/client/login.html";
    }
    var form = $('#vmform');
    // $.ajax({
    //     url: $(form).attr("action"),
    //     type: "GET",
    //     beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
    //     success: function(msg) { 
    //         //alert('Success!' + token); 
    //         console.log(msg);
    //         document.getElementById("registry").value = msg.message.docker_registry;
    //         document.getElementById("uname").value = msg.message.docker_registry_username;
    //         document.getElementById("pwd").value = msg.message.docker_registry_password;
    //     },
    //     error: function(xhr){console.log("hi" + xhr.responseJSON.message, xhr);}
    // });




    $(document).on("click", "#submit",function(){
        var data = document.getElementById("vmform");

        var vm_username = data.username.value;
        console.log(vm_username);
        var vm_hostname = data.hostname.value;
        var vm_port = data.port.value;
        var vm_pkey = data.pkey.value;
        var vm_passphrase = data.passphrase.value;
        var vm_password = data.pswd.value;

        $.ajax({
            url: $(form).attr("action"),
            type: $(form).attr("method"),
            data: JSON.stringify({
                vm_username: vm_username,
                vm_hostname: vm_hostname,
                vm_port: vm_port,
                vm_pKey: vm_pkey,
                vm_passphrase: vm_passphrase,
                vm_password: vm_password
            }),
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            dataType: 'json',
            success: function (data) {
                console.info(data);
            },
            error: function(xhr){
                console.log("In error");
                
                console.log("hi" + xhr.responseJSON.message, xhr);
            }
        });
    });
    $(document).on("click", ".remove_vm", function () {
        $(this).parent().remove();
    });
});

function resetForm(formId) {
    document.getElementById(formId).reset();
}

function createNewVM() {
    resetForm("vmform");
    $("#vmdetailsform").modal("show"); 
}
function addEntryOnPage(){


    var remove_button = "<button class='btn btn-xs btn-danger remove_vm' style='float: right;'><i class='fa fa-trash'></i>&nbsp;&nbsp;Remove</button><br>";
    var new_vm = "<div class='row' style='margin: 1em; border: 1px solid grey; border-radius: 4px; padding: 1em;'> \
                " + remove_button +
                "<label >VM Username:</label><p id='duname'></p>"
                "</div>";
    $(".vm").append(new_vm);
}