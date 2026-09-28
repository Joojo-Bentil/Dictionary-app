window.onload = function() {
    $('#word-form').hide();
    $('.edit-word, .edit-meaning').hide();
    $('.submit, .cancel').parent().hide();
    

    $('#word-index').click(function() {
        location.reload();
    });

    $('#word-add').click(function() {
        $('#word-index').removeClass('side-active');
        $(this).addClass('side-active');
        $('#word-form').show();
    });

    $('#word-form').submit(function() {
        let word = $('#word').val();
        let meaning = $('#meaning').val();

        $.ajax({
            url: '/word',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({
                'word': word,
                'meaning': meaning
            }),
            contentType: 'application/json; charset=utf-8',
            success: function(data) {
                location.reload();
            },
            error: function(err) {
                console.log(err);
            }
        });
    });


    $('#cancel').click(function() {
        location.reload();
    });

    //Delete operation
    $('.delete').click(function() {
        let word_id = $(this).attr('id');

        $.ajax({
            url: '/word/' + word_id + '/delete',
            type: 'POST',
            success: function(data) {
                location.reload();
            },
            error: function(err) {
                console.log(err);
            }
        });
    });

    $('.edit').click(function() {
        let parent = $(this).parents('tr');
        parent.find('.edit-word, .edit-meaning').show();
        parent.find('.word-word, .word-meaning').hide();
        parent.find('.submit, .cancel').parent().show();
        parent.find('.edit, .delete').parent().hide();
    });

    $('.cancel').click(function() {
        location.reload();
    });

    $('.update-form').submit(function() {
        let parent = $(this).parents('tr');
        let word = parent.find('input').val();
        let meaning = parent.find('textarea').val();
        let word_id = parent.find('.submit').attr('id');

        $.ajax({
            url: '/word/' + word_id + '/edit',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({
                'word': word,
                'meaning': meaning
            }),
            contentType: 'application/json; charset=utf-8',
            success: function(data) {
                location.reload();
            },
            error: function(err) {
                console.log(err);
            }
        });
    });

}