import tkinter as tk
from xlsx_reader import ThesisReader, EmployeesReader


class Window:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title('CommitteeIT')
        self.master.geometry('800x400')
        self.master.option_add('*Font', 'HoboStd 20')

        # self.font_size = 20
        # self.font_family = 'Hobo Std'
        # self.font = (self.font_size, 'bold')

        self.employees_reader = None
        self.thesis_reader = None

        self.employees = []
        self.thesis = []

        # create employees and thesis frames
        self.employees_frame = tk.Frame(self.master, bg='yellow')
        self.employees_frame.pack(fill='y', anchor='w', side='left')
        self.thesis_frame = tk.Frame(self.master, bg='lime')
        self.thesis_frame.pack(fill='y', anchor='e', side='right')

        # create title labels
        self.label_employees = tk.Label(self.employees_frame, text='Employees', bg='cyan')
        self.label_employees.pack(side='top', fill='x')
        self.label_thesis = tk.Label(self.thesis_frame, text='Thesis', bg='pink')
        self.label_thesis.pack(side='top', fill='x')

        # create read buttons
        self.employees_read_button = tk.Button(self.employees_frame, command=self.read_employees, text='READ',
                                               bg='grey')
        self.employees_read_button.pack(side='bottom', fill='x')
        self.thesis_read_button = tk.Button(self.thesis_frame, command=self.read_thesis, text='READ', bg='orange')
        self.thesis_read_button.pack(side='bottom', fill='x')

        # create input placeholders
        self.employees_file_input = tk.Entry(self.employees_frame, bg='purple')
        self.employees_file_input.insert(0, 'pracownicy.xlsx')
        self.employees_file_input.pack(side='bottom', fill='x')
        self.thesis_file_input = tk.Entry(self.thesis_frame, bg='brown')
        self.thesis_file_input.insert(0, 'prace.xlsx')
        self.thesis_file_input.pack(side='bottom', fill='x')

        # create elements placeholder
        # self.employees_table = tk.Frame(self.employees_frame, bg='grey')
        # self.employees_table.pack(side='bottom', fill='x')
        # self.thesis_table = tk.Frame(self.thesis_frame, bg='grey')
        # self.thesis_table.pack(side='bottom', fill='x')

        # self.employees_list = tk.Frame(self.employees_frame, bg='red')
        # self.employees_list.pack(side='bottom', fill='x')
        self.thesis_list = tk.Frame(self.thesis_frame, bg='red')
        self.thesis_list.pack(side='bottom', fill='x')

        self.employees_list_scroll_bar = tk.Scrollbar(self.employees_frame, orient='vertical')
        self.employees_list_scroll_bar.pack(side='right', fill='y')
        self.employees_canvas = tk.Canvas(self.employees_frame, bg='brown', highlightthickness=0,
                                          yscrollcommand=self.employees_list_scroll_bar.set,
                                          width=300)
        self.employees_list_scroll_bar.config(command=self.employees_canvas.yview)

        self.employees_list = tk.Frame(self.employees_canvas, bg='red')
        # self.employees_list.pack(fill='x')

        self.calendar_frame = tk.Frame(self.master, bg='black')
        self.calendar_frame.pack(fill='both', anchor='w', expand=1)
        self.employees_canvas.pack(fill='both', side='left')

    def read_employees(self):
        self.employees_reader = EmployeesReader(self.employees_file_input.get())
        for employee in self.employees_reader.employees:
            self.employees.append(tk.Button(self.employees_list, text=employee.surname))
            self.employees[-1].pack(side='top', fill='x')

        self.employees_canvas.create_window(0, 0, anchor='nw', window=self.employees_list)
        self.employees_canvas.update_idletasks()
        self.employees_canvas.configure(scrollregion=self.employees_canvas.bbox('all'),
                                        yscrollcommand=self.employees_list_scroll_bar.set)
        # self.employees_canvas.pack(fill='y', side='left')
        self.employees_canvas.pack(fill='both', side='left')

        # self.employees_list.config(yscrollcommand=self.employees_list_scroll_bar.set)

    #     self.employees_canvas.bind("<Configure>", self.OnCanvasConfigure)
    #
    # def OnCanvasConfigure(self, event):
    #     width = 0
    #     # for child in self.sensorsStatsFrame.grid_slaves():
    #     #     width += child.winfo_reqwidth()
    #
    #     self.employees_canvas.itemconfigure(self.employees_list, width=width, height=event.height)

    def read_thesis(self):
        self.thesis_reader = ThesisReader(self.thesis_file_input.get())

    def run(self):
        self.master.mainloop()


Window().run()
