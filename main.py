import time
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import signal
import json

HISTORY_FILE = "history.txt"

DATA_JSON_FILE_NAME = 'data.json'


class AppEntry:
    def __init__(self):
        self.checkbutton = None
        self.entry = None
        self.tk_int_var = None
        self.row = None
        self.process = None
        self.delete_button = None


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.columnconfigure(2, weight=1)
        self.row_index = 2
        self.data = []
        self.create_widgets()
        self.history_appender = open(HISTORY_FILE, "a+")

    def create_widgets(self):
        self.add_row = tk.Button(self)
        self.add_row["text"] = "add row"
        self.add_row["command"] = self.add_new_row
        self.add_row.grid(row=1, column=1,sticky=tk.W+tk.E+tk.N+tk.S)

        self.save_button = tk.Button(self)
        self.save_button["text"] = "save tabs"
        self.save_button["command"] = self.save_tabs
        self.save_button.grid(row=1, column=2,sticky=tk.W+tk.E+tk.N+tk.S)

        with open(DATA_JSON_FILE_NAME, "r") as read_file:
            data = json.load(read_file)
            for item in data:
                entry = self.add_new_row().entry
                entry.delete(0, tk.END)
                entry.insert(0, item)

    def create_line(self, row):
        entry_data = AppEntry()

        def process_wait():
            if entry_data.process is not None:
                entry_data.process.wait()

        def kill_process():
            if entry_data.process is not None:
                os.killpg(os.getpgid(entry_data.process.pid), signal.SIGTERM)
                entry_data.process = None

        def check_box_callback():
            if entry_data.tk_int_var.get() == 1 and entry_data.process is None:
                command_text = entry_data.entry.get()
                self.history_appender.write(command_text + "\r\n")
                self.history_appender.flush()
                timestamp = str(int(time.time()))
                entry_data.process = subprocess.Popen(
                    args="bash ./loop.sh " + command_text + " > " + timestamp + ".log 2>&1",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid)
                threading.Thread(target=process_wait).start()

            elif entry_data.tk_int_var.get() == 0 and entry_data.process is not None:
                threading.Thread(target=kill_process).start()

            print(entry_data)
            print(entry_data.tk_int_var.get())
            print(entry_data.row)
            print(entry_data.entry.get())

        def delele_button_callback():
            if self.delete_message_box_result() == "yes":
                kill_process()
                entry_data.checkbutton.grid_remove()
                entry_data.entry.grid_remove()
                entry_data.delete_button.grid_remove()
                self.data.remove(entry_data)

        tk_int_var = tk.IntVar()
        checkbutton = tk.Checkbutton(master=self, command=check_box_callback, variable=tk_int_var)
        checkbutton.grid(row=row, column=1,sticky=tk.W+tk.E+tk.N+tk.S)
        entry = tk.Entry(self)
        entry.grid(row=row, column=2,sticky=tk.W+tk.E+tk.N+tk.S)

        delete_button = tk.Button(self)
        delete_button["text"] = "delete row"
        delete_button["command"] = delele_button_callback
        delete_button.grid(row=row, column=3,sticky=tk.W+tk.E+tk.N+tk.S)

        entry_data.checkbutton = checkbutton
        entry_data.entry = entry
        entry_data.tk_int_var = tk_int_var
        entry_data.row = row
        entry_data.process = None
        entry_data.delete_button = delete_button
        self.data.append(entry_data)
        return entry_data

    def add_new_row(self):
        self.row_index = self.row_index + 1
        return self.create_line(self.row_index)

    def delete_message_box_result(self):
        return messagebox.askquestion("Delete", "Are You Sure?", icon='warning')

    def save_tabs(self):
        dump = list(map(lambda x: x.entry.get(), self.data))
        with open(DATA_JSON_FILE_NAME, 'w') as outfile:
            json.dump(dump, outfile)


root = tk.Tk()
root.geometry("800x200")
app = Application(master=root)
app.pack(fill="x",expand=True)
app.mainloop()
