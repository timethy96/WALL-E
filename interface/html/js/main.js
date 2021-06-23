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
            //alert(JSON.stringify(data)); // show response from the php script.
        },
        cache: false,
        contentType: false,
        processData: false
    });

    
});