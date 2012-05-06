from flask import abort, flash, jsonify, render_template, request, redirect, \
        url_for

from ctfengine import app
from ctfengine import database
from ctfengine import lib
from ctfengine import models

flags = lib.load_flags(app.config['FLAG_PATH'])


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
    entered_handle = request.form['handle'].strip()
    entered_flag = request.form['flag'].strip()
    if len(entered_handle) <= 0 or len(entered_flag) <= 0:
        return make_error("Please enter a handle and a flag.")
    if entered_flag not in flags:
        return make_error(request, "That is not a valid flag.")

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
        return make_error(request, "You may not resubmit flags.")

    handle.score += flag['points']
    database.conn.commit()

    entry = models.FlagEntry(handle.id, flag['hostname'])
    database.conn.add(entry)
    database.conn.commit()

    if request.wants_json():
        return jsonify(entry.serialize())
    flash("Flag scored.")
    return redirect(url_for('index'))

def make_error(request, msg, code=400):
    if request.wants_json():
        response = jsonify({'message': msg})
        response.status_code = code
        return response
    else:
        flash(msg)
        return redirect(url_for('index'))
