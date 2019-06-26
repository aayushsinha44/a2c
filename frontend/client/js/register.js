$(document).ready(function(){
    $(document).on("click", "#submit",function(){
      
      var form = $('#register');
      var data = document.getElementById("register");
      console.log(form);
      var username = data.username.value;
      var name = data.name.value;
      var password = data.pswd.value;

      

      $.post($(form).attr("action"), JSON.stringify({
        username: username,
        password: password,
        name: name
      }))
      .done(function(msg){ 
        console.log(msg.token)
      })
      .fail(function(xhr, status, error) {
          // error handling
          console.log(status, error,xhr);
          
      });
    });
});