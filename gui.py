import os
import tkinter as tk
from tkinter import filedialog, messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from assemblers.assembler import Assembler
from assemblers.genetic_hybrid_assembler import GeneticHybridAssembler
from xlsx_reader import EmployeesReader, ThesisReader
from assemblers.genetic_only_assembler import GeneticOnlyAssembler
from assemblers.heuristic_assembler import HeuristicAssembler
from multiprocessing import Process, Manager

from xlsx_writer import XlsxWriter
from threading import Thread

from config import *
from styles import *


def assemble_in_process(assembler: Assembler, return_dict):
    assembler.assemble()
    return_dict[assembler.assembler_name] = assembler


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

        self.thesis_entry = tk.Entry(
            self.thesis_frame,
            text=self.thesis_file,
            **ENTRY_PARAMS
        )

        employees_file, thesis_file = self.check_default_files()
        self.employees_entry.insert(0, employees_file)
        self.thesis_entry.insert(0, thesis_file)

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
            entry_box = tk.Entry()
            entry_box.insert(0, ASSEMBLER_PARAMS[entry]['default'])
            self.assembler_params_entries[entry] = (
                tk.Frame(
                    self.assembler_params_frame,
                    bg='black'
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **BLACK_AND_WHITE
                ),
                entry_box
            )

        self.genetic_params_entries = {}
        for entry in GENETIC_PARAMS.keys():
            entry_box = tk.Entry()
            entry_box.insert(0, GENETIC_PARAMS[entry]['default'])
            self.genetic_params_entries[entry] = (
                tk.Frame(
                    self.genetic_params_frame,
                    bg='black'
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **BLACK_AND_WHITE
                ),
                entry_box
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

    @staticmethod
    def check_default_files():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        default_employees_file = os.path.join(current_dir, 'files', DEFAULT_EMPLOYEES_FILE)
        default_thesis_file = os.path.join(current_dir, 'files', DEFAULT_THESIS_FILE)
        employees_starting_file = ''
        thesis_starting_file = ''

        if os.path.isfile(default_employees_file):
            employees_starting_file = default_employees_file
        if os.path.isfile(default_thesis_file):
            thesis_starting_file = default_thesis_file

        return employees_starting_file, thesis_starting_file

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
        t = Thread(target=self.assemble_in_thread)
        t.start()

        self.assemble_button['state'] = 'disabled'

    def assemble_in_thread(self):
        validated_data = self.validate()

        if not validated_data:
            return

        employee_reader = EmployeesReader(self.employees_entry.get())
        thesis_reader = ThesisReader(self.thesis_entry.get())

        thesis_reader.map_employees(employee_reader.employees)

        assembler_params, genetic_params = validated_data

        assembler_params['thesis'] = thesis_reader.thesis
        assembler_params['employees'] = employee_reader.employees

        assemblers = []
        if 'heuristic' in self.algorithms:
            assemblers.append(HeuristicAssembler(**assembler_params))
        if 'hybrid' in self.algorithms:
            assemblers.append(GeneticHybridAssembler(**assembler_params, **genetic_params))
        if 'genetic' in self.algorithms:
            assemblers.append(GeneticOnlyAssembler(**assembler_params, **genetic_params))

        return_dict = Manager().dict()
        processes = []
        for assembler in assemblers:
            p = Process(target=assemble_in_process, args=(assembler, return_dict))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        xlsx_writer = XlsxWriter(self.thesis_entry.get())
        for assembler in assemblers:
            xlsx_writer.write(return_dict[assembler.assembler_name].populations[0])
            self.plot_results(return_dict[assembler.assembler_name])

        self.assemble_button['state'] = 'normal'

    @staticmethod
    def plot_results(assembler):
        new_window = tk.Toplevel()
        fig = plt.Figure()
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1.0)
        ax = fig.add_subplot(111)

        x = range(assembler.iteration_count)
        ax.plot(x, assembler.mean_population_score, '-b', label='mean population score')
        ax.plot(x, assembler.best_population_score, '-r', label='best population score')
        ax.set_title(f'Population score for {assembler.assembler_name} with {assembler.time_elapsed}m execution time\n'
                     f'parents: {assembler.parents_percent} | mutation percent: {assembler.population_mutation_percent} | mutated thesis: {assembler.thesis_mutation_percent}')
        fig.text(0.5, 0.04, 'common X', ha='center')
        fig.text(0.04, 0.5, 'common Y', va='center', rotation='vertical')
        ax.legend(loc='upper left')
        canvas.draw()

    def validate(self):
        try:
            self.validate_paths()
        except ValidationError:
            return False

        assembler_params = {}
        genetic_params = {}

        for name, (_, _, entry) in self.assembler_params_entries.items():
            value = entry.get()
            validator = ASSEMBLER_PARAMS[name]
            try:
                assembler_params[name] = self.validate_param(name, value, validator)
            except ValidationError:
                return False

        if self.genetic_params_visible:
            for name, (_, _, entry) in self.genetic_params_entries.items():
                value = entry.get()
                validator = GENETIC_PARAMS[name]
                try:
                    genetic_params[name] = self.validate_param(name, value, validator)
                except ValidationError:
                    return False

        return assembler_params, genetic_params

    def validate_paths(self):
        if not os.path.isfile(self.employees_entry.get()) or not self.employees_entry.get().endswith('.xlsx'):
            raise ValidationError('Wrong employees file chosen.')
        elif not os.path.isfile(self.thesis_entry.get()) or not self.thesis_entry.get().endswith('.xlsx'):
            raise ValidationError('Wrong thesis file chosen.')

    @staticmethod
    def validate_param(name, value, validator):
        if validator['type'] == bool:
            if not value.isdigit() or not int(value) in (1, 0):
                raise ValidationError(f'{name} should be set to either 0 or 1')
            value = bool(int(value))
        if validator['type'] == int:
            if not value.isdigit():
                raise ValidationError(f'{name} must be int')
            value = int(value)
        elif validator['type'] == float:
            try:
                float(value)
            except ValueError:
                raise ValidationError(f'{name} must be float')
            value = float(value)

        if validator.get('min'):
            if value < validator['min']:
                raise ValidationError(f'Min value of {name} is {validator["min"]}')

        if validator.get('max'):
            if value > validator['max']:
                raise ValidationError(f'Max value of {name} is {validator["max"]}')

        return value

    @staticmethod
    def assemble_in_process(assembler: Assembler, return_dict):
        assembler.assemble()
        return_dict[assembler.assembler_name] = assembler


if __name__ == '__main__':
    Window().run()

# radiobutton for bools - considered, might not be that good of an idea after all
# todo - styles
# todo - store last results, allow manual write

# todo - add stop option with last best results save
# https://stackoverflow.com/questions/32930120/retrieve-a-value-from-subprocess-after-kill

# todo - configure weights
# todo - get_by_repr -> get_by_id (might cause little speedup)
# todo - terminate processes on windows close
