ALGORITHMS = ('heuristic', 'hybrid', 'genetic')
GENETIC = ('hybrid', 'genetic')

ASSEMBLER_PARAMS = {
    'employees_per_slot': {
        'type': int,
        'min': 1,
        'default': 3
    },
    'population_count': {
        'type': int,
        'min': 1,
        'default': 20
    },
    'max_slots_per_employee': {
        'type': bool,
        'default': 1
    },
    'max_thesis_per_slot': {
        'type': int,
        'min': 1,
        'default': 5
    }
}

GENETIC_PARAMS = {
    'iteration_count': {
        'type': int,
        'min': 1,
        'default': 30
    },
    'parents_percent': {
        'type': float,
        'min': 0.1,
        'max': 1.0,
        'default': 0.6
    },
    'population_mutation_percent': {
        'type': float,
        'min': 0.1,
        'max': 1.0,
        'default': 0.8
    },
    'thesis_mutation_percent': {
        'type': float,
        'min': 0.1,
        'max': 1.0,
        'default': 0.2
    }
}
