import copy
import random
import statistics
import time
import matplotlib.pyplot as plt
from typing import List

from .assembler import Assembler
from utils import get_by_repr, get_by_id, assign_to_thesis_heuristically
from models import Population, Thesis, Employee


class HeuristicAssembler(Assembler):
    def __init__(self, thesis: List[Thesis], employees: List[Employee], employees_per_slot: int,
                 population_count: int, max_slots_per_employee: bool, max_thesis_per_slot: int):
        super().__init__(thesis, employees, employees_per_slot, population_count, max_slots_per_employee,
                         max_thesis_per_slot)

        self.assembler_name = 'heuristic'

    def create_initial_population(self):
        for i in range(self.population_count):
            self.create_initial_population_heuristically()

    def assemble(self):
        global_start = time.time()
        self.create_initial_population()
        self.calculate_fitness()

        self.time_elapsed = round((time.time() - global_start) / 60, 2)
        self.save_results()
