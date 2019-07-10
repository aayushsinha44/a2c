var token = getCookie('user_token');
// code on loading 
$(window).on("load", function(){
    console.log(token);
    if (!token) {
        window.location.href="/frontend/client/login.html";
    }
    $.ajax({
        url: "http://172.21.212.180:8000/get_services/",
        type: "GET",
        beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
        success: function(msg) {
            console.log(msg);
            var array = msg.message.split(" ");
            ret_code = "";
            var table_start = '<table class="table table-striped" style="width:90%">';
            var table_end = '</table>';

            ret_code += table_start;
            ret_code += '<thead>';
            ret_code += '<tr>';
            ret_code += '<th>' + array[0] + '</th><th>' + array[1] + '</th><th>' + array[2] + '</th><th>' + array[3] + '</th><th>' + array[4] + '</th><th>' + array[5].split("\n")[0] + '</th>';
            ret_code += '</tr>';
            ret_code += '</thead>';
            ret_code += '<tbody>';
            ret_code += '<tr>';
            ret_code += '<td>' + array[5].split("\n")[1] + '</td><td>' + array[6] + '</td><td>' + array[7] + '</td><td>' + '\<none\>' + '</td><td>' + array[9] + '</td><td>' + array[10].split("\n")[0] + '</td>';
            ret_code += '</tr>';

            array = msg.message.split("\n");

            for(ele in array){
                if(ele!=0 && ele!=1){
                    line = array[ele].split(" ");
                    if(line.length <= 1)
                        continue;
                    ret_code += '<tr>';
                    for(word in line){
                        ret_code += '<td>';
                        ret_code += line[word];
                        ret_code += '</td>';
                    }
                    ret_code += '</tr>';
                    
                }
            }
            ret_code += '</tbody>';
            ret_code += table_end;
            document.getElementById("kubeser").innerHTML = ret_code;
        },
        error: function(xhr){
            console.log(xhr.responseJSON.message, xhr);
            document.getElementById("kubeser").innerHTML = xhr.responseJSON.message;
        }
    });
});