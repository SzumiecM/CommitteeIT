import copy
import random
import statistics
import time
from typing import List

from models import Thesis, Employee, Population


def create_thesis(thesis, employees, max_thesis_per_slot):
    head_of_committee_list = []
    committee_member_list = []
    for employee in employees:
        if employee.tenure:
            head_of_committee_list.append(employee)
        else:
            committee_member_list.append(employee)
    # todo assign two slots for double thesis
    # todo add limit of thesis per employee
    while True:
        head_of_committee = head_of_committee_list[random.randrange(len(head_of_committee_list))]

        if len(head_of_committee.available_slots) < 1:
            head_of_committee_list.remove(head_of_committee)
            continue

        thesis.head_of_committee = head_of_committee

        slot = head_of_committee.available_slots[random.randrange(len(head_of_committee.available_slots))]

        thesis.slot = slot

        compatible_committee_members = [committee_member for committee_member in committee_member_list
                                        if slot.__repr__() in committee_member.available_slots.__repr__()]

        if len(compatible_committee_members) < 2:
            continue

        thesis.committee_members = random.sample(compatible_committee_members, 2)

        if slot.assigned_thesis == max_thesis_per_slot:
            continue

        slot.assigned_thesis += 1
        head_of_committee.assigned_slots.append(slot)
        head_of_committee.available_slots.remove(slot)
        for member in thesis.committee_members:
            member.assigned_slots.append(slot)
            member.available_slots.remove(get_by_repr(member.available_slots, slot))
        break


def get_by_repr(list_, y):
    return [x for x in list_ if x.__repr__() == y.__repr__()].pop()


def assign_employees(thesis, employees):
    thesis, employees = copy.deepcopy(thesis), copy.deepcopy(employees)

    thesis.head_of_committee = get_by_repr(employees, thesis.head_of_committee)
    thesis.head_of_committee.available_slots.remove(
        get_by_repr(thesis.head_of_committee.available_slots, thesis.slot))
    thesis.head_of_committee.assigned_slots.append(thesis.slot)
    for member in thesis.committee_members:
        member = get_by_repr(employees, member)
        member.available_slots.remove(get_by_repr(member.available_slots, thesis.slot))
        member.assigned_slots.append(thesis.slot)

    return thesis, employees


class CommitteeAssembler:
    def __init__(self, thesis: List[Thesis], employees: List[Employee], slots: dict,
                 max_thesis_per_slot: int, population_count: int, iteration_count: int):

        self.thesis = thesis

        self.employees = employees

        self.slots = slots
        self.slot_list = [item for sublist in self.slots.values() for item in sublist]
        self.max_thesis_per_slot = max_thesis_per_slot

        self.population_count = population_count
        self.iteration_count = iteration_count

        self.populations = []
        self.parents = []
        self.best_populations = []

    def create_initial_population(self):
        for i in range(self.population_count):
            employees = copy.deepcopy(self.employees)

            thesis = copy.deepcopy(self.thesis)

            for single_thesis in thesis:
                create_thesis(
                    thesis=single_thesis,
                    employees=employees,
                    max_thesis_per_slot=self.max_thesis_per_slot
                )
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

        self.populations.sort(reverse=True)

    def select_parents(self):
        best_population_count = int(self.population_count / 3)
        self.parents = self.populations[
                       :best_population_count if best_population_count % 2 == 0 else best_population_count + 1]
        print([x.fitness for x in self.parents])

    def crossover(self):
        crossover_count = int(len(self.thesis) * 0.1)
        random.shuffle(self.parents)
        self.populations = self.populations[:-int(len(self.parents) / 2)]

        for i in range(0, len(self.parents), 2):
            parents = copy.deepcopy(self.parents[i]), copy.deepcopy(self.parents[i + 1])
            child_thesis = []
            child_employees = copy.deepcopy(self.employees)
            child_head_of_committee_list = []
            child_committee_member_list = []

            for employee in child_employees:
                if employee.tenure:
                    child_head_of_committee_list.append(employee)
                else:
                    child_committee_member_list.append(employee)

            for j in range(len(self.thesis)):
                parent = random.choice(parents)
                thesis = parent.thesis[j]
                try:
                    thesis, child_employees = assign_employees(thesis, child_employees)
                except:
                    try:
                        parent = parents[0 if parents.index(get_by_repr(parents, parent)) == 1 else 1]
                        thesis = parent.thesis[j]
                        thesis, child_employees = assign_employees(thesis, child_employees)
                    except:
                        create_thesis(
                            thesis=thesis,
                            employees=child_employees,
                            max_thesis_per_slot=self.max_thesis_per_slot
                        )

                child_thesis.append(thesis)
            self.populations.append(Population(child_thesis, child_employees))

    def mutate(self):
        mutate_population_count = int(self.population_count / 4)
        mutate_thesis_count = int(len(self.thesis) / 4)

        mutants = random.sample(self.parents, mutate_population_count)
        for mutant in mutants:
            mutant_head_of_committee_list = []
            mutant_committee_member_list = []

            for employee in mutant.employees:
                if employee.tenure:
                    mutant_head_of_committee_list.append(employee)
                else:
                    mutant_committee_member_list.append(employee)

            mutated_thesis = random.sample(mutant.thesis, mutate_thesis_count)

            for thesis in mutated_thesis:
                head = get_by_repr(mutant_head_of_committee_list, thesis.head_of_committee)
                thesis.head_of_committee = head
                thesis.head_of_committee.assigned_slots.remove(get_by_repr(head.assigned_slots, thesis.slot))
                thesis.head_of_committee.available_slots.append(thesis.slot)
                for member in thesis.committee_members:
                    member = get_by_repr(mutant_committee_member_list, member)
                    member.assigned_slots.remove(get_by_repr(member.assigned_slots, thesis.slot))
                    member.available_slots.append(thesis.slot)

                create_thesis(
                    thesis=thesis,
                    employees=mutant.employees,
                    max_thesis_per_slot=self.max_thesis_per_slot
                )
                # todo save only better ones

    def assemble(self):
        self.create_initial_population()
        for i in range(self.iteration_count):
            start = time.time()
            self.calculate_fitness()
            self.select_parents()
            self.crossover()
            self.mutate()
            print(sum([len(e.available_slots) for e in self.populations[0].employees]))
            print(sum([len(e.assigned_slots) for e in self.populations[0].employees]) / 3)
            print(
                f'{i + 1}/{self.iteration_count} | time: {round(time.time() - start)}s | mean: {round(statistics.mean([p.fitness for p in self.populations]))}')
        self.save_results()

    def save_results(self):
        self.populations.sort(reverse=True)

        self.best_populations = self.populations[:3]
        print([f'{e.surname} | {len(e.assigned_slots)}' for e in self.best_populations[0].employees])
        print(sum([len(e.assigned_slots) for e in self.best_populations[0].employees]) / 3)  # 5-123/10-166
        print(len(self.best_populations[0].thesis))

        for i, population in enumerate(self.best_populations):
            with open(f'results/{i + 1} population.txt', 'w') as f:
                lines = [f'{x} - {x.head_of_committee} | {x.committee_members}\n' for x in population.thesis]
                f.writelines(lines)
                f.close()
