import time
from typing import List

from .assembler import Assembler
from models import Thesis, Employee


class HeuristicAssembler(Assembler):
    def __init__(self, thesis: List[Thesis], employees: List[Employee], employees_per_slot: int,
                 population_count: int, max_slots_per_employee: bool, max_thesis_per_slot: int, window_queue=None):
        super().__init__(
            thesis=thesis,
            employees=employees,
            employees_per_slot=employees_per_slot,
            population_count=population_count,
            max_slots_per_employee=max_slots_per_employee,
            max_thesis_per_slot=max_thesis_per_slot,
            window_queue=window_queue
        )

        self.assembler_name = 'heuristic'

    def create_initial_population(self):
        for i in range(self.population_count):
            self.create_initial_population_heuristically()

    def assemble(self):
        global_start = time.time()
        self.create_initial_population()
        self.calculate_fitness()

        self.time_elapsed = round((time.time() - global_start) / 60, 2)
        self.window_queue.put({
            'assembler_name': self.assembler_name,
            'best_population': self.populations[0],
            'iteration_count': '1/1'
        })
        self.save_results()
