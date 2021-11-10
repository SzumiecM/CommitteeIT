import os
import tkinter as tk
from tkinter import filedialog
from xlsx_reader import ThesisReader, EmployeesReader


class Window:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title('CommitteeIT')
        self.master.geometry('800x400')
        self.master.option_add('*Font', 'HoboStd 12')

        self.thesis_file = None
        self.employees_file = None
        self.algorithms = []

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
        self.checkbox_frame = tk.Frame(self.files_frame, bg='black')

        self.banner = tk.Label(
            self.master,
            text='CommitteeIT',
            bg='black',
            fg='white',
            font=('HoboStd', 45)
        )

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

        self.checkbox_heuristic = tk.Checkbutton(
            self.checkbox_frame,
            text='Heuristic Algorithm',
            command=lambda: self.check_changed('heuristic'),
            bg='black',
            fg='white'
        )

        self.checkbox_hybrid = tk.Checkbutton(
            self.checkbox_frame,
            text='Hybrid Algorithm',
            command=lambda: self.check_changed('hybrid'),
            bg='black',
            fg='white'
        )

        self.checkbox_genetic = tk.Checkbutton(
            self.checkbox_frame,
            text='Genetic Algorithm',
            command=lambda: self.check_changed('genetic'),
            bg='black',
            fg='white'
        )

        self.banner.pack(side='top', anchor='center', fill='both')

        self.files_frame.pack(side='top', fill='x')
        self.employees_frame.pack(side='left')
        self.thesis_frame.pack(side='right')

        self.employees_entry.pack(side='top', fill='x')
        self.employees_button.pack(side='top', fill='x')
        self.thesis_entry.pack(side='top', fill='x')
        self.thesis_button.pack(side='top', fill='x')

        self.checkbox_frame.pack(anchor='center', fill='both')
        self.checkbox_heuristic.pack(side='top', anchor='w')
        self.checkbox_hybrid.pack(side='top', anchor='w')
        self.checkbox_genetic.pack(side='top', anchor='w')

    def run(self):
        self.master.mainloop()

    def browse_files(self, file):
        filename = filedialog.askopenfilename(
            initialdir=f'{os.path.dirname(os.path.realpath(__file__))}\\files\\',
            title='Select File',
            filetypes=(('xlsx files', '.xlsx'),)
        )
        setattr(self, f'{file}_file', filename)
        entry = getattr(self, f'{file}_entry')
        entry.delete(0, tk.END)
        entry.insert(0, filename)

    def check_changed(self, algorithm):
        self.algorithms.append(algorithm) if algorithm not in self.algorithms else self.algorithms.remove(algorithm)


Window().run()
