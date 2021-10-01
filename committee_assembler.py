import copy
import random
from typing import List

from models import Thesis, Employee, Population


class CommitteeAssembler:
    def __init__(self, thesis: List[Thesis], employees: List[Employee], slots: dict,
                 max_thesis_per_slot: int, population_count: int):

        self.thesis = thesis

        self.employees = employees

        self.slots = slots
        self.slot_list = [item for sublist in self.slots.values() for item in sublist]
        self.max_thesis_per_slot = max_thesis_per_slot

        self.population_count = population_count

        self.populations = []
        self.parents = []

    def create_initial_population(self):
        for i in range(self.population_count):
            employees = copy.deepcopy(self.employees)
            head_of_committee_list = []
            committee_member_list = []

            for employee in employees:
                if employee.tenure:
                    head_of_committee_list.append(employee)
                else:
                    committee_member_list.append(employee)

            thesis = copy.deepcopy(self.thesis)

            for single_thesis in thesis:
                while True:
                    head_of_committee = head_of_committee_list[random.randrange(len(head_of_committee_list))]

                    if len(head_of_committee.available_slots) < 1:
                        head_of_committee_list.remove(head_of_committee)
                        continue

                    single_thesis.head_of_committee = head_of_committee

                    slot = head_of_committee.available_slots[random.randrange(len(head_of_committee.available_slots))]

                    single_thesis.slot = slot

                    compatible_committee_members = [committee_member for committee_member in committee_member_list
                                                    if slot.__repr__() in committee_member.available_slots.__repr__()
                                                    and slot.__repr__() not in committee_member.assigned_slots.__repr__()]

                    if len(compatible_committee_members) < 2:
                        continue

                    single_thesis.committee_members = random.sample(compatible_committee_members, 2)

                    if slot.assigned_thesis == self.max_thesis_per_slot:
                        continue

                    slot.assigned_thesis += 1
                    head_of_committee.assigned_slots.append(slot)
                    head_of_committee.available_slots.remove(slot)
                    for member in single_thesis.committee_members:
                        member.assigned_slots.append(slot)
                        member.available_slots.remove(
                            [slot for slot in member.available_slots if slot.__repr__() == slot.__repr__()].pop()
                        )
                    break

            self.populations.append(Population(thesis, employees))

    def calculate_fitness(self):
        for population in self.populations:
            thesis, employees = population.thesis, population.employees
            fitness = 0

            for employee in employees:
                if len(employee.assigned_slots) == 0:
                    fitness = -999
                    break

                employee.assigned_slots.sort()

                breaks = [b - a for a, b in zip(employee.assigned_slots[:-1], employee.assigned_slots[1:])]

                fitness += breaks.count(0) * 50
                fitness += breaks.count(15) * 10

                fitness -= len([x for x in breaks if 30 < x < 60 * 13]) * 25

            for thesis in thesis:
                if thesis.supervisor.__repr__() in thesis.committee_members.__repr__() \
                        or thesis.supervisor.__repr__() is thesis.head_of_committee.__repr__():
                    fitness += 100
                if thesis.reviewer.__repr__() in thesis.committee_members.__repr__() \
                        or thesis.reviewer.__repr__() is thesis.head_of_committee.__repr__():
                    fitness += 70

            population.fitness = fitness

    def select_parents(self):
        self.populations.sort(reverse=True)

        best_population_count = int(self.population_count / 3)
        self.parents = self.populations[
                       :best_population_count if best_population_count % 2 == 0 else best_population_count + 1]
        print([x.fitness for x in self.parents])

    def crossover(self):
        crossover_count = int(len(self.thesis) * 0.1)
        random.shuffle(self.parents)

        for i in range(0, len(self.parents), 2):
            available_thesis_indexes = list(range(len(self.parents)))
            for _ in range(crossover_count):
                while True:
                    random_place = random.choice(available_thesis_indexes)
                    thesis_1 = self.parents[i][random_place]
                    thesis_2 = self.parents[i + 1][random_place]

                    self.parents[i][random_place] = thesis_2
                    self.parents[i + 1][random_place] = thesis_1

                    if self.check_for_collision(self.parents[i]) and self.check_for_collision(self.parents[i + 1]):
                        available_thesis_indexes.remove(random_place)
                        break

    def mutate(self):
        pass

    def check_for_collision(self, population):
        for thesis in population.employees:
            pass
