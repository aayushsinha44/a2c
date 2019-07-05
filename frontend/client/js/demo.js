var token = getCookie('user_token');

$(document).ready(function(){
    $(document).on("click", "#start", function(){
        console.log(token);
        $.ajax({
            url: "http://172.21.212.180:8000/track/14",
            type: "GET",
            beforeSend: function(xhr){xhr.setRequestHeader('token', token);},
            success: function(msg) { 
                //alert('Success!' + token);
                console.log(msg);
            },
            error: function(xhr){console.log(xhr.responseJSON.message, xhr);}
        });
    });

    // var set_delay = 5000,
    // callout = function () {
    //     $.ajax({
    //         /* blah */
    //     })
    //     .done(function (response) {
    //         // update the page
    //     })
    //     .always(function () {
    //         setTimeout(callout, set_delay);
    //     });
    // };

    // initial call
    //callout();

    // (function worker() {
    //     $.ajax({
    //       url: 'ajax/test.html', 
    //       success: function(data) {
    //         $('.result').html(data);
    //       },
    //       complete: function() {
    //         // Schedule the next request when the current one's complete
    //         setTimeout(worker, 5000);
    //       }
    //     });
    //   })();


});

function makeCookie(n){
    setCookie("poolid", n, 1);
}