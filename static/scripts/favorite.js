function favoriteClub(username, club) {
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
