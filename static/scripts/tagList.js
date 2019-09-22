$('#addbtn').click(function(){
    var newitem = $('#add').val();

    if(newitem == "") {
        return true;
    }

    var uniqid = Math.round(new Date().getTime() + (Math.random() * 100));
    $('#tagList').append('<li id="'+uniqid+'" class="list-group-item"><input type="button" data-id="'+uniqid+'" class="listelement btn btn-primary btn-sm" value="X" /> '+newitem+'<input type="hidden" name="listed[]" value="'+newitem+'"></li>');
    $('#add').val('');
    return false;
});

$('#tagList').delegate(".listelement", "click", function() {
    var elemid = $(this).attr('data-id');
    $("#"+elemid).remove();
});
