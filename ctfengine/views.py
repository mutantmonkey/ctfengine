import hashlib
from flask import abort, flash, jsonify, render_template, request, redirect, \
        url_for

from ctfengine import app
from ctfengine import database
from ctfengine import lib
from ctfengine import models
import ctfengine.crack.lib
import ctfengine.crack.models
import ctfengine.pwn.models

@app.route('/')
def index():
    scores = models.Handle.topscores()
    total_points = database.conn.query(
            ctfengine.pwn.models.Flag.total_points()).first()[0] or 0
    total_points += database.conn.query(
            ctfengine.crack.models.Password.total_points()).first()[0] or 0

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
        return make_error(request, "Please enter a handle and a flag.")

    flag = ctfengine.pwn.models.Flag.get(entered_flag)
    if not flag:
        return make_error(request, "That is not a valid flag.")

    # search for handle
    handle = models.Handle.get(entered_handle)
    if not handle:
        handle = models.Handle(entered_handle, 0)
        database.conn.add(handle)
        database.conn.commit()

    existing_entry = ctfengine.pwn.models.FlagEntry.query.filter(
            ctfengine.pwn.models.FlagEntry.handle == handle.id,
            ctfengine.pwn.models.FlagEntry.flag == flag.id).first()
    if existing_entry:
        return make_error(request, "You may not resubmit flags.")

    # update points for user
    handle.score += flag.points
    database.conn.commit()

    # log flag submission
    entry = ctfengine.pwn.models.FlagEntry(handle.id, flag.id,
            request.remote_addr, request.user_agent.string)
    database.conn.add(entry)
    database.conn.commit()

    # mark machine as dirty if necessary
    if flag.machine:
        machine = database.conn.query(
                ctfengine.pwn.models.Machine).get(flag.machine)
        machine.dirty = True
        database.conn.commit()

    if request.wants_json():
        return jsonify(entry.serialize())
    flash("Flag scored.")
    return redirect(url_for('index'))


@app.route('/submitpw', methods=['POST'])
def submit_password():
    entered_handle = request.form['handle'].strip()
    if len(entered_handle) <= 0:
        return make_error(request, "Please enter a handle.")

    counts = {'good': 0, 'notfound': 0, 'bad': 0, 'duplicate': 0}
    entered_pws = request.form['passwords'].strip().splitlines()
    for entered_pw in entered_pws:
        entered_pw = entered_pw.split(':', 1)
        if len(entered_pw) <= 1:
            return make_error(request, "Cracked passwords must be in the "\
                    "hashed:plaintext format.")

        password = ctfengine.crack.models.Password.get(entered_pw[0])
        if not password:
            counts['notfound'] += 1
            continue

        # verify that the password is correct
        if ctfengine.crack.lib.hashpw(password.algo, entered_pw[1]) !=\
                password.password:
            counts['bad'] += 1
            continue

        # search for handle
        handle = models.Handle.get(entered_handle)
        if not handle:
            handle = models.Handle(entered_handle, 0)
            database.conn.add(handle)
            database.conn.commit()

        existing_entry = ctfengine.crack.models.PasswordEntry.query.filter(
                ctfengine.crack.models.PasswordEntry.handle == handle.id,
                ctfengine.crack.models.PasswordEntry.password == password.id).\
                        first()
        if existing_entry:
            counts['duplicate'] += 1
            continue

        counts['good'] += 1

        # update points for user
        handle.score += password.points

        # log password submission
        entry = ctfengine.crack.models.PasswordEntry(handle.id, password.id,
                entered_pw[1], request.remote_addr, request.user_agent.string)
        database.conn.add(entry)

    database.conn.commit()

    if request.wants_json():
        return jsonify(entry.serialize())
    flash("{good} passwords accepted, {notfound} not found in database, "\
            "{duplicate} passwords already scored, and {bad} incorrect "\
            "plaintexts.".format(**counts))
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    scores = models.Handle.topscores()
    total_points = database.conn.query(
            ctfengine.pwn.models.Flag.total_points()).first()[0] or 0
    total_points += database.conn.query(
            ctfengine.crack.models.Password.total_points()).first()[0] or 0

    machines = database.conn.query(ctfengine.pwn.models.Machine).\
            order_by(ctfengine.pwn.models.Machine.hostname)

    if request.wants_json():
        return jsonify({
            'scores': [(x.handle, x.score) for x in scores],
            'total_points': total_points,
            'machines': [m.serialize() for m in machines],
        })

    return render_template('dashboard.html', scores=scores,
            total_points=total_points, machines=machines)


def make_error(request, msg, code=400):
    if request.wants_json():
        response = jsonify({'message': msg})
        response.status_code = code
        return response
    else:
        flash(msg)
        return redirect(url_for('index'))
