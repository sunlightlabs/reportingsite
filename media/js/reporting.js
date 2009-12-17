$().ready(function() {
    $("div.otherProperty img").hover(function(){
        $(this).attr("src", $(this).attr("data-color"));
    }, function(){
        $(this).attr("src", $(this).attr("data-grey"));
    });
});