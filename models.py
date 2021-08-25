class Person:
    def __init__(self, name: str, surname: str):
        self.name = name
        self.surname = surname


class CommitteeMember(Person):
    def __init__(self, name: str, surname: str, tenure: bool,
                 online_slots: tuple = None, stationary_slots: tuple = None, availability: dict = None):
        super().__init__(name, surname)
        self.tenure = tenure
        self.online_slot_single = None
        self.online_slot_multiple = None
        self.stationary_slot_single = None
        self.stationary_slot_multiple = None
        self.availability = None

        self.assign_slots(online_slots, stationary_slots)
        self.assign_availability(availability)

    def assign_slots(self, online_slots, stationary_slots):
        self.online_slot_single, self.online_slot_multiple = online_slots
        self.stationary_slot_single, self.stationary_slot_multiple = stationary_slots

    def assign_availability(self, availability):
        self.availability = availability


class Thesis:
    def __init__(self, topic: str, individual: bool,
                 supervisor: CommitteeMember = None, reviewer: CommitteeMember = None, faculty: str = None):
        self.topic = topic
        self.individual = individual
        self.faculty = faculty

        self.supervisor = supervisor
        self.reviewer = reviewer

        # to define after
        self.date = None
        self.start = None
        self.end = None
        self.leader = None
        self.committee_members = []

    def specify_date(self, date, start, end):
        self.date = date
        self.start = start
        self.end = end

    def specify_squad(self, leader, committee_members):
        self.leader = leader
        self.committee_members = committee_members


class Student(Person):
    def __init__(self, name: str, surname: str, index: int,
                 thesis: Thesis = None):
        super().__init__(name, surname)
        self.index = index
        self.thesis = thesis

    def assign_thesis(self, thesis: Thesis):
        self.thesis = thesis
