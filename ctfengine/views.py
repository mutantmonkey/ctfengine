import hashlib
from flask import abort, flash, jsonify, make_response, render_template, \
    request, redirect, url_for, Response

from ctfengine import app
from ctfengine import db
from ctfengine import lib
from ctfengine import models
from ctfengine.models import Handle
from ctfengine.crack.models import Password, PasswordEntry
from ctfengine.pwn.models import Flag, FlagEntry, Machine
from ctfengine import sse
import ctfengine.crack.lib


def serialize_date(item):
    item['datetime'] = str(item['datetime'])
    return item


def serialize_dates(items):
    for item in items:
        item['datetime'] = str(item['datetime'])
    return items


@app.route('/')
@app.route('/scores')
def index():
    scores = Handle.top_scores()
    total_points = Flag.total_points() + Password.total_points()

    if request.wants_json():
        return jsonify({
            'scores': [(x.id, x.handle, x.score) for x in scores],
            'total_points': total_points,
        })

    return render_template('index.html',
                           CTF_NAME=app.config['CTF_NAME'],
                           scores=scores,
                           total_points=total_points)


@app.route('/submit', methods=['POST'])
def submit_flag():
    entered_handle = request.form['handle'].strip()
    entered_flag = request.form['flag'].strip()
    if len(entered_handle) <= 0 or len(entered_flag) <= 0:
        return make_error(request, "Please enter a handle and a flag.")

    flag = Flag.get(entered_flag)
    if not flag:
        return make_error(request, "That is not a valid flag.")

    # search for handle
    handle = Handle.get(entered_handle)
    if not handle:
        handle = Handle(entered_handle, 0)
        db.session.add(handle)
        db.session.commit()

    existing_entry = FlagEntry.query.filter(
        FlagEntry.handle == handle.id,
        FlagEntry.flag == flag.id).first()
    if existing_entry:
        return make_error(request, "You may not resubmit flags.")

    # update points for user
    handle.score += flag.points

    # log flag submission
    entry = FlagEntry(handle.id,
                      flag.id,
                      request.remote_addr,
                      request.user_agent.string)
    db.session.add(entry)

    # mark machine as dirty if necessary
    if flag.machine:
        machine = Machine.query.get(flag.machine)
        machine.dirty = True

    db.session.commit()

    sse.send("score: {handle_id}: flag".format(handle_id=handle.id))

    if request.wants_json():
        return jsonify(serialize_date(entry.serialize()))
    flash("Flag scored.")
    return redirect(url_for('index'))


@app.route('/submitpw', methods=['POST'])
def submit_password():
    entered_handle = request.form['handle'].strip()
    if len(entered_handle) <= 0:
        return make_error(request, "Please enter a handle.")

    handle = Handle.get(entered_handle)

    counts = {'good': 0, 'notfound': 0, 'bad': 0, 'duplicate': 0}
    entered_pws = request.form['passwords'].strip().splitlines()
    for entered_pw in entered_pws:
        entered_pw = entered_pw.split(':', 1)
        if len(entered_pw) <= 1:
            return make_error(request, "Cracked passwords must be in the "
                              "hashed:plaintext format.")

        password = Password.get(entered_pw[0])
        if not password:
            # hash not found in DB
            counts['notfound'] += 1
        elif ctfengine.crack.lib.hashpw(password.algo, entered_pw[1]) !=\
                password.password:
            # plaintext is not correct for hash
            counts['bad'] += 1
        else:
            if not handle:
                # handle does not exist, create
                handle = Handle(entered_handle, 0)
                db.session.add(handle)
                db.session.commit()

            # look for existing entries
            existing_entry = PasswordEntry.query.filter(
                PasswordEntry.handle == handle.id,
                PasswordEntry.password == password.id).first()
            if existing_entry:
                counts['duplicate'] += 1
            else:
                counts['good'] += 1

                # update points for user
                handle.score += password.points

                # log password submission
                entry = PasswordEntry(handle.id,
                                      password.id,
                                      entered_pw[1],
                                      request.remote_addr,
                                      request.user_agent.string)
                db.session.add(entry)
                db.session.commit()

    if counts['good'] > 0:
        sse.send("score: {handle_id:d}: password".format(handle_id=handle.id))

    if request.wants_json():
        return jsonify({'status': counts})
    flash("{good} passwords accepted, {notfound} not found in database, "
          "{duplicate} passwords already scored, and {bad} incorrect "
          "plaintexts.".format(**counts))
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    scores = Handle.top_scores()
    total_points = Flag.total_points() + Password.total_points()
    machines = Machine.query.order_by(Machine.hostname)

    if request.wants_json():
        return jsonify({
            'scores': [(x.id, x.handle, x.score) for x in scores],
            'total_points': total_points,
            'machines': [m.serialize() for m in machines],
        })

    return render_template('dashboard.html',
                           CTF_NAME=app.config['CTF_NAME'],
                           scores=scores,
                           total_points=total_points,
                           machines=machines)


@app.route('/breakdown/<int:handle_id>')
def score_breakdown(handle_id):
    handle = Handle.query.get_or_404(handle_id)

    flags = db.session.query(FlagEntry, Flag).\
        filter(FlagEntry.handle == handle_id).\
        join(Flag, FlagEntry.flag == Flag.id).\
        order_by(FlagEntry.datetime).all()
    score_flags = 0
    for entry in flags:
        score_flags += entry[1].points

    passwords = db.session.query(PasswordEntry, Password).\
        filter(PasswordEntry.handle == handle_id).\
        join(Password, PasswordEntry.password == Password.id).\
        order_by(PasswordEntry.datetime).all()
    score_passwords = 0
    for entry in passwords:
        score_passwords += entry[1].points

    if request.wants_json():
        flagdata = []
        for entry in flags:
            flagdata.append(entry[0].serialize(entry[1]))

        pwdata = []
        for entry in passwords:
            pwdata.append(entry[0].serialize(entry[1]))

        return jsonify({
            'handle': handle.serialize(),
            'flags': serialize_dates(flagdata),
            'passwords': serialize_dates(pwdata),
            'score_flags': score_flags,
            'score_passwords': score_passwords,
        })

    return render_template('breakdown.html',
                           CTF_NAME=app.config['CTF_NAME'],
                           handle=handle,
                           flags=flags,
                           passwords=passwords,
                           score_flags=score_flags,
                           score_passwords=score_passwords)


@app.route('/flag/<int:flag_id>')
def pwn_submissions(flag_id):
    flag = Flag.query.get_or_404(flag_id)

    submissions = db.session.query(FlagEntry, Handle).\
        filter(FlagEntry.flag == flag.id).\
        join(Handle, Handle.id == FlagEntry.handle).\
        order_by(FlagEntry.datetime).all()

    if request.wants_json():
        subdata = []
        for entry, handle in submissions:
            subdata.append({
                'entry': serialize_date(entry.serialize()),
                'handle': handle.serialize(),
            })
        return jsonify({
            'flag': flag.serialize(),
            'submissions': subdata,
        })

    return render_template('pwn_submissions.html',
                           CTF_NAME=app.config['CTF_NAME'],
                           flag=flag,
                           submissions=submissions)


@app.route('/password/<int:password_id>')
def crack_submissions(password_id):
    password = Password.query.get_or_404(password_id)

    submissions = db.session.query(PasswordEntry, Handle).\
        filter(PasswordEntry.password == password.id).\
        join(Handle, Handle.id == PasswordEntry.handle).\
        order_by(PasswordEntry.datetime).all()

    if request.wants_json():
        def serialize_date(item):
            item['datetime'] = str(item['datetime'])
            return item

        subdata = []
        for entry, handle in submissions:
            subdata.append({
                'entry': serialize_date(entry.serialize()),
                'handle': handle.serialize(),
            })

        return jsonify({
            'flag': flag.serialize(),
            'submissions': subdata,
        })

    return render_template('crack_submissions.html',
                           CTF_NAME=app.config['CTF_NAME'],
                           password=password,
                           submissions=submissions)


@app.route('/passwords/<string:algo>')
def list_hashes(algo):
    passwords = Password.query.filter(Password.algo == algo).all()
    if not passwords:
        abort(404)

    hashed = [pw.password for pw in passwords]
    if request.wants_json():
        return jsonify({
            'algo': algo,
            'hashes': hashed,
        })

    return Response("\n".join(hashed), mimetype="text/plain")


@app.route('/live')
def livestream():
    response = Response(sse.event_stream(), mimetype="text/event-stream")
    response.headers['Cache-Control'] = "no-cache"
    response.headers['Connection'] = "keep-alive"
    response.headers['X-Accel-Buffering'] = "no"
    return response


def make_error(request, msg, code=400):
    if request.wants_json():
        response = jsonify({'message': msg})
        response.status_code = code
        return response
    else:
        flash(msg)
        return redirect(url_for('index'))


@app.route('/js/index.js')
def indexjs():
    resp = make_response(render_template('index.js'))
    resp.headers['Content-Type'] = "application/javascript; charset=utf-8"
    return resp


@app.route('/js/dashboard.js')
def dashboardjs():
    resp = make_response(render_template('dashboard.js'))
    resp.headers['Content-Type'] = "application/javascript; charset=utf-8"
    return resp


@app.errorhandler(403)
def error403(e):
    return render_template('error403.html',
                           CTF_NAME=app.config['CTF_NAME']), 403


@app.errorhandler(404)
def error404(e):
    return render_template('error404.html',
                           CTF_NAME=app.config['CTF_NAME']), 404


@app.errorhandler(500)
def error500(e):
    return render_template('error500.html',
                           CTF_NAME=app.config['CTF_NAME']), 500
