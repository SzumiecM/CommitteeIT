import os
import tkinter as tk
from tkinter import filedialog
from xlsx_reader import ThesisReader, EmployeesReader


class Window:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title('CommitteeIT')
        self.master.geometry('800x400')
        self.master.option_add('*Font', 'HoboStd 10')

        self.thesis_file = None
        self.employees_file = None

        entry_params = {
            'bg': 'pink'
        }
        button_params = {
            'width': 25,
            'height': 2,
            'bg': 'purple'
        }

        self.files_frame = tk.Frame(self.master, bg='yellow')
        self.employees_frame = tk.Frame(self.files_frame)
        self.thesis_frame = tk.Frame(self.files_frame)

        self.employees_entry = tk.Entry(
            self.employees_frame,
            text=self.employees_file,
            **entry_params
        )
        self.employees_entry.insert(0, 'pracownicy.xlsx')
        self.thesis_entry = tk.Entry(
            self.thesis_frame,
            text=self.thesis_file,
            **entry_params
        )
        self.thesis_entry.insert(0, 'prace.xlsx')
        self.employees_button = tk.Button(
            self.employees_frame,
            text='Choose employees file',
            command=lambda: self.browse_files('employees'),
            **button_params
        )
        self.thesis_button = tk.Button(
            self.thesis_frame,
            text='Choose thesis file',
            command=lambda: self.browse_files('thesis'),
            **button_params
        )

        self.files_frame.pack(fill='x', anchor='n')
        self.employees_frame.pack(side='left')
        self.thesis_frame.pack(side='right')

        self.employees_entry.pack(anchor='n', fill='x')
        self.employees_button.pack(anchor='s', fill='x')
        self.thesis_entry.pack(anchor='n', fill='x')
        self.thesis_button.pack(anchor='s', fill='x')

    def run(self):
        self.master.mainloop()

    def browse_files(self, file):
        filename = filedialog.askopenfilename(
            initialdir=f'{os.path.dirname(os.path.realpath(__file__))}\\files\\',
            title='Select File',
            filetypes=(('xlsx files', '.xlsx'),)
        )
        setattr(self, f'{file}_file', filename)
        getattr(self, f'{file}_entry').configure(text=filename)


Window().run()
