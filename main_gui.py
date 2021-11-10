import os
import tkinter as tk
from tkinter import filedialog
from xlsx_reader import ThesisReader, EmployeesReader

ALGORITHMS = ('heuristic', 'hybrid', 'genetic')
GENETIC = ('hybrid', 'genetic')
ASSEMBLER_PARAMS = ('employees_per_slot', 'population_count', 'max_slots_per_employee', 'max_thesis_per_slot')
GENETIC_PARAMS = ('iteration_count', 'parents_percent', 'population_mutation_percent', 'thesis_mutation_percent')


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

        entry_params = {
            'bg': 'pink'
        }
        button_params = {
            'width': 25,
            'height': 2,
            'bg': 'purple'
        }
        black_and_white = {
            'bg': 'black',
            'fg': 'white'
        }

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
            **black_and_white
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
        for entry in ASSEMBLER_PARAMS:
            self.assembler_params_entries[entry] = (
                tk.Frame(
                    self.assembler_params_frame,
                    bg='black'
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **black_and_white
                ),
                tk.Entry()
            )

        self.genetic_params_entries = {}
        for entry in GENETIC_PARAMS:
            self.genetic_params_entries[entry] = (
                tk.Frame(
                    self.genetic_params_frame,
                    bg='black'
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **black_and_white
                ),
                tk.Entry()
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


Window().run()
