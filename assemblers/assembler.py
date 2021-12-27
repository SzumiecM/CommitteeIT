import random
import statistics
import time
from typing import List
import copy

from matplotlib import pyplot as plt

from config import FITNESS_WEIGHTS, TRANSLATIONS, TRANSLATE
from models import Thesis, Employee, Individual
from utils import assign_to_thesis_heuristically, get_by_id, assign_employees


class Assembler:
    def __init__(self, thesis: List[Thesis], employees: List[Employee], population_count: int,
                 max_slots_per_employee: bool, max_thesis_per_slot: int, break_time: int, slot_block: int,
                 window_queue=None):

        self.thesis = copy.deepcopy(thesis)
        self.employees = copy.deepcopy(employees)
        self.population_count = population_count
        self.mean_slots_per_employee = int(len(self.thesis) * 3 / len(self.employees))

        self.max_slots_per_employee = self.mean_slots_per_employee + 6 if max_slots_per_employee else 9999
        self.max_thesis_per_slot = max_thesis_per_slot
        self.break_time = break_time
        self.slot_block = slot_block

        self.window_queue = window_queue

        self.population = []
        self.best_individuals = []
        self.assembler_name = ''
        self.time_elapsed = 0

    def create_initial_population(self):
        raise NotImplementedError

    def assemble(self):
        raise NotImplementedError

    def calculate_fitness(self):
        for individual in self.population:
            individual.fitness = self.calculate_individual_fitness(individual)

        self.population.sort(reverse=True)

    def calculate_individual_fitness(self, individual):
        thesis, employees = individual.thesis, individual.employees
        fitness = 0

        for employee in employees:
            if len(employee.assigned_slots) == 0 and FITNESS_WEIGHTS['slot_for_everyone']:
                fitness = -999
                break

            employee.assigned_slots.sort()

            breaks = [b - a for a, b in zip(employee.assigned_slots[:-1], employee.assigned_slots[1:])]

            fitness += breaks.count(0) * FITNESS_WEIGHTS['no_break']
            fitness += breaks.count(self.break_time) * FITNESS_WEIGHTS['break_time_break']

            double_thesis = len([x for x in thesis if not x.individual])
            fitness -= double_thesis * FITNESS_WEIGHTS['no_break']  # to not count them as breaks

            fitness += len([x for x in breaks if 30 < x < 60 * 13]) * FITNESS_WEIGHTS['longer_break']
            fitness += (len(employee.assigned_slots) - self.max_slots_per_employee) * FITNESS_WEIGHTS[
                'max_slots_per_employee_exceeded'] if len(employee.assigned_slots) > self.max_slots_per_employee else 0

        squads = []

        for thesis in thesis:
            if thesis.supervisor.id in [x.id for x in thesis.committee_members] \
                    or thesis.supervisor.id == thesis.head_of_committee.id:
                fitness += FITNESS_WEIGHTS['supervisor_present']
            if thesis.reviewer.id in [x.id for x in thesis.committee_members] \
                    or thesis.reviewer.id == thesis.head_of_committee.id:
                fitness += FITNESS_WEIGHTS['reviewer_present']

            squads.append({thesis.head_of_committee.id, thesis.committee_members[0].id, thesis.committee_members[1].id})

        fitness += (len(squads) - len(set(frozenset(x) for x in squads))) * FITNESS_WEIGHTS['same_squad']

        return fitness

    def save_results(self):
        self.population.sort(reverse=True)

        self.check_if_slots_duplicates()
        self.check_max_thesis_per_slot()

        if len(self.population) >= 3:
            self.best_individuals = self.population[:3]

        print([f'{e.surname} | {len(e.assigned_slots)} | {len(e.available_slots)}' for e in
               self.best_individuals[0].employees])

        print(
            f'{self.time_elapsed}m | {self.assembler_name} | {" | ".join([str(p.fitness) for p in self.population])}')

    def create_initial_individual_heuristically(self):
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

                individual_thesis = []
                double_thesis = []

                for single_thesis in thesis:
                    if single_thesis.individual:
                        individual_thesis.append(single_thesis)
                    else:
                        double_thesis.append(single_thesis)

                kwargs = {
                    'head_of_committee_list': head_of_committee_list,
                    'committee_member_list': committee_member_list,
                    'break_time': self.break_time,
                    'max_slots_per_employee': self.max_slots_per_employee,
                    'max_thesis_per_slot': self.max_thesis_per_slot
                }

                assign_to_thesis_heuristically(
                    thesis=double_thesis,
                    block=1,
                    slots_to_assign=2,
                    **kwargs
                )
                assign_to_thesis_heuristically(
                    thesis=individual_thesis,
                    block=self.slot_block,
                    slots_to_assign=1,
                    **kwargs
                )

                self.population.append(Individual(thesis, employees))

                break
            except TimeoutError:
                continue

    def check_if_slots_duplicates(self):
        for individual in self.population:
            for employee in individual.employees:
                slots = [slot.id for slot in employee.assigned_slots]
                if len(set(slots)) != len(slots):
                    raise Exception

    def check_max_thesis_per_slot(self):
        print([max(slot.assigned_thesis for slot in [thesis.slot for thesis in individual.thesis]) for individual in
               self.population])


class GeneticAssembler(Assembler):
    def __init__(self, thesis: List[Thesis], employees: List[Employee], population_count: int, iteration_count: int,
                 max_slots_per_employee: bool, max_thesis_per_slot: int, parents_percent: float,
                 population_mutation_percent: float, thesis_mutation_percent: float, break_time: int, slot_block: int,
                 timeout: int, window_queue=None):
        super().__init__(
            thesis=thesis,
            employees=employees,
            population_count=population_count,
            max_slots_per_employee=max_slots_per_employee,
            max_thesis_per_slot=max_thesis_per_slot,
            break_time=break_time,
            slot_block=slot_block,
            window_queue=window_queue
        )

        self.iteration_count = iteration_count
        self.parents_percent = parents_percent
        self.population_mutation_percent = population_mutation_percent
        self.thesis_mutation_percent = thesis_mutation_percent
        self.timeout = timeout
        self.parents = []

        self.mean_population_scores = []
        self.best_individual_scores = []
        self.mean_diffs = []
        self.elapsed_times = []

    def select_parents(self):
        best_population_count = int(self.population_count * self.parents_percent)
        self.parents = self.population[
                       :best_population_count if best_population_count % 2 == 0 else best_population_count + 1]

    def crossover(self):
        self.population.sort(reverse=True)
        child_count = int(len(self.parents) / 2)
        if child_count == 0:
            return
        individuals_to_replace = self.population[-child_count:]
        self.population = self.population[:-child_count]

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
                    parent = parents[0]
                    thesis = parent.thesis[j]
                    thesis, child_employees = assign_employees(thesis, child_employees, self.max_slots_per_employee)
                    child_thesis.append(thesis)

            for j in range(len(self.thesis)):
                if self.thesis[j].individual:
                    parent = random.choice(parents)
                    thesis = parent.thesis[j]
                    try:
                        thesis, child_employees = assign_employees(thesis, child_employees, self.max_slots_per_employee)
                    except:
                        try:
                            parent = parents[0 if parents.index(get_by_id(parents, parent.id)) == 1 else 1]
                            thesis = parent.thesis[j]
                            thesis, child_employees = assign_employees(thesis, child_employees,
                                                                       self.max_slots_per_employee)
                        except:
                            try:
                                self.create_thesis(
                                    thesis=thesis,
                                    employees=child_employees
                                )
                            except TimeoutError:
                                print('Crossover not successful')
                                return

                    child_thesis.append(thesis)

            child_thesis = sorted(child_thesis, key=lambda x: x.id)

            individuals_to_replace.append(Individual(child_thesis, child_employees))

        for individual in individuals_to_replace:
            if not individual.fitness:
                individual.fitness = self.calculate_individual_fitness(individual)

        individuals_to_replace.sort(reverse=True)
        individuals_to_replace = individuals_to_replace[:child_count]
        self.population.extend(individuals_to_replace)

    def mutate(self):
        mutate_population_count = int(self.population_count * self.population_mutation_percent)
        mutate_thesis_count = int(len(self.thesis) * self.thesis_mutation_percent)

        origins = random.sample(self.population, mutate_population_count)
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
                try:
                    head = get_by_id(mutant_head_of_committee_list, thesis.head_of_committee.id)
                    thesis.head_of_committee = head
                    thesis.head_of_committee.assigned_slots.remove(get_by_id(head.assigned_slots, thesis.slot.id))
                    thesis.head_of_committee.available_slots.append(thesis.slot)

                    if not thesis.individual:
                        slot_2 = get_by_id(head.assigned_slots, thesis.slot.id + 1)
                        thesis.head_of_committee.assigned_slots.remove(slot_2)
                        thesis.head_of_committee.available_slots.append(slot_2)

                    for member in thesis.committee_members:
                        member = get_by_id(mutant_committee_member_list, member.id)
                        member.assigned_slots.remove(get_by_id(member.assigned_slots, thesis.slot.id))
                        member.available_slots.append(thesis.slot)

                        if not thesis.individual:
                            slot_2 = get_by_id(member.assigned_slots, thesis.slot.id + 1)
                            member.assigned_slots.remove(slot_2)
                            member.available_slots.append(slot_2)

                    self.create_thesis(
                        thesis=thesis,
                        employees=mutant.employees
                    )
                except TimeoutError:
                    print('Mutation not successful')
                    return

            mutant.fitness = self.calculate_individual_fitness(mutant)
            if mutant.fitness > origin.fitness:
                self.population.remove(origin)
                self.population.append(mutant)

    def assemble(self):
        global_start = time.time()
        self.create_initial_population()

        parents_percent = self.parents_percent
        population_mutation_percent = self.population_mutation_percent
        thesis_mutation_percent = self.thesis_mutation_percent
        extreme_mutation_mode = False

        for i in range(self.iteration_count):
            start = time.time()
            previous_fitness = [p.fitness for p in self.population]
            self.calculate_fitness()
            self.select_parents()
            self.crossover()
            self.mutate()

            self.population.sort(reverse=True)

            self.mean_population_scores.append(round(statistics.mean([p.fitness for p in self.population])))
            self.best_individual_scores.append(self.population[0].fitness)

            fitness = [individual.fitness for individual in self.population]
            if len(set(fitness)) == 1 and not extreme_mutation_mode:
                print('entering extreme mutation mode')
                self.parents_percent = 0
                self.population_mutation_percent = 1
                self.thesis_mutation_percent = 0.2
                extreme_mutation_mode = True
            elif len(set(fitness)) != 1 and extreme_mutation_mode:
                print('leaving extreme mutation mode')
                self.parents_percent = parents_percent
                self.population_mutation_percent = population_mutation_percent
                self.thesis_mutation_percent = thesis_mutation_percent
                extreme_mutation_mode = False

            mean_population_diff = abs(statistics.mean(
                [x - y for (x, y) in zip([p.fitness for p in self.population], previous_fitness)]))

            self.mean_diffs.append(mean_population_diff)
            self.elapsed_times.append(round(time.time() - start, 2))

            print(
                f'{i + 1}/{self.iteration_count} |{self.population[0].fitness}| {self.assembler_name} ({round(time.time() - start, 2)}) -> mean score: {self.mean_population_scores[-1]} | mean diff: {mean_population_diff}')
            # print(sum([len(e.assigned_slots) for e in self.populations[0].employees]) / self.employees_per_slot)
            self.time_elapsed = round((time.time() - global_start) / 60, 2)

            self.window_queue.put({
                'assembler_name': self.assembler_name,
                'progress_msg': f'{TRANSLATIONS["ALGORITHMS"][self.assembler_name] if TRANSLATE else self.assembler_name} {i + 1}/{self.iteration_count} ({self.population[0].fitness})',
                'iteration': i + 1,
                'best_individual': self.population[0],
                'best_individual_scores': self.best_individual_scores,
                'mean_population_scores': self.mean_population_scores,
                'time_elapsed': self.time_elapsed
            })

        self.save_results()

        x = range(self.iteration_count)

        plt.plot(x, self.mean_diffs, '-b', label='średnia różnica wyników przystosowania osobnikówi')
        plt.title(
            f'Wyniki dla: {TRANSLATIONS["ALGORITHMS"][self.assembler_name]}, z czasem wykonywania: {self.time_elapsed}m')
        plt.xlabel('iteracje')
        plt.ylabel('różnica przystosowania')
        plt.legend(loc="upper left")
        plt.show()

        # plt.plot(x, self.elapsed_times, '-g', label='czas wykonywania iteracji')
        # plt.title(
        #     f'Wyniki dla: {TRANSLATIONS["ALGORITHMS"][self.assembler_name]}, z czasem wykonywania: {self.time_elapsed}m')
        # plt.xlabel('iteracje')
        # plt.ylabel('czas wykonywania')
        # plt.legend(loc="upper left")
        # plt.show()
        #
        # plt.plot(x, self.mean_population_scores, '-b',
        #          label='średni wynik przystosowania osobników' if TRANSLATE else 'mean population score')
        # plt.plot(x, self.best_individual_scores, '-r',
        #          label='wynik najlepszego osobnika' if TRANSLATE else 'best individual score')
        # plt.title(
        #     f'Wyniki dla: {TRANSLATIONS["ALGORITHMS"][self.assembler_name]}, z czasem wykonywania: {self.time_elapsed}m')
        # plt.xlabel('iteracje')
        # plt.ylabel('współczynnik przystosowania')
        # plt.legend(loc='upper left')
        # plt.show()

        results = f"""
        ///////////////////////////////////
        
        assembler: {self.assembler_name}
        iterations: {self.iteration_count}
        population count: {self.population_count}
        parents percent: {self.parents_percent}
        population mutation percent: {self.population_mutation_percent}
        thesis mutation percent: {self.thesis_mutation_percent}
        
        mean mean score: {statistics.mean(self.mean_population_scores)}
        stdev mean scores: {statistics.stdev(self.mean_population_scores)}
        mean mean score 10+: {statistics.mean(self.mean_population_scores[10:])}
        stdev mean scores 10+: {statistics.stdev(self.mean_population_scores[10:])}
        
        best score: {self.best_individual_scores[-1]}
        
        mean mean diffs: {statistics.mean(self.mean_diffs)}
        stdev mean diffs: {statistics.stdev(self.mean_diffs)}
        mean mean diffs 10+: {statistics.mean(self.mean_diffs[10:])}
        stdev mean diffs 10+: {statistics.stdev(self.mean_diffs[10:])}
        
        mean time: {statistics.mean(self.elapsed_times)}s
        stdev time: {statistics.stdev(self.elapsed_times)}s
        
        total time: {self.time_elapsed}m
        
        """

        with open("files\\results_new.txt", "a") as myfile:
            myfile.write(results)

    def create_thesis(self, thesis, employees):
        head_of_committee_list = []
        committee_member_list = []
        for employee in employees:
            if employee.tenure:
                head_of_committee_list.append(employee)
            else:
                committee_member_list.append(employee)

        start = time.time()
        while True:
            if time.time() - start > self.timeout:
                raise TimeoutError

            head_of_committee = head_of_committee_list[random.randrange(len(head_of_committee_list))]

            if len(head_of_committee.available_slots) < 1 or head_of_committee.assigned_slots == self.max_slots_per_employee:
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
                                            if slot.id in [s.id for s in committee_member.available_slots] and len(
                    committee_member.assigned_slots) < self.max_slots_per_employee]

            if not thesis.individual:
                compatible_committee_members = [committee_member for committee_member in compatible_committee_members
                                                if
                                                slot_2.id in [s.id for s in committee_member.available_slots] and len(
                                                    committee_member.assigned_slots) < self.max_slots_per_employee + 1]

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
                member.available_slots.remove(get_by_id(member.available_slots, slot.id))
                if not thesis.individual:
                    member.assigned_slots.append(slot_2)
                    member.available_slots.remove(get_by_id(member.available_slots, slot_2.id))
            break
