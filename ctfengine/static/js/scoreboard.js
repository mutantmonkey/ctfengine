function loadScores(scoreurl) {
    $.ajax({
        'url': scoreurl,
        'dataType': 'json',
    }).done(function(data){
        scores = [];

        // hack to sort scores
        for(k in data['scores'])
        {
            scores.push([data['scores'][k][0], data['scores'][k][1]]);
        }
        scores.sort(function(a, b){return a[1] < b[1]});

        JSON.stringify(scores);

        $('#scoreboard tr').remove();
        for(i in scores)
        {
            tr = document.createElement('tr');

            td = document.createElement('td');
            $(td).text(scores[i][0]);
            $(tr).append(td);

            td = document.createElement('td');
            $(td).text(scores[i][1]);
            $(tr).append(td);

            $('#scoreboard').append(tr);
        }

        total = $('#scoreboard_total').text("Total points: " +
                data['total_points']);
    });
}

function liveScoreboard(liveurl, scoreurl) {
    var source = new EventSource(liveurl);
    source.onmessage = function(ev) {
        msg = ev.data.split(': ');
        if(msg[0] == 'score') {
            loadScores(scoreurl);
        }
    };
}
