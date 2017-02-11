#!/usr/bin/env python
import tkinter as tk
from random import choice
import argparse
import sys
import flask

from game_data import adjatives, people, situations

subs = {"M": {
        "{his}": "his",
        "{he's}": "he's",
        },
        "F": {
        "{his}": "her",
        "{he's}": "she's",
        }}

def engender(situation, gender):
    for from_, to in subs[gender].items():
        situation = situation.replace(from_, to)
    return situation

def new_text():
    adj = choice(adjatives)
    person, gender = choice(people)
    situation = engender(choice(situations), gender)
    return '  '.join([adj, person, situation])


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.create_widgets()
        self.update_text()

    def create_widgets(self):
        self.label = tk.Label(self)
        self.label["text"] = ""
        self.label["font"] = "{courier 10 bold}"
        self.label.pack(side="top")

        self.next = tk.Button(self)
        self.next["text"] = "Next"
        self.next["command"] = self.update_text
        self.next["font"] = "{courier 10 bold}"
        self.next.pack(side="top", fill="both")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit["font"] = "{courier 10 bold}"
        self.quit.pack(side="bottom", fill="x")

    def update_text(self):
        self.label["text"] = new_text()


def start_webapp():
    app = flask.Flask(__name__)

    @app.route("/")
    def hello():
        template = open("index.html", "r").read()
        return flask.render_template_string(template, content=new_text())
    app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action="store_true", help="start in browser")
    args = parser.parse_args(sys.argv[1:])
    if args.w:
        start_webapp()
    else:
        root = tk.Tk()
        app = Application(master=root)
        app.master.title("Second Impressions")
        app.mainloop()
