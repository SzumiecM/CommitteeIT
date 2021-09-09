from openpyxl import load_workbook

from models import Student, Thesis, Employee


# todo ulepszyć ewentualnie, bo nie podoba mi się to całkowicie
def read_objects(worksheet, row, collection, model, **kwargs):
    while True:
        parameters = {}
        for object, column in kwargs.items():
            parameters[object] = worksheet[''.join([column, row])].value

        if None not in kwargs.values():
            collection.append(model(parameters))
            row += 1
        else:
            break

    return collection


class XlsxReader:
    def __init__(self, file):
        self.workbook = load_workbook(filename=f'files/{file}')
        self.worksheet = self.workbook.active

        # todo zrobić taki ogólny reader po którym będzie reszta dziedziczyła


class ThesisReader(XlsxReader):
    def __init__(self, file):
        super().__init__(file)

        self.thesis = []
        self.students = []

        self.read_thesis()
        self.read_students()
        self.assign_thesis()

    def read_thesis(self):
        row = 2
        while True:
            topic, supervisor, reviewer, faculty, individual = self.worksheet[f'O{row}'].value, \
                                                               self.worksheet[f'D{row}'].value, \
                                                               self.worksheet[f'E{row}'].value, \
                                                               self.worksheet[f'C{row}'].value, \
                                                               True if self.worksheet[f'F{row}'].value == 'Pojedyncza' else False

            if topic and supervisor and reviewer and individual:
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
        self.read_employees()
        # self.read_slots()
        # self.rea

    def read_employees(self):
        row = 6
        while True:
            surname_and_name, tenure = self.worksheet[f'B{row}'].value, \
                                       True if self.worksheet[f'C{row}'].value == 'tak' else False

            surname_and_name = [x.capitalize() for x in surname_and_name.split(' ')]

            online_slots, stationary_slots = self.read_slots(row)

            availabilty = {
                'day1': self.worksheet[f'F{row}'].value,
                'day2': self.worksheet[f'G{row}'].value,
                'day3': self.worksheet[f'H{row}'].value,
                'day4': self.worksheet[f'I{row}'].value,
            }

            if len(surname_and_name) == 2:
                self.employees.append(Employee(
                    name=surname_and_name[1],
                    surname=surname_and_name[0],
                    tenure=tenure,
                    online_slots=online_slots,
                    stationary_slots=stationary_slots,
                    availability=availabilty
                ))
                row += 1
            else:
                break

    def read_slots(self, row):
        online_slots, stationary_slots = self.worksheet[f'D{row}'].value, \
                                      self.worksheet[f'E{row}'].value

        online_slots = online_slots.split('; ') if online_slots else None
        stationary_slots = stationary_slots.split('; ') if stationary_slots else None

        return online_slots, stationary_slots

    def read_availability(self, row):
        pass
