import os
import tkinter as tk
from tkinter import filedialog, messagebox
from xlsx_reader import ThesisReader, EmployeesReader

from config import *
from styles import *


class ValidationError(Exception):
    def __init__(self, msg):
        super().__init__()
        messagebox.showerror('ValidationError', msg)


class Window:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title('CommitteeIT')
        self.master.geometry('800x400')
        self.master.option_add('*Font', 'HoboStd 12')

        self.thesis_file = None
        self.employees_file = None
        self.algorithms = []

        self.genetic_params_visible = False

        self.files_frame = tk.Frame(self.master, bg='yellow')
        self.employees_frame = tk.Frame(self.files_frame)
        self.thesis_frame = tk.Frame(self.files_frame)
        self.checkbox_frame = tk.Frame(self.files_frame, bg='black')
        self.assembler_params_frame = tk.Frame(self.master, bg='orange')
        self.genetic_params_frame = tk.Frame(self.master, bg='cyan')

        self.banner = tk.Label(
            self.master,
            text='CommitteeIT',
            font=('HoboStd', 45),
            **BLACK_AND_WHITE
        )

        self.employees_entry = tk.Entry(
            self.employees_frame,
            text=self.employees_file,
            **ENTRY_PARAMS
        )
        self.employees_entry.insert(0, 'pracownicy.xlsx')

        self.thesis_entry = tk.Entry(
            self.thesis_frame,
            text=self.thesis_file,
            **ENTRY_PARAMS
        )
        self.thesis_entry.insert(0, 'prace.xlsx')

        self.employees_button = tk.Button(
            self.employees_frame,
            text='Choose employees file',
            command=lambda: self.browse_files('employees'),
            **BUTTON_PARAMS
        )

        self.thesis_button = tk.Button(
            self.thesis_frame,
            text='Choose thesis file',
            command=lambda: self.browse_files('thesis'),
            **BUTTON_PARAMS
        )

        self.algorithm_checkboxes = []
        for name in ALGORITHMS:
            self.algorithm_checkboxes.append(
                tk.Checkbutton(
                    self.checkbox_frame,
                    text=f'{name.capitalize()} Algorithm',
                    command=lambda x=name: self.check_changed(x)
                )
            )

        self.assembler_params_entries = {}
        for entry in ASSEMBLER_PARAMS.keys():
            self.assembler_params_entries[entry] = (
                tk.Frame(
                    self.assembler_params_frame,
                    bg='black'
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **BLACK_AND_WHITE
                ),
                tk.Entry()
            )

        self.genetic_params_entries = {}
        for entry in GENETIC_PARAMS.keys():
            self.genetic_params_entries[entry] = (
                tk.Frame(
                    self.genetic_params_frame,
                    bg='black'
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **BLACK_AND_WHITE
                ),
                tk.Entry()
            )

        self.assemble_button = tk.Button(
            self.master,
            text='ASSEMBLE',
            command=self.assemble,
            **BUTTON_PARAMS
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
        for checkbox in self.algorithm_checkboxes:
            checkbox.pack(side='top', anchor='w')

        self.assembler_params_frame.pack(side='top', fill='x')
        for frame, label, entry in self.assembler_params_entries.values():
            frame.pack(side='top', fill='x')
            label.pack(side='left', in_=frame)
            entry.pack(side='left', in_=frame)

        self.assemble_button.pack(side='bottom', fill='x')

    def run(self):
        self.master.mainloop()

    def browse_files(self, file):
        filename = filedialog.askopenfilename(
            initialdir=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files'),
            title='Select File',
            filetypes=(('xlsx files', '.xlsx'),)
        )
        setattr(self, f'{file}_file', filename)
        entry = getattr(self, f'{file}_entry')
        entry.delete(0, tk.END)
        entry.insert(0, filename)

    def check_changed(self, algorithm):
        self.algorithms.append(algorithm) if algorithm not in self.algorithms else self.algorithms.remove(algorithm)
        self.banner.configure(text=''.join(self.algorithms))

        if algorithm in GENETIC and not self.genetic_params_visible:
            self.show_genetic_params()
        elif all(x not in self.algorithms for x in GENETIC) and self.genetic_params_visible:
            self.hide_genetic_params()

    def show_genetic_params(self):
        self.genetic_params_frame.pack(side='top', fill='x')
        for frame, label, entry in self.genetic_params_entries.values():
            frame.pack(side='top', fill='x')
            label.pack(side='left', in_=frame)
            entry.pack(side='left', in_=frame)

        self.genetic_params_visible = True

    def hide_genetic_params(self):
        self.genetic_params_frame.pack_forget()
        for frame, label, entry in self.genetic_params_entries.values():
            frame.pack_forget()
            label.pack_forget()
            entry.pack_forget()

        self.genetic_params_visible = False

    def assemble(self):
        self.validate()

    def validate(self):
        for name, (_, _, entry) in self.assembler_params_entries.items():
            value = entry.get()
            validator = ASSEMBLER_PARAMS[name]
            try:
                self.validate_param(name, value, validator)
            except ValidationError:
                return

        if self.genetic_params_visible:
            for name, (_, _, entry) in self.genetic_params_entries.items():
                value = entry.get()
                validator = GENETIC_PARAMS[name]
                try:
                    self.validate_param(name, value, validator)
                except ValidationError:
                    return

    @staticmethod
    def validate_param(name, value, validator):
        if validator['type'] == int:
            if not value.isdigit():
                raise ValidationError(f'{name} must be int')
        elif validator['type'] == float:
            try:
                float(value)
            except ValueError:
                raise ValidationError(f'{name} must be float')

        if validator.get('min'):
            if float(value) < validator['min']:
                raise ValidationError(f'Min value of {name} is {validator["min"]}')

        if validator.get('max'):
            if float(value) > validator['max']:
                raise ValidationError(f'Max value of {name} is {validator["max"]}')


if __name__ == '__main__':
    Window().run()
