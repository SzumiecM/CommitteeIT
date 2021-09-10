from typing import List


class Person:
    def __init__(self, name: str, surname: str):
        self.name = name
        self.surname = surname


class Employee(Person):
    def __init__(self, name: str, surname: str, tenure: bool,
                 online_slots: tuple = None, stationary_slots: tuple = None, availability: dict = None):
        super().__init__(name, surname)
        self.tenure = tenure
        self.online_slot_single = None
        self.online_slot_multiple = None
        self.stationary_slot_single = None
        self.stationary_slot_multiple = None
        self.availability = None

        if tenure:
            self.assign_slots(online_slots, stationary_slots)

        self.assign_availability(availability)

    def assign_slots(self, online_slots, stationary_slots):
        self.online_slot_single, self.online_slot_multiple = online_slots
        self.stationary_slot_single, self.stationary_slot_multiple = stationary_slots

    def assign_availability(self, availability):
        self.availability = availability


class Slot:
    def __init__(self, date, start, end):
        self.date = date
        self.start = start
        self.end = end


class Thesis:
    def __init__(self, kwargs):
        self.topic = kwargs['topic']
        self.individual = kwargs['individual']
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
