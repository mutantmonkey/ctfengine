$('#flash').click(function(){
    $('#flash').fadeOut('slow');
});

function flash(msg) {
    $('#flash').text(msg);
    $('#flash').fadeIn('slow');

    window.setTimeout(function(){
        $('#flash').fadeOut('slow');
    }, 5000);
}

function ajaxForm(frm, submitType) {
    $(frm).submit(function() {
        data = $(this).serializeArray();

        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: data,
            dataType: 'json',
            frm: frm,
            submitType: submitType,
        }).done(function(msg) {
            //$('.clear-after-submit').val('');
            $(frm)[0].reset();

            if(this.submitType == 'flag') {
                flash("Flag scored.");
            }
            else {
                flash(msg['status']['good'] + " passwords accepted, " +
                    msg['status']['notfound'] + " not found in database, " +
                    msg['status']['duplicate'] + " passwords already " +
                    "scored, and " + msg['status']['bad'] + " incorrect " +
                    "plaintexts.");
            }
        }).fail(function(resp) {
            $(frm)[0].reset();

            data = JSON.parse(resp.responseText);
            flash(data['message']);
        });

        return false;
    });
}
