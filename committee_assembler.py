import copy
import random
from typing import List

from models import Thesis, Employee, Slot


class CommitteeAssembler:
    def __init__(self, thesis: List[Thesis], employees: List[Employee], slots: dict,
                 max_thesis_per_slot: int, population_count: int):

        self.thesis = thesis

        self.head_of_committee_list = []
        self.committee_member_list = []

        for employee in employees:
            if employee.tenure:
                self.head_of_committee_list.append(employee)
            else:
                self.committee_member_list.append(employee)

        self.slots = slots
        self.slot_list = [item for sublist in self.slots.values() for item in sublist]
        self.max_thesis_per_slot = max_thesis_per_slot

        self.population_count = population_count

        self.population = []  # list of Thesis setups

    def create_initial_population(self):
        for i in range(self.population_count):

            thesis = copy.deepcopy(self.thesis)
            head_of_committee_list = copy.deepcopy(self.head_of_committee_list)
            committee_member_list = copy.deepcopy(self.committee_member_list)

            for single_thesis in thesis:
                while True:
                    head_of_committee = head_of_committee_list[random.randrange(len(head_of_committee_list))]

                    if len(head_of_committee.slots) < 1:
                        head_of_committee_list.remove(head_of_committee)
                        continue

                    single_thesis.head_of_committee = head_of_committee

                    single_thesis.slot = head_of_committee.slots[random.randrange(len(head_of_committee.slots))]

                    compatible_committee_members = [committee_member for committee_member in committee_member_list
                                                    if single_thesis.slot.__repr__() in committee_member.slots.__repr__()]

                    if len(compatible_committee_members) < 2:
                        continue

                    single_thesis.committee_members = random.sample(compatible_committee_members, 2)

                    if single_thesis.slot.assigned_thesis == self.max_thesis_per_slot:
                        continue

                    single_thesis.slot.assigned_thesis += 1

                    head_of_committee.slots.remove(single_thesis.slot)
                    for member in single_thesis.committee_members:
                        committee_member_list[committee_member_list.index(member)].slots.remove(
                            [slot for slot in member.slots if slot.__repr__() == single_thesis.slot.__repr__()].pop())
                    break

            self.population.append(thesis)
            # print([
            #           f'{x.topic} | {x.slot} | {x.head_of_committee.surname} | {x.committee_members[0].surname} | {x.committee_members[1].surname}'
            #           for x in thesis])

            # for x in thesis:
            #     print(
            #         f'{x.topic} | {x.slot} | {x.head_of_committee.surname} | {x.committee_members[0].surname} | {x.committee_members[1].surname}')

    def calculate_fitness(self):
        for population in self.population:
            population.sort()

    def select_parents(self):
        pass

    def crossover(self):
        pass

    def mutate(self):
        pass
