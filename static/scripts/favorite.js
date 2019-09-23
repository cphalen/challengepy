function favoriteClub(username, club) {
  // Technically this would cause an issue if
  // somebody created an account with the username "None"
  // but I'm just going to leave that as a standing issue
  if(username == "None") {
    alert("Sign in to favorite clubs!")
  }

  url = "/api/favorite"
  data = {
    "username": username,
    "club": club
  }

  $.ajax({
    type: "POST",
    url: url,
    data: data
  }).then(() => {
    location.reload();
  });
}
