import enum
from datetime import datetime

from flask import redirect, abort, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user

from app import db, admin


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

    def engender(self, gender):
        situation = self.situation
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


class Combination(db.Model):
    __tablename__ = 'combination'
    __table_args__ = (db.Index('comb_idx', 'adjative_id', 'person_id', 'situation_id'), )
    id = db.Column(db.Integer, primary_key=True)

    adjative_id = db.Column(db.Integer, db.ForeignKey('adjative.id'))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    situation_id = db.Column(db.Integer, db.ForeignKey('situation.id'))

    adjative = db.relationship('Adjative', backref='combinations')
    person = db.relationship('Person', backref='combinations')
    situation = db.relationship('Situation', backref='combinations')

    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    netvotes = db.Column(db.Integer)

    def __init__(self, adjative, person, situation):
        self.adjative = adjative
        self.person = person
        self.situation = situation
        self.upvotes = 0
        self.downvotes = 0
        self.netvotes = 0

    def upvote(self):
        self.upvotes += 1
        self.netvotes = self.upvotes - self.downvotes

    def downvote(self):
        self.downvotes += 1
        self.netvotes = self.upvotes - self.downvotes

    def __repr__(self):
        fmt = '<Combination: adjative:{}, person:{}, situation:{}, netvotes:{}>'
        return fmt.format(self.adjative_id, self.person_id, self.situation_id, self.netvotes)

    def to_str(self):
        return str(self)

    def __str__(self):
        if self.adjative:
            return ' '.join([self.adjative.adjative,
                             self.person.name,
                             self.situation.engender(self.person.gender)])
        else:
            return ' '.join([self.person.name,
                             self.situation.engender(self.person.gender)])


db.create_all()
