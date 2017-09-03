#!/usr/bin/env python
import os

from flask import (url_for, render_template, redirect,
                   flash, request, session)

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

from app import app, db
from app.models import Adjative, Person, Situation, Gender


def init_db():
    from flask_security.utils import encrypt_password
    from game_data import adjatives, people, situations
    from app import user_datastore, Role
    db.create_all()
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


def engender(situation, gender):
    if gender == Gender.unknown:
        gender = Gender.male
    subs = {Gender.male: {
            "{his}": "his",
            "{him}": "him",
            "{he}": "he",
            "{he's}": "he's",
            "{himself}": "himself",
            },
            Gender.female: {
            "{his}": "her",
            "{him}": "her",
            "{he}": "she",
            "{he's}": "she's",
            "{himself}": "herself",
            },
            Gender.neutral: {
            "{his}": "its",
            "{him}": "it",
            "{he}": "it",
            "{he's}": "it's",
            "{himself}": "itself",
            }}
    for from_, to in subs[gender].items():
        situation = situation.replace(from_, to)
    return situation


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


def new_text(mode):
    adjatives = Adjative.query.filter(Adjative.approved).all()
    people = Person.query.filter(Person.approved).all()
    situations = Situation.query.filter(Situation.approved).all()
    if 'prevN_adj' not in session:
        session['prevN_adj'] = []
    if 'prevN_sit' not in session:
        session['prevN_sit'] = []
    if 'prevN_per' not in session:
        session['prevN_per'] = []
    adj = pick(adjatives, 'prevN_adj').adjative
    person = pick(people, 'prevN_per')
    name, gender = person.name, person.gender
    situation = engender(pick(situations, 'prevN_sit').situation, gender)
    if mode == 'easy':
        return '  '.join([name, situation])
    else:  # 'hard'
        return '  '.join([adj, name, situation])


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


gamemodes = {'easy': ('Easy Mode', 'success'),
             'hard': ('Hard Mode', 'danger'),
             }


@app.route("/easy")
def easy():
    return render_template('easy.html',
                           content=new_text('easy'),
                           gamemode=gamemodes['easy'])


@app.route("/hard")
def hard():
    return render_template('hard.html',
                           content=new_text('hard'),
                           gamemode=gamemodes['hard'])


@app.route("/")
def index():
    return render_template('index.html', gamemodes=gamemodes)


if __name__ == "__main__":
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        init_db()
        print('Creating initial db')
    else:
        app.run(host="0.0.0.0", port=8080)
