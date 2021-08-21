from openpyxl import load_workbook

from models import Student, Thesis


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
            topic, supervisor, reviewer, individual = self.worksheet[f'O{row}'].value, \
                                                      self.worksheet[f'D{row}'].value, \
                                                      self.worksheet[f'E{row}'].value, \
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
