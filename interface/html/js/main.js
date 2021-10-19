$("#bImgUl").click(function(){
    $(".ul").slideUp();
    $("#imgUl").slideDown();
});
$("#bDrawUl").click(function(){
    $(".ul").slideUp();
    $("#drawUl").slideDown();
});
$("#bVidUl").click(function(){
    $(".ul").slideUp();
    $("#vidUl").slideDown();
});
$(".ulForm").submit(function(e) {

    $(".loading").show();
    $(".responseText").html("");

    e.preventDefault(); // avoid to execute the actual submit of the form.

    var formData = new FormData(this);
    var url = $(this).attr('action');
    
    $.ajax({
        type: "POST",
        url: url,
        data: formData,
        success: function(data) {
            $(".loading").hide();
            $(".responseText").html(data.Result);
            $(".responseText").css("color","darkgreen");
            updateQueue();
        },
        cache: false,
        contentType: false,
        processData: false
    });

    
});

function updateQueue()
{ 
    $( "#queueDiv" ).load(" #queueDiv > *" );
}

$(document).ready(function(){
    setInterval(function(){
          updateQueue();
    },10000);
});


$(document).on('click', '.delMov', function(e) {

    $(this).html("&#x23F3;");

    var formData = new FormData(this.parentNode);
    var url = $(this).parent().attr('action');
    
    $.ajax({
        type: "POST",
        url: url,
        data: formData,
        success: function(data) {
            updateQueue();
        },
        cache: false,
        contentType: false,
        processData: false
    });

    
});

$(document).on('click', '.headerForm', function(e) {

    $(this).children('span').html("&#x23F3;");
    const clickedForm = this;

    var formData = new FormData(this);
    var url = $(this).attr('action');
    
    $.ajax({
        type: "POST",
        url: url,
        data: formData,
        success: function(data) {
            alert(data.success);
            $(clickedForm).children('span').html("&#x1F50C;");
        },
        error: function(data) {
            alert(JSON.stringify(data));
            $(clickedForm).children('span').html("&#x1F50C;");
        },
        cache: false,
        contentType: false,
        processData: false
    });

    
});