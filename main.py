#!/usr/bin/python

import tkinter as tk
from random import choice
import json


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.people = self.load_json("people.json")
        self.adjatives = self.load_json("adjatives.json")
        self.situations = self.load_json("situations.json")

    def load_json(self, filename):
        with open(filename) as file_:
            return json.load(file_)

    def create_widgets(self):
        self.next = tk.Button(self)
        self.next["text"] = "Next"
        self.next["command"] = self.update_text
        self.next.pack(side="top")

        self.label = tk.Label(self)
        self.label["text"] = ""
        self.label["font"] = "{courier 10 bold}"
        self.label.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.pack(side="bottom")

    def update_text(self):
        text = '  '.join([choice(self.adjatives),
                         choice(self.people),
                         choice(self.situations)])
        self.label["text"] = text


root = tk.Tk()
app = Application(master=root)
app.master.title("Second Impressions")
app.master.minsize(800, 300)
app.mainloop()
