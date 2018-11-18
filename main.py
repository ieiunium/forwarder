import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import signal


class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class Context:
    def __init__(self):
        self.history = []
        self.tabs = []


class AppEntry:
    def __init__(self):
        pass


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.row_index = 2
        self.data = []

    def create_widgets(self):
        self.add_row = tk.Button(self)
        self.add_row["text"] = "add row"
        self.add_row["command"] = self.add_new_row
        self.add_row.grid(row=1, column=1)

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
                entry_data.process = subprocess.Popen(args=command_text, shell=True, stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE, preexec_fn=os.setsid)
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
        checkbutton.grid(row=row, column=1)
        entry = EntryWithPlaceholder(self, 'command')
        entry.grid(row=row, column=2)

        delete_button = tk.Button(self)
        delete_button["text"] = "delete row"
        delete_button["command"] = delele_button_callback
        delete_button.grid(row=row, column=3)

        entry_data.checkbutton = checkbutton
        entry_data.entry = entry
        entry_data.tk_int_var = tk_int_var
        entry_data.row = row
        entry_data.process = None
        entry_data.delete_button = delete_button
        self.data.append(entry_data)

    def add_new_row(self):
        self.row_index = self.row_index + 1
        self.create_line(self.row_index)
        pass

    def delete_message_box_result(self):
        return messagebox.askquestion("Delete", "Are You Sure?", icon='warning')


root = tk.Tk()
root.geometry("400x200")
app = Application(master=root)
app.mainloop()
