from openpyxl import load_workbook

from models import Student, Thesis, CommitteeMember


class XlsxReader:
    def __init__(self, file):
        self.workbook = load_workbook(filename=f'files/{file}')
        self.worksheet = self.workbook.active


class ThesisReader(XlsxReader):
    def __init__(self, file):
        super().__init__(file)

        self.thesis = []
        self.students = []

    def read_thesis(self):
        row = 2
        while True:
            topic, supervisor, reviewer, faculty, individual = self.worksheet[f'O{row}'].value, \
                                                               self.worksheet[f'D{row}'].value, \
                                                               self.worksheet[f'E{row}'].value, \
                                                               self.worksheet[f'C{row}'].value, \
                                                               True if self.worksheet[f'F{row}'].value == 'Pojedyncza' else False


            if topic and supervisor and reviewer:
                self.thesis.append(Thesis(
                    topic=topic,
                    supervisor=supervisor,
                    reviewer=reviewer,
                    individual=individual
                ))
                row += 1
            else:
                break

    def read_students(self):
        row = 2
        while True:
            surname, name, index = self.worksheet[f'A{row}'].value, \
                                   self.worksheet[f'B{row}'].value, \
                                   self.worksheet[f'P{row}'].value

            if surname and name and index:
                self.students.append(Student(
                    name=name,
                    surname=surname,
                    index=index
                ))
                row += 1
            else:
                break

    def assign_thesis(self):
        for student, thesis in zip(self.students, self.thesis):
            student.thesis = thesis


class EmployeesReader(XlsxReader):
    def __init__(self, file):
        super().__init__(file)

        self.employees = []

    def read_employees(self):
        row = 6
        while True:
            surname_and_name, tenure = self.worksheet[f'B{row}'].value, \
                                       True if self.worksheet[f'C{row}'].value == 'tak' else False

            surname_and_name = [x.capitalize() for x in surname_and_name.split(' ')]

            if len(surname_and_name) == 2:
                self.employees.append(CommitteeMember(
                    name=surname_and_name[1],
                    surname=surname_and_name[0],
                    tenure=tenure
                ))
                row += 1
            else:
                break

    def read_slots(self, row):
        online_slots, offline_slots = self.worksheet[f'D{row}'].value, \
                                      self.worksheet[f'E{row}'].value

        online_slots = online_slots.split('; ')
        offline_slots = offline_slots.split('; ')

        return online_slots, offline_slots

    def read_availability(self, row):
        pass

    def debug_employees(self):
        for employee in self.employees:
            print(employee.name + employee.surname + str(employee.tenure))

#     def debug_students(self):
#         for student in self.students:
#             print(student.thesis.topic)
#             print(student.thesis.individual)
#
#
# x = ThesisReader('prace złożone 15.01.2021_egz dypl_21-26.01.2021.xlsx')
x = EmployeesReader('IT lista-pracownicy_dostępność.xlsx')
# x.read_students()
# x.read_thesis()
# x.assign_thesis()
#
# x.debug_students()
x.read_employees()
x.debug_employees()
