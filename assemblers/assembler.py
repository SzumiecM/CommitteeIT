import random
import statistics
import time
from typing import List
import copy

from matplotlib import pyplot as plt

from models import Thesis, Employee, Population
from utils import assign_to_thesis_heuristically, get_by_repr, get_by_id, assign_employees


class Assembler:
    # todo define everywhere super() with parameter names
    def __init__(self, thesis: List[Thesis], employees: List[Employee], employees_per_slot: int,
                 population_count: int, max_slots_per_employee: bool, max_thesis_per_slot: int):

        self.thesis = copy.deepcopy(thesis)
        self.employees = copy.deepcopy(employees)
        self.population_count = population_count
        self.employees_per_slot = employees_per_slot
        self.mean_slots_per_employee = int(len(self.thesis) * self.employees_per_slot / len(self.employees))

        self.max_slots_per_employee = self.mean_slots_per_employee + 6 if max_slots_per_employee else 9999
        self.max_thesis_per_slot = max_thesis_per_slot

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

            breaks = [b - a for a, b in zip(employee.assigned_slots[:-1], employee.assigned_slots[1:]) if b - a != 15]

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
        # print(sum([len(e.assigned_slots) for e in self.best_populations[0].employees]) / self.employees_per_slot)
        print(f'{self.assembler_name} | {" | ".join([str(p.fitness) for p in self.populations])}')

        for i, population in enumerate(self.best_populations):
            with open(f'results/{i + 1} {self.assembler_name} population.txt', 'w') as f:
                lines = [f'{x} - {x.head_of_committee} | {x.committee_members}\n' for x in population.thesis]
                f.writelines(lines)
                f.close()

    def create_initial_population_heuristically(self):
        while True:
            try:
                thesis = copy.deepcopy(self.thesis)
                employees = copy.deepcopy(self.employees)

                head_of_committee_list = []
                committee_member_list = []
                for employee in employees:
                    if employee.tenure:
                        head_of_committee_list.append(employee)
                    else:
                        committee_member_list.append(employee)

                block = 3

                individual_thesis = []
                double_thesis = []

                for single_thesis in thesis:
                    if single_thesis.individual:
                        individual_thesis.append(single_thesis)
                    else:
                        double_thesis.append(single_thesis)

                assign_to_thesis_heuristically(double_thesis, head_of_committee_list, committee_member_list, 1, 2,
                                               self.max_slots_per_employee)
                assign_to_thesis_heuristically(individual_thesis, head_of_committee_list, committee_member_list, block,
                                               1,
                                               self.max_slots_per_employee)

                self.populations.append(Population(thesis, employees))

                break
            except TimeoutError:
                continue


class GeneticAssembler(Assembler):
    def __init__(self, thesis: List[Thesis], employees: List[Employee], employees_per_slot: int,
                 population_count: int, iteration_count: int, max_slots_per_employee: bool, max_thesis_per_slot: int):
        super().__init__(thesis, employees, employees_per_slot, population_count, max_slots_per_employee,
                         max_thesis_per_slot)

        self.iteration_count = iteration_count
        self.parents = []

    def create_initial_population(self):
        raise NotImplementedError

    def select_parents(self):
        best_population_count = int(self.population_count / 3)
        self.parents = self.populations[
                       :best_population_count if best_population_count % 2 == 0 else best_population_count + 1]
        print([x.fitness for x in self.parents])

    def crossover(self):
        child_count = int(len(self.parents) / 2)
        populations_to_replace = self.populations[-child_count:]
        self.populations = self.populations[:-child_count]

        random.shuffle(self.parents)

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

            populations_to_replace.append(Population(child_thesis, child_employees))

        for population in populations_to_replace:
            if not population.fitness:
                population.fitness = self.calculate_population_fitness(population)

        populations_to_replace.sort(reverse=True)
        populations_to_replace = populations_to_replace[:child_count]
        self.populations.extend(populations_to_replace)

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

        mean_population_score = []
        best_population_score = []

        for i in range(self.iteration_count):
            start = time.time()
            self.calculate_fitness()
            self.select_parents()
            self.crossover()
            self.mutate()

            mean_population_score.append(round(statistics.mean([p.fitness for p in self.populations])))
            best_population_score.append(self.populations[0].fitness)

            # print(sum([len(e.assigned_slots) for e in self.populations[0].employees]) / 3)
            # print(
            #     f'{i + 1}/{self.iteration_count} | time: {round(time.time() - start)}s | mean: {round(statistics.mean([p.fitness for p in self.populations]))}')
        self.save_results()

        x = range(self.iteration_count)
        plt.plot(x, mean_population_score, '-b', label='mean population score')
        plt.plot(x, best_population_score, '-r', label='best population score')
        plt.title(f'Population score for {self.assembler_name}')
        plt.xlabel('Iteration')
        plt.ylabel('Score')
        plt.legend(loc="upper left")
        plt.show()

    def create_thesis(self, thesis, employees):
        head_of_committee_list = []
        committee_member_list = []
        for employee in employees:
            if employee.tenure:
                head_of_committee_list.append(employee)
            else:
                committee_member_list.append(employee)

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
                    if slot_2.assigned_thesis == self.max_thesis_per_slot:
                        continue

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
            if not thesis.individual:
                slot_2.assigned_thesis += 1

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