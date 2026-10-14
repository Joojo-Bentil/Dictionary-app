window.onload = function() {
    $('.password-toggle').on('click', function() {
        let input = document.getElementById(this.dataset.target);
        if (!input) {
            return;
        }

        let showPassword = input.type === 'password';
        input.type = showPassword ? 'text' : 'password';
        this.setAttribute('aria-pressed', showPassword ? 'true' : 'false');
        this.setAttribute('aria-label', showPassword ? 'Hide password' : 'Show password');
        $(this).find('.eye-icon-open').toggle(!showPassword);
        $(this).find('.eye-icon-closed').toggle(showPassword);
    });

    $('#word-form').hide();
    $('#words-csv-form').hide();
    $('#logo-form').hide();
    $('.edit-word, .edit-meaning').hide();
    $('.update-actions').hide();
    

    $('#word-index').click(function() {
        location.reload();
    });

    // create operation for adding a word and its meaning
    $('#word-add').click(function() {
        $('#word-index, #logo-add').removeClass('side-active');
        $(this).addClass('side-active');
        $('#word-form').show();
        $('#words-csv-form').show();
        $('#logo-form').hide();
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

    $('#words-csv-form').submit(function(event) {
        event.preventDefault();
        let formData = new FormData(this);

        $.ajax({
            url: this.action,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            dataType: 'json',
            success: function(response) {
                alert(response.message);
                location.reload();
            },
            error: function(xhr) {
                let message = xhr.responseJSON && xhr.responseJSON.message
                    ? xhr.responseJSON.message
                    : 'Unable to import the CSV file. Please try again.';
                alert(message);
            }
        });
    });

    $('#file-cancel').click(function() {
        location.reload();
    });

    //create operation for user registration
    $('.user-registration-form').submit(function(event) {
        event.preventDefault();
        let fullname = $('#full_name').val();
        let email = $('#email').val();
        let password = $('#password').val();
        let confirm_password = $('#confirm_password').val();

        if (password !== confirm_password) {
            alert('Passwords do not match!');
            return;
        }

        $.ajax({
            url: this.action,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({
                'fullname': fullname,
                'email': email,
                'password': password,
                'confirm_password': confirm_password
            }),
            contentType: 'application/json; charset=utf-8',
            success: function(data) {
                window.location.assign(data.redirect);
            },
            error: function(xhr) {
                let message = xhr.responseJSON && xhr.responseJSON.message
                    ? xhr.responseJSON.message
                    : 'Unable to register account. Please try again.';
                alert(message);
            }
        });
    });

    // Sign in with the credentials registered for the account.
    $('.login-form').submit(function(event) {
        event.preventDefault();

        $.ajax({
            url: this.action,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({
                email: $('#username').val(),
                password: $('#password').val()
            }),
            contentType: 'application/json; charset=utf-8',
            success: function(data) {
                window.location.assign(data.redirect);
            },
            error: function(xhr) {
                let message = xhr.responseJSON && xhr.responseJSON.message
                    ? xhr.responseJSON.message
                    : 'Unable to sign in. Please try again.';
                alert(message);
            }
        });
    });

    // logo add operation
    $('#logo-add').click(function() {
        $('#word-index, #word-add').removeClass('side-active');
        $(this).addClass('side-active');
        $('#word-form').hide();
        $('#words-csv-form').hide();
        $('#logo-form').show();
    });

    $('#logo-cancel').click(function() {
        location.reload();
    });

    $('#logo-form').submit(function() {
        let data =new FormData();
        data.append('file', $('#logo')[0].files[0]);

        $.ajax({
            url: '/add_logo',
            type: 'POST',
            data: data,
            enctype: 'multipart/form-data',
            processData: false,
            contentType: false,
            success: function(data) {
                location.reload();
            },
            error: function(err) {
                console.log(err);
            }
        });
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


    // update operation
    $('.edit').click(function() {
        let parent = $(this).parents('tr');
        parent.find('.edit-word input').val(parent.find('.word-word').text());
        parent.find('.edit-meaning textarea').val(parent.find('.word-meaning').text());
        parent.find('.edit-word, .edit-meaning').show();
        parent.find('.word-word, .word-meaning').hide();
        parent.find('.update-actions').show();
        parent.find('.edit, .delete').parent().hide();
    });

    $('.cancel').click(function() {
        let parent = $(this).parents('tr');
        parent.find('.edit-word input').val(parent.find('.word-word').text());
        parent.find('.edit-meaning textarea').val(parent.find('.word-meaning').text());
        parent.find('.edit-word, .edit-meaning, .update-actions').hide();
        parent.find('.word-word, .word-meaning').show();
        parent.find('.edit, .delete').parent().show();
    });

    $('.submit').click(function() {
        let parent = $(this).parents('tr');
        let wordInput = parent.find('.edit-word input')[0];
        let meaningInput = parent.find('.edit-meaning textarea')[0];
        if (!wordInput.reportValidity() || !meaningInput.reportValidity()) {
            return;
        }

        let word = wordInput.value.trim();
        let meaning = meaningInput.value.trim();
        if (!word || !meaning) {
            alert('Word and meaning are required.');
            return;
        }

        let word_id = $(this).attr('id');
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
                parent.find('.word-word').text(word).show();
                parent.find('.word-meaning').text(meaning).show();
                wordInput.value = word;
                meaningInput.value = meaning;
                parent.find('.edit-word, .edit-meaning, .update-actions').hide();
                parent.find('.edit, .delete').parent().show();
            },
            error: function(xhr) {
                let message = xhr.responseJSON && xhr.responseJSON.message
                    ? xhr.responseJSON.message
                    : 'Unable to update this word. Please try again.';
                alert(message);
            }
        });
    });

}