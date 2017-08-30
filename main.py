#!/usr/bin/env python
from random import choice
import enum
import os
from datetime import datetime
from flask import (Flask, url_for, render_template_string, redirect,
                   flash, request, abort)
from flaskext.markdown import Markdown
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import helpers as admin_helpers

from flask_security import (Security, SQLAlchemyUserDatastore,
                            UserMixin, RoleMixin, current_user)
from flask_security.utils import encrypt_password

app = Flask(__name__)
app.config.from_object("config")
Markdown(app)

db = SQLAlchemy(app)

admin = Admin(app, name='Second Impressions - Administration',
              template_mode='bootstrap3')


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class RestrictedView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('superuser'):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is
        not accessible.
        """
        print(current_user)
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class Gender(enum.Enum):
    male = 'M'
    female = 'F'
    neutral = 'N'
    unknown = 'U'


class Adjative(db.Model):
    __tablename__ = 'adjative'
    id = db.Column(db.Integer, primary_key=True)
    adjative = db.Column(db.String)
    approved = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __init__(self, adjative):
        self.adjative = adjative
        self.approved = False
        self.timestamp = datetime.now()

    def __repr__(self):
        return '<Adjative: {}, {}>'.format(self.adjative,
                                           self.approved)


class AdjativeView(RestrictedView):
    page_size = 100
    column_editable_list = ['adjative', 'approved']


class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    gender = db.Column(db.Enum(Gender))
    approved = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        self.approved = False
        self.timestamp = datetime.now()

    def __repr__(self):
        return '<Person: {}({}), {}>'.format(self.name,
                                             self.gender,
                                             self.approved)


class PersonView(RestrictedView):
    page_size = 100
    column_editable_list = ['approved', 'gender', 'name']


class Situation(db.Model):
    __tablename__ = 'situation'
    id = db.Column(db.Integer, primary_key=True)
    situation = db.Column(db.String)
    approved = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __init__(self, situation):
        self.situation = situation
        self.approved = False
        self.timestamp = datetime.now()

    def __repr__(self):
        sit = self.situation
        if len(self.situation) > 20:
            sit = sit[:18]+'...'
        return '<Situation: {}, {}>'.format(sit, self.approved)


class SituationView(RestrictedView):
    page_size = 100
    column_editable_list = ['situation', 'approved']


admin.add_view(AdjativeView(Adjative, db.session))
admin.add_view(PersonView(Person, db.session))
admin.add_view(SituationView(Situation, db.session))


@security.context_processor
def security_context_processor():
    '''
    Define a context processor for merging flask-admin's template context into
    the flask-security views.
     '''
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
        )


def init_db():
    from game_data import adjatives, people, situations
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

        admin_user = user_datastore.create_user(
                email=admin_email,
                password=encrypt_password(admin_password),
                roles=[user_role, super_user_role]
        )
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
            },
            }
    for from_, to in subs[gender].items():
        situation = situation.replace(from_, to)
    return situation

def pick(l, prev20):
    if len(l) <=20:
        return choice(l)
    while True:
        pick = choice(l)
        if l in prev20:
            continue
        if len(prev20)>=20:
            prev20.pop()
        prev20.insert(0, pick)
        return pick

prev20_adj = []
prev20_sit = []
prev20_per = []

def new_text():
    adjatives = Adjative.query.filter(Adjative.approved).all()
    people = Person.query.filter(Person.approved).all()
    situations = Situation.query.filter(Situation.approved).all()
    adj = pick(adjatives, prev20_adj).adjative
    person = pick(people, prev20_per)
    name, gender = person.name, person.gender
    situation = engender(pick(situations, prev20_sit).situation, gender)
    return '  '.join([adj, name, situation])


class SituationForm(FlaskForm):
    submission = TextAreaField('Situation', validators=[DataRequired()])


class PersonForm(FlaskForm):
    submission = StringField('Person', validators=[DataRequired()])


def fmt_submission(sub):
    return ("{} FROM {}: \n{}\n"
            "======================="
            "\n").format(datetime.now(), request.remote_addr, sub)


@app.route("/submit-situation", methods=["GET", "POST"])
def submit_situation():
    form = SituationForm()
    if form.validate_on_submit():
        db.session.add(Situation(form.submission.data))
        db.session.commit()
        flash("Situation sucessfully submitted")
        return redirect(url_for("index"))
    else:
        template = open("submit.html", "r").read()
        return render_template_string(template, form=form)


@app.route("/submit-person", methods=["GET", "POST"])
def submit_person():
    form = PersonForm()
    if form.validate_on_submit():
        db.session.add(Person(form.submission.data, Gender.unknown))
        db.session.commit()
        flash("Person sucessfully submitted")
        return redirect(url_for("index"))
    else:
        template = open("submit.html", "r").read()
        return render_template_string(template, form=form)


@app.route("/")
def index():
    template = open("index.html", "r").read()
    return render_template_string(template, content=new_text())


if __name__ == "__main__":
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        init_db()
        print('Creating initial db')
    else:
        app.run(host="0.0.0.0", port=8080)
