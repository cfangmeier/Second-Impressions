#!/usr/bin/env python
from random import choice
import argparse
import sys
from datetime import datetime
from flask import Flask, url_for, render_template_string, redirect, flash, request
from flaskext.markdown import Markdown
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from game_data import adjatives, people, situations

app = Flask(__name__)
app.config.from_object("config")
Markdown(app)

subs = {"M": {
        "{his}": "his",
        "{him}": "him",
        "{he}": "he",
        "{he's}": "he's",
        },
        "F": {
        "{his}": "her",
        "{him}": "her",
        "{he}": "she",
        "{he's}": "she's",
        },
        "N": {
        "{his}": "its",
        "{him}": "it",
        "{he}": "it",
        "{he's}": "it's",
        },
        }

SUBMITTED_SITUATIONS_FILE = "situations.txt"
SUBMITTED_PEOPLE_FILE = "people.txt"

def engender(situation, gender):
    for from_, to in subs[gender].items():
        situation = situation.replace(from_, to)
    return situation

def new_text():
    adj = choice(adjatives)
    person, gender = choice(people)
    situation = engender(choice(situations), gender)
    return '  '.join([adj, person, situation])

class SituationForm(FlaskForm):
    submission = StringField('Situation', validators=[DataRequired()])

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
        with open(SUBMITTED_SITUATIONS_FILE, "a") as f:
            f.write(fmt_submission(form.submission.data))
            flash("Situtation sucessfully submitted")
        return redirect(url_for("index"));
    else:
        template = open("submit.html", "r").read()
        return render_template_string(template, form=form)

@app.route("/submit-person", methods=["GET", "POST"])
def submit_person():
    form = PersonForm()
    if form.validate_on_submit():
        with open(SUBMITTED_PEOPLE_FILE, "a") as f:
            f.write(fmt_submission(form.submission.data))
            flash("Person sucessfully submitted")
        return redirect(url_for("index"));
    else:
        template = open("submit.html", "r").read()
        return render_template_string(template, form=form)

@app.route("/")
@app.route("/index.html")
def index():
    template = open("index.html", "r").read()
    return render_template_string(template, content=new_text())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
