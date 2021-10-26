from typing import List

from models import Thesis, Employee


class Assembler:
    def __init__(self, thesis: List[Thesis], employees: List[Employee], slots: dict,
                 max_thesis_per_slot: int, population_count: int, max_slots_per_employee: bool):
        self.thesis = thesis

        self.employees = employees

        # self.slots = slots
        # self.slot_list = [item for sublist in self.slots.values() for item in sublist]
        self.max_thesis_per_slot = max_thesis_per_slot
        self.max_slots_per_employee = int(
            len(self.thesis) * 3 / len(self.employees)) + 2 if max_slots_per_employee else 9999

        self.population_count = population_count

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

        for employee in employees:
            if len(employee.assigned_slots) == 0:
                fitness = -999
                break

            employee.assigned_slots.sort()

            breaks = [b - a for a, b in zip(employee.assigned_slots[:-1], employee.assigned_slots[1:])]

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

        self.best_populations = self.populations[:3]

        print([f'{e.surname} | {len(e.assigned_slots)} | {len(e.available_slots)}' for e in
               self.best_populations[0].employees])
        print(sum([len(e.assigned_slots) for e in self.best_populations[0].employees]) / 3)
        print(len(self.best_populations[0].thesis))

        for i, population in enumerate(self.best_populations):
            with open(f'results/{i + 1} {self.assembler_name} population.txt', 'w') as f:
                lines = [f'{x} - {x.head_of_committee} | {x.committee_members}\n' for x in population.thesis]
                f.writelines(lines)
                f.close()