function validatePasswords() {
  var password = document.getElementById("password").value;
  var confirmPassword = document.getElementById("confirmPassword").value;
  console.log(password);
  console.log(confirmPassword);
  return password == confirmPassword;
}

function checkPasswords(input) {
    if(!validatePasswords()){
        input.setCustomValidity('The passwords don\'t match!');
    } else {
        input.setCustomValidity('');
    }
    return true;
}
