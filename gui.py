import tkinter as tk


class Window:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title('CommitteeIT')
        self.master.geometry('600x400')
        self.master.option_add('*Font', 'HoboStd 20')

        # self.font_size = 20
        # self.font_family = 'Hobo Std'
        # self.font = (self.font_size, 'bold')

        self.thesis_file = None
        self.employees_file = None

        frame_element_kwargs = {'side': 'bottom', 'fill': 'x'}

        self.employees_frame = tk.Frame(self.master, bg='yellow')
        self.employees_frame.pack(fill='y', anchor='w', side='left')
        self.thesis_frame = tk.Frame(self.master, bg='lime')
        self.thesis_frame.pack(fill='y', anchor='e', side='right')

        self.label_employees = tk.Label(self.employees_frame, text='Employees', bg='cyan')
        self.label_employees.pack(side='top', fill='x')
        self.label_thesis = tk.Label(self.thesis_frame, text='Thesis', bg='pink')
        self.label_thesis.pack(side='top', fill='x')

        self.employees_read_button = tk.Button(self.employees_frame, text='READ', bg='grey')
        self.employees_read_button.pack(side='bottom', fill='x')
        self.thesis_read_button = tk.Button(self.thesis_frame, text='READ', bg='orange', fontsize=5)
        self.thesis_read_button.pack(side='bottom', fill='x')

        self.employees_file_input = tk.Entry(self.employees_frame, bg='purple')
        self.employees_file_input.pack(side='bottom', fill='x')
        self.thesis_file_input = tk.Entry(self.thesis_frame, bg='brown')
        self.thesis_file_input.pack(side='bottom', fill='x')

    def run(self):
        self.master.mainloop()


Window().run()
