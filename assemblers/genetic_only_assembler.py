import copy
from typing import List

from .assembler import GeneticAssembler
from models import Population, Thesis, Employee


class GeneticOnlyAssembler(GeneticAssembler):
    def __init__(self, thesis: List[Thesis], employees: List[Employee], employees_per_slot: int,
                 population_count: int, iteration_count: int, max_slots_per_employee: bool, max_thesis_per_slot: int,
                 parents_percent: float, population_mutation_percent: float, thesis_mutation_percent: float, window_queue=None):
        super().__init__(
            thesis=thesis,
            employees=employees,
            employees_per_slot=employees_per_slot,
            population_count=population_count,
            iteration_count=iteration_count,
            max_slots_per_employee=max_slots_per_employee,
            max_thesis_per_slot=max_thesis_per_slot,
            parents_percent=parents_percent,
            population_mutation_percent=population_mutation_percent,
            thesis_mutation_percent=thesis_mutation_percent,
            window_queue=window_queue
        )

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
