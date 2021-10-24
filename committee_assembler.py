import copy
import random
import statistics
import time
from typing import List

from models import Thesis, Employee, Population


def get_by_repr(list_, y):
    return [x for x in list_ if x.__repr__() == y.__repr__()].pop()


def get_by_id(list_, id_):
    # todo maybe replace with some clever lambda
    return [x for x in list_ if x.id == id_].pop()


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
                 max_thesis_per_slot: int, population_count: int, iteration_count: int,
                 max_slots_per_employee: bool):

        self.thesis = thesis

        self.employees = employees

        # self.slots = slots
        # self.slot_list = [item for sublist in self.slots.values() for item in sublist]
        self.max_thesis_per_slot = max_thesis_per_slot
        self.max_slots_per_employee = int(
            len(self.thesis) * 3 / len(self.employees)) + 2 if max_slots_per_employee else 9999

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
                self.create_thesis(
                    thesis=single_thesis,
                    employees=employees,
                )
            self.populations.append(Population(thesis, employees))

    def calculate_fitness(self):
        for population in self.populations:
            population.fitness = self.calculate_population_fitness(population)

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

            parents[0].thesis = sorted(parents[0].thesis, key=lambda x: x.id)
            parents[1].thesis = sorted(parents[1].thesis, key=lambda x: x.id)

            for j in range(len(self.thesis)):
                if not self.thesis[j].individual:
                    parent = parents[0]  # random.choice(parents)
                    thesis = parent.thesis[j]
                    thesis, child_employees = assign_employees(thesis, child_employees)
                    child_thesis.append(thesis)

            for j in range(len(self.thesis)):
                if self.thesis[j].individual:
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
                            self.create_thesis(
                                thesis=thesis,
                                employees=child_employees
                            )

                    child_thesis.append(thesis)

            child_thesis = sorted(child_thesis, key=lambda x: x.id)

            self.populations.append(Population(child_thesis, child_employees))

    def mutate(self):
        mutate_population_count = int(self.population_count / 4)
        mutate_thesis_count = int(len(self.thesis) / 4)

        origins = random.sample(self.populations, mutate_population_count)
        for origin in origins:
            mutant = copy.deepcopy(origin)
            mutant_head_of_committee_list = []
            mutant_committee_member_list = []

            for employee in mutant.employees:
                if employee.tenure:
                    mutant_head_of_committee_list.append(employee)
                else:
                    mutant_committee_member_list.append(employee)

            mutated_thesis = random.sample(mutant.thesis, mutate_thesis_count)

            for thesis in mutated_thesis:
                if thesis.individual:  # todo consider mutating also double (but it would overcomplicate stuff)
                    head = get_by_repr(mutant_head_of_committee_list, thesis.head_of_committee)
                    thesis.head_of_committee = head
                    thesis.head_of_committee.assigned_slots.remove(get_by_repr(head.assigned_slots, thesis.slot))
                    thesis.head_of_committee.available_slots.append(thesis.slot)
                    for member in thesis.committee_members:
                        member = get_by_repr(mutant_committee_member_list, member)
                        member.assigned_slots.remove(get_by_repr(member.assigned_slots, thesis.slot))
                        member.available_slots.append(thesis.slot)
                    self.create_thesis(
                        thesis=thesis,
                        employees=mutant.employees
                    )

            mutant.fitness = self.calculate_population_fitness(mutant)
            if mutant.fitness > origin.fitness:
                self.populations.remove(origin)
                self.populations.append(mutant)

    def assemble(self):
        self.create_initial_population()
        for i in range(self.iteration_count):
            start = time.time()
            self.calculate_fitness()
            self.select_parents()
            self.crossover()
            self.mutate()
            print(sum([len(e.assigned_slots) for e in self.populations[0].employees]) / 3)
            print(
                f'{i + 1}/{self.iteration_count} | time: {round(time.time() - start)}s | mean: {round(statistics.mean([p.fitness for p in self.populations]))}')
        self.save_results()

    def save_results(self):
        self.populations.sort(reverse=True)

        self.best_populations = self.populations[:3]
        print([f'{e.surname} | {len(e.assigned_slots)} | {len(e.available_slots)}' for e in
               self.best_populations[0].employees])
        print(sum([len(e.assigned_slots) for e in self.best_populations[0].employees]) / 3)
        print(len(self.best_populations[0].thesis))

        for i, population in enumerate(self.best_populations):
            with open(f'results/{i + 1} population.txt', 'w') as f:
                lines = [f'{x} - {x.head_of_committee} | {x.committee_members}\n' for x in population.thesis]
                f.writelines(lines)
                f.close()

    def create_thesis(self, thesis, employees):
        head_of_committee_list = []
        committee_member_list = []
        for employee in employees:
            if employee.tenure:
                head_of_committee_list.append(employee)
            else:
                committee_member_list.append(employee)

        # todo assign two slots for double thesis
        # todo consider approach with merge_slots function like merge_slots(slot1, slot2) -> slot3
        # todo or just have two slots next to each other reserved and always check if thesis is not individual
        while True:
            head_of_committee = head_of_committee_list[random.randrange(len(head_of_committee_list))]

            if len(head_of_committee.available_slots) < 1:
                head_of_committee_list.remove(head_of_committee)
                continue

            slot = head_of_committee.available_slots[random.randrange(len(head_of_committee.available_slots))]

            if not thesis.individual:
                if slot.id + 1 not in [slot.id for slot in head_of_committee.available_slots]:
                    continue
                else:
                    slot_2 = get_by_id(head_of_committee.available_slots, slot.id + 1)

            if slot.assigned_thesis == self.max_thesis_per_slot:
                continue

            compatible_committee_members = [committee_member for committee_member in committee_member_list
                                            if slot.__repr__() in committee_member.available_slots.__repr__()]

            if not thesis.individual:
                compatible_committee_members = [committee_member for committee_member in compatible_committee_members
                                                if slot_2.__repr__() in committee_member.available_slots.__repr__()]

            if len(compatible_committee_members) < 2:
                continue

            thesis.slot = slot
            thesis.head_of_committee = head_of_committee
            thesis.committee_members = random.sample(compatible_committee_members, 2)

            slot.assigned_thesis += 1
            head_of_committee.assigned_slots.append(slot)
            head_of_committee.available_slots.remove(slot)
            if not thesis.individual:
                head_of_committee.assigned_slots.append(slot_2)
                head_of_committee.available_slots.remove(slot_2)
            for member in thesis.committee_members:
                member.assigned_slots.append(slot)
                member.available_slots.remove(get_by_repr(member.available_slots, slot))
                if not thesis.individual:
                    member.assigned_slots.append(slot_2)
                    member.available_slots.remove(get_by_repr(member.available_slots, slot_2))
            break

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

            double_thesis = len([x for x in thesis if not x.individual])
            # print(double_thesis)
            # fitness -= double_thesis * 50  # to not count them as breaks

            fitness -= len([x for x in breaks if 30 < x < 60 * 13]) * 25
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
