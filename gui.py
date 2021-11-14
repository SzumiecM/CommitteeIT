import os
import tkinter as tk
from tkinter import filedialog, messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from assemblers.assembler import Assembler
from assemblers.genetic_hybrid_assembler import GeneticHybridAssembler
from xlsx_components.xlsx_reader import EmployeesReader, ThesisReader
from assemblers.genetic_only_assembler import GeneticOnlyAssembler
from assemblers.heuristic_assembler import HeuristicAssembler
from multiprocessing import Process, Manager, freeze_support

from xlsx_components.xlsx_writer import XlsxWriter
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
        self.master.geometry('900x714')
        self.master.minsize(750, 714)
        self.master.maxsize(1000, 714)
        self.master.option_add('*Font', 'HoboStd 12')
        self.master.configure(**MASTER_PARAMS)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.assembler_killed = False
        self.assembling = False
        self.window_closed = False
        self.cache = {}
        self.processes = []
        self.queue = Manager().Queue()
        self.listener_thread = Thread(target=self.queue_listener)
        self.listener_thread.start()
        self.assemble_thread = None

        self.thesis_file = None
        self.employees_file = None
        self.algorithms = []

        self.genetic_params_visible = False

        self.files_frame = tk.Frame(self.master, **MASTER_PARAMS)
        self.employees_frame = tk.Frame(self.files_frame, **MASTER_PARAMS)
        self.thesis_frame = tk.Frame(self.files_frame, **MASTER_PARAMS)
        self.checkbox_frame = tk.Frame(self.files_frame, **MASTER_PARAMS)
        self.reader_params_frame = tk.Frame(self.master, **MASTER_PARAMS)
        self.assembler_params_frame = tk.Frame(self.master, **MASTER_PARAMS)
        self.genetic_params_frame = tk.Frame(self.master, **MASTER_PARAMS)

        self.banner = tk.Label(
            self.master,
            text='CommitteeIT',
            font=('HoboStd', 45),
            **MASTER_PARAMS
        )

        self.employees_entry = tk.Entry(
            self.employees_frame,
            text=self.employees_file,
            **PARAM_PARAMS
        )

        self.thesis_entry = tk.Entry(
            self.thesis_frame,
            text=self.thesis_file,
            **PARAM_PARAMS
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
                    command=lambda x=name: self.check_changed(x),
                    **MASTER_PARAMS
                )
            )

        self.reader_params_label = tk.Label(
            self.reader_params_frame,
            text='Reader Params',
            **TITLE_PARAMS
        )

        self.reader_params_entries = {}
        for entry in READER_PARAMS.keys():
            entry_box = tk.Entry()
            entry_box.insert(0, READER_PARAMS[entry]['default'])
            self.reader_params_entries[entry] = (
                tk.Frame(
                    self.reader_params_frame,
                    **PARAM_PARAMS
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **PARAM_PARAMS
                ),
                entry_box
            )

        self.assembler_params_label = tk.Label(
            self.assembler_params_frame,
            text='Assembler Params',
            **TITLE_PARAMS
        )

        self.assembler_params_entries = {}
        for entry in ASSEMBLER_PARAMS.keys():
            entry_box = tk.Entry()
            entry_box.insert(0, ASSEMBLER_PARAMS[entry]['default'])
            self.assembler_params_entries[entry] = (
                tk.Frame(
                    self.assembler_params_frame,
                    **PARAM_PARAMS
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **PARAM_PARAMS
                ),
                entry_box
            )

        self.genetic_params_label = tk.Label(
            self.genetic_params_frame,
            text='Genetic Params',
            **TITLE_PARAMS
        )

        self.genetic_params_entries = {}
        for entry in GENETIC_PARAMS.keys():
            entry_box = tk.Entry()
            entry_box.insert(0, GENETIC_PARAMS[entry]['default'])
            self.genetic_params_entries[entry] = (
                tk.Frame(
                    self.genetic_params_frame,
                    **PARAM_PARAMS
                ),
                tk.Label(
                    text=' '.join(entry.split('_')).title(),
                    **PARAM_PARAMS
                ),
                entry_box
            )

        self.assemble_button = tk.Button(
            self.master,
            text='ASSEMBLE',
            command=self.assemble,
            **BUTTON_PARAMS
        )

        self.assemble_stop_button = tk.Button(
            self.master,
            text='STOP ASSEMBLING',
            command=self.assemble_stop,
            **BUTTON_PARAMS
        )
        self.assemble_stop_button['state'] = 'disabled'

        self.progress = tk.Label(
            self.master,
            **TITLE_PARAMS
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

        self.reader_params_frame.pack(side='top', fill='x')
        self.reader_params_label.pack(side='top', fill='x')
        for frame, label, entry in self.reader_params_entries.values():
            frame.pack(side='top', fill='x')
            label.pack(side='left', in_=frame)
            entry.pack(side='left', in_=frame)

        self.assembler_params_frame.pack(side='top', fill='x')
        self.assembler_params_label.pack(side='top', fill='x')
        for frame, label, entry in self.assembler_params_entries.values():
            frame.pack(side='top', fill='x')
            label.pack(side='left', in_=frame)
            entry.pack(side='left', in_=frame)

        self.assemble_button.pack(side='bottom', fill='x')
        self.assemble_stop_button.pack(side='bottom', fill='x')
        self.progress.pack(side='bottom', fill='x')

    def run(self):
        self.master.mainloop()

    def on_close(self):
        self.queue.put('DONE')
        if self.assembling:
            self.assembler_killed = True
            self.window_closed = True
            for p in self.processes:
                p.kill()
            self.processes = []
            self.assemble_thread.join()

        self.master.destroy()

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
        self.genetic_params_label.pack(side='top', fill='x')
        for frame, label, entry in self.genetic_params_entries.values():
            frame.pack(side='top', fill='x')
            label.pack(side='left', in_=frame)
            entry.pack(side='left', in_=frame)

        self.genetic_params_visible = True

    def hide_genetic_params(self):
        self.genetic_params_frame.pack_forget()
        self.genetic_params_label.pack_forget()
        for frame, label, entry in self.genetic_params_entries.values():
            frame.pack_forget()
            label.pack_forget()
            entry.pack_forget()

        self.genetic_params_visible = False

    def queue_listener(self):
        while True:
            msg = self.queue.get()
            if msg == 'DONE':
                break
            self.cache[msg['assembler_name']] = {**msg}
            self.progress.configure(text=' | '.join(self.cache[name]['progress_msg'] for name in self.cache.keys()))

    def assemble(self):
        self.assemble_thread = Thread(target=self.assemble_in_thread)
        self.assemble_thread.start()
        self.assembling = True

        self.assemble_button['state'] = 'disabled'
        self.assemble_stop_button['state'] = 'normal'

    def assemble_stop(self):
        self.assembler_killed = True
        for p in self.processes:
            p.kill()
        self.processes = []

    def assemble_in_thread(self):
        validated_data = self.validate()

        if not validated_data:
            self.assemble_button['state'] = 'normal'
            self.assemble_stop_button['state'] = 'disabled'
            return

        reader_params, assembler_params, genetic_params = validated_data

        try:
            employee_reader = EmployeesReader(self.employees_entry.get(), **reader_params)
            thesis_reader = ThesisReader(self.thesis_entry.get())

            thesis_reader.map_employees(employee_reader.employees)
        except ValueError as e:
            self.progress.configure(text=e)
            self.assemble_button['state'] = 'normal'
            self.assemble_stop_button['state'] = 'disabled'
            return

        assembler_params['thesis'] = thesis_reader.thesis
        assembler_params['employees'] = employee_reader.employees
        assembler_params['window_queue'] = self.queue

        assemblers = []
        if 'heuristic' in self.algorithms:
            assemblers.append(HeuristicAssembler(**assembler_params))
        if 'hybrid' in self.algorithms:
            assemblers.append(GeneticHybridAssembler(**assembler_params, **genetic_params))
        if 'genetic' in self.algorithms:
            assemblers.append(GeneticOnlyAssembler(**assembler_params, **genetic_params))

        return_dict = Manager().dict()
        self.processes = []
        for assembler in assemblers:
            p = Process(target=assemble_in_process, args=(assembler, return_dict))
            p.start()
            self.processes.append(p)

        for p in self.processes:
            p.join()

        if not self.assembler_killed:
            self.processes = []

        if self.window_closed:
            return

        xlsx_writer = XlsxWriter(self.thesis_entry.get())

        try:
            if self.assembler_killed:
                for assembler in assemblers:
                    if assembler.assembler_name in self.cache.keys():
                        xlsx_writer.write(self.cache[assembler.assembler_name]['best_population'], assembler.assembler_name)
                        self.plot_results(self.cache[assembler.assembler_name], cached=True, **genetic_params)
            else:
                for assembler in assemblers:
                    xlsx_writer.write(return_dict[assembler.assembler_name].populations[0], assembler.assembler_name)
                    self.plot_results(return_dict[assembler.assembler_name])
        except ValueError as e:
            self.progress.configure(text=e)

        self.assembler_killed = False
        self.assembling = False
        self.cache = {}
        self.assemble_button['state'] = 'normal'
        self.assemble_stop_button['state'] = 'disabled'

    @staticmethod
    def plot_results(assembler, cached=False, **kwargs):
        assembler_name = assembler.assembler_name if not cached else assembler['assembler_name']
        if assembler_name not in GENETIC:
            return

        mean_population_score = assembler.mean_population_score if not cached else assembler['mean_population_score']
        best_population_score = assembler.best_population_score if not cached else assembler['best_population_score']
        time_elapsed = assembler.time_elapsed if not cached else assembler['time_elapsed']
        parents_percent = assembler.parents_percent if not cached else kwargs['parents_percent']
        population_mutation_percent = assembler.population_mutation_percent if not cached else kwargs['population_mutation_percent']
        thesis_mutation_percent = assembler.thesis_mutation_percent if not cached else kwargs[
            'thesis_mutation_percent']
        iteration_count = assembler.iteration_count if not cached else assembler['iteration']

        new_window = tk.Toplevel()
        fig = plt.Figure()
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1.0)
        ax = fig.add_subplot(111)

        x = range(iteration_count)
        ax.plot(x, mean_population_score, '-b', label='mean population score')
        ax.plot(x, best_population_score, '-r', label='best population score')
        ax.set_title(f'Population score for {assembler_name} with {time_elapsed}m execution time\n'
                     f'parents: {parents_percent} | mutation percent: {population_mutation_percent} | mutated thesis: {thesis_mutation_percent}')
        fig.text(0.5, 0.04, 'common X', ha='center')
        fig.text(0.04, 0.5, 'common Y', va='center', rotation='vertical')
        ax.legend(loc='upper left')
        canvas.draw()

    def validate(self):
        try:
            self.validate_paths()
        except ValidationError:
            return False

        reader_params = {}
        assembler_params = {}
        genetic_params = {}

        for name, (_, _, entry) in self.reader_params_entries.items():
            value = entry.get()
            validator = READER_PARAMS[name]
            try:
                reader_params[name] = self.validate_param(name, value, validator)
                if name == 'break_time':
                    assembler_params[name] = reader_params[name]
            except ValidationError:
                return False

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

        return reader_params, assembler_params, genetic_params

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


if __name__ == '__main__':
    freeze_support()
    Window().run()

# todo - styles

# todo reward same committee squads
