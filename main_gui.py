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

        background_label = 'pink'
        background_button = 'purple'

        dimensions_label = {
            'width': 20,
            'height': 4
        }
        dimensions_button = {
            'width': 25,
            'height': 2
        }

        self.files_frame = tk.Frame(self.master, bg='yellow')
        self.employees_frame = tk.Frame(self.files_frame, bg='cyan')
        self.thesis_frame = tk.Frame(self.files_frame, bg='pink')

        self.employees_label = tk.Label(
            self.employees_frame,
            text=self.employees_file,
            bg=background_label,
            **dimensions_label
        )
        self.thesis_label = tk.Label(
            self.thesis_frame,
            text=self.thesis_file,
            bg=background_label,
            **dimensions_label
        )
        self.employees_button = tk.Button(
            self.employees_frame,
            text='Choose employees file',
            command=lambda: self.browse_files('employees'),
            bg=background_button,
            **dimensions_button
        )
        self.thesis_button = tk.Button(
            self.thesis_frame,
            text='Choose thesis file',
            command=lambda: self.browse_files('thesis'),
            bg=background_button,
            **dimensions_button
        )

        # todo create frames with sizable elements
        self.files_frame.pack(fill='x', anchor='n')
        self.employees_frame.pack(side='left')
        self.thesis_frame.pack(side='right')

        self.employees_label.pack(anchor='n')
        self.employees_button.pack(anchor='s')
        self.thesis_label.pack(anchor='n')
        self.thesis_button.pack(anchor='s')

    def run(self):
        self.master.mainloop()

    def browse_files(self, file):
        filename = filedialog.askopenfilename(
            initialdir=f'{os.path.dirname(os.path.realpath(__file__))}\\files\\',
            title='Select File',
            filetypes=(('xlsx files', '.xlsx'),)
        )
        setattr(self, f'{file}_file', filename)
        getattr(self, f'{file}_label').configure(text=filename)


Window().run()
