from typing import List
import copy

from models import Thesis, Employee


class Assembler:
    def __init__(self, thesis: List[Thesis], employees: List[Employee], slots: dict, employees_per_slot: int):

        self.thesis = copy.deepcopy(thesis)
        self.employees = copy.deepcopy(employees)
        self.employees_per_slot = employees_per_slot\

        self.mean_slots_per_employee = int(len(self.thesis) * self.employees_per_slot / len(self.employees))
        self.max_slots_per_employee = self.mean_slots_per_employee + 6

        # self.slots = slots
        # self.slot_list = [item for sublist in self.slots.values() for item in sublist]

        self.populations = []
        self.best_populations = []
        self.assembler_name = ''

    def create_initial_population(self):
        raise NotImplementedError

    def assemble(self):
        raise NotImplementedError

    def calculate_fitness(self):
        for population in self.populations:
            population.fitness = self.calculate_population_fitness(population)

        self.populations.sort(reverse=True)

    def calculate_population_fitness(self, population):
        thesis, employees = population.thesis, population.employees
        fitness = 0
        # todo consider storing only slots id and read their value only in calculate_fitness method

        for employee in employees:
            if len(employee.assigned_slots) == 0:
                fitness = -999
                break

            employee.assigned_slots.sort()

            breaks = [b - a for a, b in zip(employee.assigned_slots[:-1], employee.assigned_slots[1:]) if b-a != 15]

            fitness += breaks.count(0) * 50
            fitness += breaks.count(15) * 10

            # todo reward same committee squads

            double_thesis = len([x for x in thesis if not x.individual])
            fitness -= double_thesis * 50  # to not count them as breaks

            fitness -= len([x for x in breaks if 30 < x < 60 * 13]) * 50
            fitness -= (len(employee.assigned_slots) - self.max_slots_per_employee) * 20 if len(
                employee.assigned_slots) > self.max_slots_per_employee else 0

        for thesis in thesis:
            if thesis.supervisor.__repr__() in thesis.committee_members.__repr__() \
                    or thesis.supervisor.__repr__() is thesis.head_of_committee.__repr__():
                fitness += 100
            if thesis.reviewer.__repr__() in thesis.committee_members.__repr__() \
                    or thesis.reviewer.__repr__() is thesis.head_of_committee.__repr__():
                fitness += 70

        return fitness

    def save_results(self):
        self.populations.sort(reverse=True)

        if len(self.populations) >= 3:
            self.best_populations = self.populations[:3]

        print([f'{e.surname} | {len(e.assigned_slots)} | {len(e.available_slots)}' for e in
               self.best_populations[0].employees])
        print(sum([len(e.assigned_slots) for e in self.best_populations[0].employees]) / self.employees_per_slot)
        print(self.best_populations[0].fitness)

        for i, population in enumerate(self.best_populations):
            with open(f'results/{i + 1} {self.assembler_name} population.txt', 'w') as f:
                lines = [f'{x} - {x.head_of_committee} | {x.committee_members}\n' for x in population.thesis]
                f.writelines(lines)
                f.close()
