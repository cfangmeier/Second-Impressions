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
