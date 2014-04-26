liveScoreboard("{{ url_for('livestream') }}", "{{ url_for('index') }}", "breakdown/");
ajaxForm($('#submit_flag_form'), 'flag');
ajaxForm($('#submit_password_form'), 'password');
