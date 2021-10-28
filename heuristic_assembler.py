import copy
import random
import statistics
import time
import matplotlib.pyplot as plt
from typing import List

from assembler import Assembler
from utils import get_by_repr, get_by_id
from models import Population, Thesis, Employee


class HeuristicAssembler(Assembler):
    def __init__(self, thesis: List[Thesis], employees: List[Employee], slots: dict, employees_per_slot: int):
        super().__init__(thesis, employees, slots, employees_per_slot)

        self.assembler_name = 'heuristic'

    def create_initial_population(self):
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

        individual_thesis = []  # todo rename (shadowing different variable)
        double_thesis = []

        for single_thesis in thesis:
            if single_thesis.individual:
                individual_thesis.append(single_thesis)
            else:
                double_thesis.append(single_thesis)

        self.assign_to_thesis(double_thesis, head_of_committee_list, committee_member_list, 1, 2)
        self.assign_to_thesis(individual_thesis, head_of_committee_list, committee_member_list, block, 1)

        self.populations.append(Population(thesis, employees))
        self.populations[0].fitness = self.calculate_population_fitness(self.populations[0])
        self.best_populations.append(self.populations[0])

    def assemble(self):
        while True:
            try:
                self.create_initial_population()
                break
            except TimeoutError:
                continue
        self.save_results()

    def assign_to_thesis(self, thesis, head_of_committee_list, committee_member_list, block, slots_to_assign):
        for i in range(0, len(thesis), block):
            start = time.time()
            head_of_committee_list.sort()
            committee_member_list.sort()
            head_counter = 0
            slot_counter = 0
            print(f'running thesis {i}-{i + block - 1}')

            while True:
                if time.time() - start > 2:
                    raise TimeoutError

                if len(head_of_committee_list) <= head_counter:
                    slot_counter = 0
                    head_counter = 0
                    continue

                # head_of_committee = head_of_committee_list[head_counter]
                head_of_committee = random.choice(head_of_committee_list)

                if len(head_of_committee.available_slots) < block * slots_to_assign or len(
                        head_of_committee.assigned_slots) >= self.max_slots_per_employee:
                    head_of_committee_list.remove(head_of_committee)
                    slot_counter = 0
                    continue

                if len(head_of_committee.available_slots) < (slot_counter + block) * slots_to_assign:
                    slot_counter = 0
                    head_counter += 1
                    continue

                slots = head_of_committee.available_slots[slot_counter:(slot_counter + block) * slots_to_assign]

                if len(set([b - a for a, b in zip(slots[:-1], slots[1:]) if b - a != 15])) != 1:
                    # todo dynamically read break
                    slot_counter += 1
                    continue

                compatible_committee_members = [committee_member for committee_member in committee_member_list
                                                if all(
                        slot in [x.id for x in committee_member.available_slots] for slot in
                        [x.id for x in slots]) and len(
                        committee_member.assigned_slots) <= (self.max_slots_per_employee - block) * slots_to_assign]

                if len(compatible_committee_members) < 2:
                    slot_counter += 1
                    continue

                # compatible_committee_members = compatible_committee_members[:2]
                compatible_committee_members = random.sample(compatible_committee_members, 2)

                for j, slot in enumerate(slots):
                    if i + j > len(thesis) - 1:
                        continue

                    if slots_to_assign == 2 and j % 2 == 1:
                        continue

                    thesis[i + j].slot = slot
                    thesis[i + j].head_of_committee = head_of_committee
                    thesis[i + j].committee_members = compatible_committee_members

                    head_of_committee.assigned_slots.append(slot)
                    head_of_committee.available_slots.remove(slot)

                    if slots_to_assign == 2:
                        # todo problem here, but only sometimes (STILL OCCURRING)
                        slot_2 = get_by_id(slots, slot.id + 1)
                        head_of_committee.assigned_slots.append(slot_2)
                        head_of_committee.available_slots.remove(slot_2)
                    for member in compatible_committee_members:
                        member.assigned_slots.append(slot)
                        member.available_slots.remove(get_by_repr(member.available_slots, slot))
                        if slots_to_assign == 2:
                            member.assigned_slots.append(slot_2)
                            member.available_slots.remove(get_by_repr(member.available_slots, slot_2))

                # for member in compatible_committee_members:
                #     committee_member_list.remove(member)
                # head_of_committee_list.remove(head_of_committee)

                break
