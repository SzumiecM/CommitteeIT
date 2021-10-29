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
    def __init__(self, thesis: List[Thesis], employees: List[Employee], slots: dict, employees_per_slot: int,
                 population_count: int):
        super().__init__(thesis, employees, slots, employees_per_slot, population_count)

        self.assembler_name = 'heuristic'

    def create_initial_population(self):
        for i in range(self.population_count):
            self.create_initial_population_heuristically()

    def assemble(self):
        self.create_initial_population()
        self.calculate_fitness()
        self.save_results()
