from .assembler import GeneticAssembler


class GeneticHybridAssembler(GeneticAssembler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.assembler_name = 'hybrid'

    def create_initial_population(self):
        for i in range(self.population_count):
            self.create_initial_individual_heuristically()
