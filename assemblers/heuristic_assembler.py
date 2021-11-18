import time

from config import TRANSLATE, TRANSLATIONS
from .assembler import Assembler


class HeuristicAssembler(Assembler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
            'progress_msg': f'{TRANSLATIONS["ALGORITHMS"]["heuristic"] if TRANSLATE else "heuristic"} 1/1 ({self.populations[0].fitness})'
        })
        self.save_results()
