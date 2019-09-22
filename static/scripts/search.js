$('#searchBtn').click(function(){

  parameter = $("input#searchParameter").val()
  clubs = $("section.club")

  for (var i = 0; i < clubs.length; i++) {
    club = clubs[i]
    name = club.children[0].textContent

    if (!name.includes(parameter)) {
      club.style.display = "none";
    } else {
      club.style.display = "block"
    }
  }
});
