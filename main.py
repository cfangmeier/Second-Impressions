#!/usr/bin/python
import tkinter as tk
from random import choice

from game_data import adjatives, people, situations


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

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
        text = '  '.join([choice(adjatives),
                         choice(people),
                         choice(situations)])
        self.label["text"] = text


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.master.title("Second Impressions")
    app.mainloop()
