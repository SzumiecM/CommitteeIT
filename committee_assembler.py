from typing import List

from models import Thesis, Employee, Slot


class CommitteeAssembler:
    def __init__(self, thesis: List[Thesis], employees: List[Employee], slots: List[Slot],
                 max_thesis_per_slot: int):
        self.thesis = thesis
        self.employees = employees
        self.slots = slots
        self.max_thesis_per_slot = max_thesis_per_slot

        self.population = None

    def create_initial_population(self):
        pass

    def calculate_fitness(self):
        pass

    def select_parents(self):
        pass

    def crossover(self):
        pass

    def mutate(self):
        pass
