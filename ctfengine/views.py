from flask import abort, render_template, request, jsonify

from ctfengine import app
from ctfengine import database
from ctfengine import lib
from ctfengine import models


@app.route('/')
def index():
    scores = models.Handle.topscores()
    if request.wants_json():
        out = {}
        for score in scores:
            out[score.handle] = score.score
        return jsonify(out)

    return render_template('index.html', scores=scores)


@app.route('/submit', methods=['POST'])
def submit_flag():
    flags = lib.load_flags(app.config['FLAG_PATH'])

    entered_handle = request.form['handle'].strip()
    entered_flag = request.form['flag'].strip()
    if len(entered_handle) > 0 and len(entered_flag) > 0:
        if entered_flag not in flags:
            return "not a valid flag"

        flag = flags[entered_flag]

        # search for handle
        handle = models.Handle.get(entered_handle)
        if not handle:
            handle = models.Handle(entered_handle, 0)
            database.conn.add(handle)
            database.conn.commit()

        existing_entry = models.FlagEntry.query.filter(
                models.FlagEntry.handle == handle.id,
                models.FlagEntry.hostname == flag['hostname']).first()
        if existing_entry:
            return "you may not resubmit flags"

        handle.score += flag['points']
        database.conn.commit()

        entry = models.FlagEntry(handle.id, flag['hostname'])
        database.conn.add(entry)
        database.conn.commit()

        return jsonify(entry.serialize())
