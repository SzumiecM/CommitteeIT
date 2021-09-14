from typing import List


class Person:
    def __init__(self, name: str, surname: str):
        self.name = name
        self.surname = surname


class Employee(Person):
    def __init__(self, kwargs):
        super().__init__(kwargs['name'], kwargs['surname'])
        self.tenure = kwargs['tenure']
        self.online_slots = kwargs['online_slots']
        self.stationary_slots = kwargs['stationary_slots']
        self.notes = kwargs.get('notes')

        self.availability = None
        self.online_slot_single = None
        self.online_slot_multiple = None
        self.stationary_slot_single = None
        self.stationary_slot_multiple = None

        if self.online_slots and self.stationary_slots:
            self.check_slots(self.online_slots, self.stationary_slots)

        self.check_fix_names()
        self.check_tenure()

    def check_slots(self, online_slots, stationary_slots):
        self.online_slot_single, self.online_slot_multiple = online_slots.split('; ')
        self.stationary_slot_single, self.stationary_slot_multiple = stationary_slots.split('; ')

    def check_fix_names(self):
        if len(self.name.split(' ')) > 1 and len(self.surname.split(' ')) > 1:
            self.surname, self.name = [x.capitalize() for x in self.name.split(' ') if x != '']

    def check_tenure(self):
        self.tenure = True if self.tenure else False


class Slot:
    def __init__(self, date, start, end):
        self.date = date
        self.start = start
        self.end = end


class Thesis:
    def __init__(self, kwargs):
        self.topic = kwargs['topic']
        self.individual = True if kwargs['individual'] == 'Pojedyncza' else False
        self.faculty = kwargs['faculty']

        self.supervisor = kwargs['supervisor']
        self.reviewer = kwargs['reviewer']

        self.slot = None
        self.head_of_committee = None
        self.committee_members = []

    def assign_slot(self, slot: Slot):
        self.slot = slot

    def specify_squad(self, leader: Employee, committee_members: List[Employee]):
        self.head_of_committee = leader
        self.committee_members = committee_members


class Student(Person):
    def __init__(self, kwargs):
        super().__init__(kwargs['name'], kwargs['surname'])
        self.index = kwargs['index']
        self.thesis = None

    def assign_thesis(self, thesis: Thesis):
        self.thesis = thesis
