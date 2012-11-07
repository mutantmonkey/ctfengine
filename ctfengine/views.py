import hashlib
from flask import abort, flash, jsonify, render_template, request, redirect, \
        url_for

from ctfengine import app
from ctfengine import database
from ctfengine import lib
from ctfengine import models

@app.route('/')
def index():
    scores = models.Handle.topscores()
    total_points = database.conn.query(models.Flag.total_points()).first()[0]
    if request.wants_json():
        return jsonify({
            'scores': [(x.handle, x.score) for x in scores],
            'total_points': total_points,
        })

    return render_template('index.html', scores=scores,
            total_points=total_points)


@app.route('/submit', methods=['POST'])
def submit_flag():
    entered_handle = request.form['handle'].strip()
    entered_flag = request.form['flag'].strip()
    if len(entered_handle) <= 0 or len(entered_flag) <= 0:
        return make_error("Please enter a handle and a flag.")

    flag = models.Flag.get(entered_flag)
    if not flag:
        return make_error(request, "That is not a valid flag.")

    # search for handle
    handle = models.Handle.get(entered_handle)
    if not handle:
        handle = models.Handle(entered_handle, 0)
        database.conn.add(handle)
        database.conn.commit()

    existing_entry = models.FlagEntry.query.filter(
            models.FlagEntry.handle == handle.id,
            models.FlagEntry.flag == flag.id).first()
    if existing_entry:
        return make_error(request, "You may not resubmit flags.")

    # update points for user
    handle.score += flag.points
    database.conn.commit()

    # log flag submission
    entry = models.FlagEntry(handle.id, flag.id, request.remote_addr,
            request.user_agent.string)
    database.conn.add(entry)
    database.conn.commit()

    # mark machine as dirty if necessary
    if flag.machine:
        machine = database.conn.query(models.Machine).get(flag.machine)
        machine.dirty = True
        database.conn.commit()

    if request.wants_json():
        return jsonify(entry.serialize())
    flash("Flag scored.")
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    machines = database.conn.query(models.Machine).all()
    if request.wants_json():
        return jsonify({
            'machines': [m.serialize() for m in machines],
        })

    return render_template('dashboard.html', machines=machines)


def make_error(request, msg, code=400):
    if request.wants_json():
        response = jsonify({'message': msg})
        response.status_code = code
        return response
    else:
        flash(msg)
        return redirect(url_for('index'))
