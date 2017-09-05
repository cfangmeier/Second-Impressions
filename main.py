#!/usr/bin/env python
import os

from flask import (url_for, render_template, redirect,
                   flash, session, request)

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

from app import app, db
from app.models import Adjative, Person, Situation, Gender, Combination


def init_db():
    from flask_security.utils import encrypt_password
    from game_data import adjatives, people, situations
    from app import user_datastore, Role
    print("Creating fresh DB")
    for adjative in adjatives:
        obj = Adjative(adjative)
        obj.approved = True
        db.session.add(obj)
    for person, gender in people:
        obj = Person(person, Gender(gender))
        obj.approved = True
        db.session.add(obj)
    for situation in situations:
        obj = Situation(situation)
        obj.approved = True
        db.session.add(obj)
    db.session.commit()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')

        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        try:
            admin_email = os.environ['SI_EMAIL']
        except KeyError:
            admin_email = 'admin@example.com'
        try:
            admin_password = os.environ['SI_PASSWORD']
        except KeyError:
            admin_password = 'admin'

        admin_user = user_datastore.create_user(email=admin_email,
                                                password=encrypt_password(admin_password),
                                                roles=[user_role, super_user_role])
        db.session.add(admin_user)
        db.session.commit()


def pick(l, prevN_name, N=20):
    from random import choice
    from collections import deque
    prevN = deque(session[prevN_name], N)
    while True:
        pick = choice(l)
        if pick.id in prevN:
            continue
        prevN.append(pick.id)
        session[prevN_name] = list(prevN)
        return pick


def new_combination(mode):
    adjatives = Adjative.query.filter(Adjative.approved).all()
    people = Person.query.filter(Person.approved).all()
    situations = Situation.query.filter(Situation.approved).all()
    if 'prevN_adj' not in session:
        session['prevN_adj'] = []
    if 'prevN_sit' not in session:
        session['prevN_sit'] = []
    if 'prevN_per' not in session:
        session['prevN_per'] = []
    person = pick(people, 'prevN_per')
    situation = pick(situations, 'prevN_sit')
    if mode == 'normal':
        return (None, person, situation)
    else:  # 'hard'
        adj = pick(adjatives, 'prevN_adj')
        return (adj, person, situation)


@app.route("/submit-situation", methods=["GET", "POST"])
def submit_situation():
    class SituationForm(FlaskForm):
        submission = TextAreaField('Situation', validators=[DataRequired()])
    form = SituationForm()
    if form.validate_on_submit():
        db.session.add(Situation(form.submission.data))
        db.session.commit()
        flash("Situation sucessfully submitted")
        return redirect(url_for("index"))
    else:
        return render_template('submit.html', form=form)


@app.route("/submit-person", methods=["GET", "POST"])
def submit_person():
    class PersonForm(FlaskForm):
        submission = StringField('Person', validators=[DataRequired()])
    form = PersonForm()
    if form.validate_on_submit():
        db.session.add(Person(form.submission.data, Gender.unknown))
        db.session.commit()
        flash("Person sucessfully submitted")
        return redirect(url_for("index"))
    else:
        return render_template('submit.html', form=form)


# gamemodes = {'easy': ('Easy Mode', 'success'),
mode_infos = {'normal': ('Normal Mode', 'info'),
              'hard': ('Hard Mode', 'danger'),
              }


def vote(adj_id, per_id, sit_id, updn):
    per = Person.query.filter(Person.id == per_id).first()
    sit = Situation.query.filter(Situation.id == sit_id).first()
    if adj_id:
        adj = Adjative.query.filter(Adjative.id == adj_id).first()
        prev_comb = Combination.query.filter((Combination.adjative_id == adj_id) &
                                             (Combination.person_id == per_id) &
                                             (Combination.situation_id == sit_id)).all()
    else:
        adj = None
        prev_comb = Combination.query.filter(Combination.adjative_id.is_(None) &
                                             (Combination.person_id == per_id) &
                                             (Combination.situation_id == sit_id)).all()
    if not prev_comb:
        comb = Combination(adj, per, sit)
        db.session.add(comb)
    else:
        comb = prev_comb[0]
    if updn == 'upvote':
        comb.upvote()
    else:
        comb.downvote()
    db.session.commit()


@app.route('/halloffame')
def halloffame():
    combs = Combination.query.order_by(Combination.netvotes.desc()).limit(30).all()
    return render_template('halloffame.html',
                           combinations=combs)


@app.route('/normal')
def normal():
    action = request.args.get('action', 'new')
    if action in ('upvote', 'downvote'):
        adj_id = session.get('adj_id')
        per_id = session.get('per_id')
        sit_id = session.get('sit_id')
        vote(adj_id, per_id, sit_id, action)
    _, per, sit = new_combination('normal')
    session['adj_id'] = None
    session['per_id'] = per.id
    session['sit_id'] = sit.id
    return render_template('game.html',
                           person=per,
                           situation=sit,
                           gamemode='normal',
                           mode_info=mode_infos['normal'])


@app.route('/hard')
def hard():
    action = request.args.get('action', 'new')
    if action in ('upvote', 'downvote'):
        adj_id = session.get('adj_id')
        per_id = session.get('per_id')
        sit_id = session.get('sit_id')
        vote(adj_id, per_id, sit_id, action)
    adj, per, sit = new_combination('hard')
    session['adj_id'] = adj.id
    session['sit_id'] = sit.id
    session['per_id'] = per.id
    return render_template('game.html',
                           adjative=adj,
                           person=per,
                           situation=sit,
                           gamemode='hard',
                           mode_info=mode_infos['hard'])


@app.route("/")
def index():
    return render_template('index.html', mode_infos=mode_infos)


if __name__ == "__main__":
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    init_db()
    app.run(host="0.0.0.0", port=8080)
