import os
basedir = os.path.abspath(os.path.dirname(__file__))
###############################################################################
# WTF CONFIGURATION
###############################################################################
WTF_CSRF_ENABLED = True
SECRET_KEY = 'hJeqWmafXUxEQ3RRSFMkMDyg7'

DATABASE_FILE = 'appdata.sqlite3'
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir, DATABASE_FILE)

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"

SECURITY_POST_LOGIN_VIEW = "/admin"
SECURITY_POST_LOGOUT_VIEW = "/"

# Flask-Security features
SECURITY_REGISTERABLE = False
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
