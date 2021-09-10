from openpyxl import load_workbook

from models import Student, Thesis, Employee


class XlsxReader:
    def __init__(self, file):
        self.workbook = load_workbook(filename=f'files/{file}')
        self.worksheet = self.workbook.active

        self.objects_to_read = {}

    def find_starting_row_and_column(self, title):
        for row in self.worksheet.iter_rows(max_row=10):
            for cell in row:
                if cell.value == title:
                    return cell.row, cell.column
        raise Exception

    def read_objects(self):
        for object_class, kwargs in self.objects_to_read.items():
            collection = []
            rows = []
            for attribute, title in kwargs.items():
                starting_row, kwargs[attribute] = self.find_starting_row_and_column(title)
                rows.append(starting_row)

            if len(set(rows)) != 1:
                raise Exception

            row = rows[0] + 1

            while True:
                parameters = {}

                for attribute, column in kwargs.items():
                    parameters[attribute] = self.worksheet.cell(row=row, column=column).value

                if not all(value is None for value in parameters.values()):
                    print(parameters)
                    collection.append(
                        object_class(
                            parameters
                        )
                    )
                    row += 1
                else:
                    class_name = object_class.__name__
                    setattr(self, class_name.lower() if class_name.endswith('s') else class_name.lower() + 's',
                            collection)
                    break


class ThesisReader(XlsxReader):
    def __init__(self, file):
        super().__init__(file)

        self.objects_to_read = {
            Thesis: {
                'topic': 'Dyplom, temat',
                'individual': 'rodzaj rozlicz.',
                'faculty': 'Katedra - promotor',
                'supervisor': 'Dyplom, promotor',
                'reviewer': 'Dyplom, recenzent'
            },
            Student: {
                'name': 'Imię',
                'surname': 'Nazwisko',
                'index': 'Nr albumu'
            }
        }

        self.thesis = []
        self.students = []

        self.read_objects()
        self.assign_thesis()

    def assign_thesis(self):
        for student, thesis in zip(self.students, self.thesis):
            student.thesis = thesis


class EmployeesReader(XlsxReader):
    def __init__(self, file):
        super().__init__(file)
        self.employees = []
        self.read_employees()

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
