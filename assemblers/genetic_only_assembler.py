import copy

from .assembler import GeneticAssembler
from models import Individual


class GeneticOnlyAssembler(GeneticAssembler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

            self.population.append(Individual(thesis, employees))
