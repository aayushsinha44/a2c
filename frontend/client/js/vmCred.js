var token = getCookie('user_token');
var ids = [];

var pool_id = getCookie('poolid');



// code on loading 
$(window).on("load", function(){
    console.log(token);
    if (!token) {
        window.location.href="/frontend/client/login.html";
    }
    var form = $('#vmform');
    var flag = 0;
    $.ajax({
        url: $(form).attr("action"),
        type: "GET",
        beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
        success: function(msg) { 
            //alert('Success!' + token);
            var vm_data = msg.data;
            console.log(msg.data);

            for(i in vm_data){
                flag = 1;
                var item = vm_data[i];
                ids.push(item.id);
                addEntryOnPage(item);
            }
            //if there is atleast one vm them start button will be displayed
            if(flag == 1){
                document.getElementById("start").style.display = "block";
            }

            //if there is an existing poolid then disable the start and addnew button
            if(pool_id){
                $.ajax({
                    url: "http://172.21.212.180:8000/track/"+pool_id,
                    type: "GET",
                    beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
                    success: function(msg) { 
                        if(msg.data.pool_info["in_use"] == true){
                            document.getElementById("start").disabled = true;
                            document.getElementById("addnew").disabled = true;
                        }
                    },
                    error: function(xhr){console.log(xhr.responseJSON.message, xhr);}
                });
            }
            
        },
        error: function(xhr){console.log(xhr.responseJSON.message, xhr);}
    });
});

$(document).ready(function(){
    console.log(token);
    var form = $('#vmform');

    //Adding new VM Details
    $(document).on("click", "#submit",function(){
        var data = document.getElementById("vmform");

        var vm_username = data.username.value;
        var vm_hostname = data.hostname.value;
        var vm_port = data.port.value;
        var vm_pkey = data.pkey.value;
        if(vm_pkey == "")
            vm_pkey = null;
        var vm_passphrase = data.passphrase.value;
        if(vm_passphrase==""){
            vm_passphrase = null;
        }
        var vm_password = data.pswd.value;
        var vm_no_replica = data.replica.value;

        $.ajax({
            url: $(form).attr("action"),
            type: "POST",
            data: JSON.stringify({
                vm_username: vm_username,
                vm_hostname: vm_hostname,
                vm_port: vm_port,
                vm_pKey: vm_pkey,
                vm_passphrase: vm_passphrase,
                vm_password: vm_password,
                vm_no_replica: vm_no_replica
            }),
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            dataType: 'json',
            success: function (data) {
                console.info(data);
                document.location.reload(true);
            },
            error: function(xhr){
                console.log("In error");
                console.log(xhr.responseJSON.message, xhr);
            }
        });
    });
    // Editing the VM Details
    $(document).on("click", ".edit_vm", function(){
        var div_id = $(this).parent().parent().attr("id");

        //send a get request for details of that particular vm
        //Load the received details in the form

        $("#vmdetailseditform").modal("show");

        $.ajax({
            url: $(form).attr("action") + div_id,
            type: "GET",
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            success: function(msg) { 
                //alert('Success!' + token); 
                console.log(msg);
                if(msg.data[0].vm_pkey === undefined)
                    msg.data[0].vm_pkey=""
                document.getElementById("uname1").value = msg.data[0].vm_username;
                document.getElementById("hname1").value = msg.data[0].vm_hostname;
                document.getElementById("prt1").value = msg.data[0].vm_port;
                document.getElementById("pk1").value = msg.data[0].vm_pkey;
                document.getElementById("pphrase1").value = msg.data[0].vm_passphrase;
                document.getElementById("rep1").value = msg.data[0].vm_no_replica;
                document.getElementById("pwd1").value = msg.data[0].vm_password;
            },
            error: function(xhr){console.log("hi" + xhr.responseJSON.message, xhr);}
        });

        
        //Read the details when the save changes button is pressed
        $(document).on("click", "#savechanges", function(){
            var data = document.getElementById("vmformedit");
            
            var vm_username = data.username1.value;
            var vm_hostname = data.hostname1.value;
            var vm_port = data.port1.value;
            var vm_pkey = data.pkey1.value;
            if(vm_pkey == "")
                vm_pkey = null;
            var vm_passphrase = data.passphrase1.value;
            if(vm_passphrase==""){
                vm_passphrase = null;
            }
            var vm_password = data.pswd1.value;
            var vm_no_replica = data.replica1.value;

            //Send a PUT request to update the details
            $.ajax({
                url: $(form).attr("action") + div_id,
                type: "PUT",
                beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
                data: JSON.stringify({
                    vm_username: vm_username,
                    vm_hostname: vm_hostname,
                    vm_port: vm_port,
                    vm_pKey: vm_pkey,
                    vm_passphrase: vm_passphrase,
                    vm_password: vm_password,
                    vm_no_replica: vm_no_replica
                }),
                dataType: 'json',
                success: function (data) {
                    console.info(data);
                    document.location.reload(true);
                },
                error: function(xhr){
                    console.log("In error");
                    console.log(xhr.responseJSON.message, xhr);
                }
            });
        });   
    });
    // Removing the Vm Details
    $(document).on("click", ".remove_vm", function () {
        var div_id = $(this).parent().parent().attr("id");
        //console.log(div_id);
        $.ajax({
            url: $(form).attr("action") + div_id,
            type: "DELETE",
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            dataType: 'json',
            success: function (data) {
                console.info(data);
                document.location.reload(true);
            },
            error: function(xhr){
                console.log("In error");
                console.log(xhr.responseJSON.message, xhr);
            }
        });
    });

    //Staring Containerization
    $(document).on("click", "#start", function(){
        
        $.ajax({
            url: "http://172.21.212.180:8000/start_process/",
            type: "POST",
            data: JSON.stringify({
                vm_id: ids
            }),
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            success: function(msg) { 
                //alert('Success!' + token);
                if(msg.message == "started"){
                    pool_id = msg.pool_id;
                    setCookie("poolid",pool_id,30);
                    console.log(pool_id);
                }
                document.getElementById("start").disabled = true;
                document.getElementById("addnew").disabled = true;

                console.log(msg);
            },
            error: function(xhr){
                console.log(xhr.responseJSON.message, xhr);
                if(xhr.responseJSON.message == "agent in use")
                    alert("Agent in use, try again")
            }
        });
    });
});

function resetForm(formId) {
    document.getElementById(formId).reset();
}

function createNewVM() {
    resetForm("vmform");
    $("#vmdetailsform").modal("show"); 
}

function showDetails(id, t) {
    var purpose = $(t).attr("id");
    if (purpose == "show") {
        $(id).show();
        $(t).html("<label>Show less&nbsp;&nbsp;</label><i class='fa fa-angle-up'></i>");
        $(t).attr("id", "hide");
    } else {
        $(id).hide();
        $(t).html("<label>Show status&nbsp;&nbsp;</label><i class='fa fa-angle-down'></i>");
        $(t).attr("id", "show");
    }
}
function getThisVMStatus(data){
    var id = data.id;

    var spinner = '<i class="fa fa-circle-o-notch fa-spin" style="font-size:18px"></i>';
    var tick = '<i class="fa fa-check" style="font-size:18px;color:green"></i>'


    
    var current_data = worker(data);

    var code = '<br>hello, Hi there ' + id + '&nbsp;&nbsp;' + tick + spinner;
    console.log("hello");
    document.getElementById("details"+id).innerHTML = code;
    
}

function worker(d) {
    $.ajax({
        url: "http://172.21.212.180:8000/track/21",
        type: "GET",
        beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
        success: function(msg) {
            //todo process and return data
            console.log("hi");


            setTimeout(function() {getThisVMStatus(d);}, 4000);
            return true;
            
        },
        complete: function() {
        // Schedule the next request when the current one's complete
        
        }
    });
}
function addEntryOnPage(data){
    //console.log(data);
    var edit_button = "<button class='btn btn-xs btn-warning edit_vm'><i class='fa fa-edit'></i>&nbsp;&nbsp;Edit</button>&nbsp;&nbsp;";
    var delete_button = "<button class='btn btn-xs btn-danger remove_vm'><i class='fa fa-trash'></i>&nbsp;&nbsp;Remove</button><br>";
    var vm_details = "<br><span id='details" + data.id + "' style='display: none'>Containerization Not Started</span>";
    var vm_display = "<span><label>" + data.vm_username + "@" + data.vm_hostname + "</label></span><br>";
    var new_vm = "<div class='row' id=" + data.id + " style='margin: 1em; border: 1px solid grey; border-radius: 4px; padding: 1em; width: 95%'> \
                <span style='float: right'>" + edit_button + delete_button + "</span>" + 
                vm_display + 
                "<button class='btn btn-sm btn-outline-info' id='show' onclick='showDetails(details" + data.id + ", this)'><label>Show status&nbsp;&nbsp;</label><i class='fa fa-angle-down'></i></button>" + 
                vm_details + 
                "</div>";
    $(".vm").append(new_vm);
    // getThisVMStatus(data);
}