from datetime import datetime
from typing import List


class IDModel:
    def __init__(self, id_: int):
        self.id = id_


class Person(IDModel):
    def __init__(self, name: str, surname: str, id_: int):
        super().__init__(id_)
        self.name = name
        self.surname = surname


class Employee(Person):
    def __init__(self, kwargs):
        super().__init__(kwargs['name'], kwargs['surname'], kwargs['id'])
        self.tenure = kwargs['tenure']
        self.online_slots = kwargs['online_slots']
        self.stationary_slots = kwargs['stationary_slots']
        self.notes = kwargs.get('notes')

        self.availability = None
        self.online_slot_single = None
        self.online_slot_multiple = None
        self.stationary_slot_single = None
        self.stationary_slot_multiple = None

        self.available_slots = []
        self.assigned_slots = []

        if self.online_slots and self.stationary_slots:
            self.check_slots(self.online_slots, self.stationary_slots)

        self.check_fix_names()
        self.check_tenure()

    def __repr__(self):
        return f'{self.name}|{self.surname}|{self.tenure}'

    def check_slots(self, online_slots, stationary_slots):
        self.online_slot_single, self.online_slot_multiple = online_slots.split('; ')
        self.stationary_slot_single, self.stationary_slot_multiple = stationary_slots.split('; ')

    def check_fix_names(self):
        if len(self.name.split(' ')) > 1 and len(self.surname.split(' ')) > 1:
            self.surname, self.name = [x.capitalize() for x in self.name.split(' ') if x != '']

    def check_tenure(self):
        self.tenure = True if self.tenure else False


class Slot(IDModel):
    def __init__(self, day, start, end, id_):
        super().__init__(id_)
        self.day = day
        self.start = start
        self.end = end

        self.assigned_thesis = 0

    def __repr__(self):
        return f'{self.day}: {self.start.hour}:{self.start.minute}-{self.end.hour}:{self.end.minute}'

    def __lt__(self, other):
        return self.start < other.end

    def __sub__(self, other):
        delta = self.start - other.end
        return int(delta.seconds / 60) + 24 * 60 * delta.days


class Thesis:
    def __init__(self, kwargs):
        self.topic = kwargs['topic']
        self.individual = True if kwargs['individual'] == 'Pojedyncza' else False
        self.faculty = kwargs['faculty']

        self.supervisor = kwargs['supervisor']
        self.reviewer = kwargs['reviewer']

        self.id = None
        self.slot = None
        self.head_of_committee = None
        self.committee_members = []

    def __repr__(self):
        return f'{self.topic} | {self.slot}'

    def __lt__(self, other):
        return self.slot.__repr__() < other.slot.__repr__()

    def assign_slot(self, slot: Slot):
        self.slot = slot

    def specify_squad(self, leader: Employee, committee_members: List[Employee]):
        self.head_of_committee = leader
        self.committee_members = committee_members


class Student(Person):
    def __init__(self, kwargs):
        super().__init__(kwargs['name'], kwargs['surname'], kwargs['id'])
        self.index = kwargs['index']
        self.thesis = None

    def assign_thesis(self, thesis: Thesis):
        self.thesis = thesis


class Population:
    def __init__(self, thesis: List[Thesis], employees: List[Employee]):
        self.thesis = thesis
        self.employees = employees
        self.fitness = 0

    def __lt__(self, other):
        return self.fitness < other.fitness
