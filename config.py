ALGORITHMS = ('heuristic', 'hybrid', 'genetic')
GENETIC = ('hybrid', 'genetic')

ASSEMBLER_PARAMS = {
    'employees_per_slot': {
        'type': int,
        'min': 1
    },
    'population_count': {
        'type': int,
        'min': 1
    },
    'max_slots_per_employee': {
        'type': int,
        'min': 1
    },
    'max_thesis_per_slot': {
        'type': int,
        'min': 1
    }
}

GENETIC_PARAMS = {
    'iteration_count': {
        'type': int,
        'min': 1
    },
    'parents_percent': {
        'type': float,
        'min': 0.1,
        'max': 1.0
    },
    'population_mutation_percent': {
        'type': float,
        'min': 0.1,
        'max': 1.0
    },
    'thesis_mutation_percent': {
        'type': float,
        'min': 0.1,
        'max': 1.0
    }
}
