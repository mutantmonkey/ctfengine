function loadScores(scoreurl, breakdownurl, highlights) {
    $.ajax({
        'url': scoreurl,
        'dataType': 'json',
        'beakdownurl': breakdownurl,
        'highlights': highlights,
    }).done(function(data){
        var scores = [];

        // hack to sort scores
        for(k in data['scores'])
        {
            scores.push(data['scores'][k]);
        }
        scores.sort(function(a, b){return a[2] < b[2]});

        JSON.stringify(scores);

        $('#scoreboard tr').remove();
        for(i in scores)
        {
            tr = document.createElement('tr');
            $(tr).attr('id', 'scoreboard_handle_' + scores[i][0]);

            handle = document.createElement('a');
            $(handle).attr('href', breakdownurl + scores[i][0]);
            $(handle).text(scores[i][1]);

            td = document.createElement('td');
            $(td).append(handle);
            $(tr).append(td);

            td = document.createElement('td');
            $(td).text(scores[i][2]);
            $(tr).append(td);

            $('#scoreboard').append(tr);
        }

        $('#scoreboard_total').text("Total points: " + data['total_points']);

        for(h in highlights) {
            $('#scoreboard_handle_' + highlights[h]).addClass('recent');
        }
    });
}

function liveScoreboard(liveurl, scoreurl, breakdownurl) {
    var source = new EventSource(liveurl);
    source.onmessage = function(ev) {
        msg = ev.data.split(': ');
        if(msg[0] == 'score') {
            loadScores(scoreurl, breakdownurl, [msg[1]]);
        }
    };
}
