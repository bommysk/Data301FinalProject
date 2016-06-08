$(function() {
    $('button').click(function() {
        $.ajax({
            url: '/handlereview',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                $("#reviewText").html(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});