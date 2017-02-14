#!/usr/bin/env python
from random import choice
import argparse
import sys
import flask
import markdown

from game_data import adjatives, people, situations

app = flask.Flask(__name__)

subs = {"M": {
        "{his}": "his",
        "{he}": "he",
        "{he's}": "he's",
        },
        "F": {
        "{his}": "her",
        "{he}": "she",
        "{he's}": "she's",
        },
        "N": {
        "{his}": "its",
        "{he}": "it",
        "{he's}": "it's",
        },
        }

def engender(situation, gender):
    for from_, to in subs[gender].items():
        situation = situation.replace(from_, to)
    return situation

def new_text():
    adj = choice(adjatives)
    person, gender = choice(people)
    situation = engender(choice(situations), gender)
    return markdown.markdown('  '.join([adj, person, situation]))



@app.route("/")
def hello():
    template = open("index.html", "r").read()
    return flask.render_template_string(template, content=new_text())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
