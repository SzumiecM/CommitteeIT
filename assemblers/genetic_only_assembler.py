import copy
import random
import statistics
import time
import matplotlib.pyplot as plt
from typing import List

from .assembler import Assembler, GeneticAssembler
from utils import get_by_repr, get_by_id, assign_employees
from models import Population, Thesis, Employee


class GeneticOnlyAssembler(GeneticAssembler):
    def __init__(self, thesis: List[Thesis], employees: List[Employee], employees_per_slot: int,
                 population_count: int, iteration_count: int, max_slots_per_employee: bool, max_thesis_per_slot: int,
                 parents_percent: float, population_mutation_percent: float, thesis_mutation_percent: float):
        super().__init__(thesis, employees, employees_per_slot, population_count, iteration_count,
                         max_slots_per_employee, max_thesis_per_slot, parents_percent, population_mutation_percent,
                         thesis_mutation_percent)

        self.assembler_name = 'genetic'

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
