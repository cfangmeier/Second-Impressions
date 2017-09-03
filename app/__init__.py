from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flaskext.markdown import Markdown
from flask_admin import Admin, helpers
from flask_security import (Security, SQLAlchemyUserDatastore,
                            UserMixin, RoleMixin)

app = Flask(__name__)
app.config.from_object('config')
Markdown(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

admin = Admin(app, name='Second Impressions - Administration',
              template_mode='bootstrap3')

# Setup Flask-Security
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


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@security.context_processor
def security_context_processor():
    '''
    Define a context processor for merging flask-admin's template context into
    the flask-security views.
     '''
    return dict(admin_base_template=admin.base_template,
                admin_view=admin.index_view,
                h=helpers,
                get_url=url_for
                )

# from app import views, models
