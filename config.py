import json

DEFAULT_EMPLOYEES_FILE = 'pracownicy.xlsx'
DEFAULT_THESIS_FILE = 'prace.xlsx'

ALGORITHMS = ('heuristic', 'hybrid', 'genetic')
GENETIC = ('hybrid', 'genetic')

with open('config.json') as f:
    file_json = json.load(f)


def replace_types(dict_):
    try:
        dict_.keys()
    except AttributeError:
        return dict_

    if 'type' in dict_.keys():
        type_ = dict_['type']
        if type_ == 'int':
            dict_['type'] = int
        elif type_ == 'float':
            dict_['type'] = float
        elif type_ == 'bool':
            dict_['type'] = bool
        else:
            raise ValueError('Wrong type provided in config.json')
        return dict_
    else:
        for k in dict_.keys():
            dict_[k] = replace_types(dict_[k])
        return dict_


file_json = replace_types(file_json)

READER_PARAMS = file_json['READER_PARAMS']
ASSEMBLER_PARAMS = file_json['ASSEMBLER_PARAMS']
GENETIC_PARAMS = file_json['GENETIC_PARAMS']
FITNESS_WEIGHTS = file_json['FITNESS_WEIGHTS']
TRANSLATE = file_json['TRANSLATE']
TRANSLATIONS = {
    "ALGORITHMS": {
        "heuristic": "heurystyczny",
        "hybrid": "hybrydowy",
        "genetic": "genetyczny"
    },
    "READER": {
        "slot_size": "Długość egzaminu (w minutach)",
        "break_time": "Długość przerwy (w minutach)",
        "slot_block": "Długość bloku egzaminów"
    },
    "ASSEMBLER": {
        "employees_per_slot": "Wielkość komisji (liczba pracowników)",
        "population_count": "Wielkość populacji (liczba zestawionych składów)",
        "max_slots_per_employee": "Maksymalna ilość egzaminów dla pracownika (1-Tak, 0-Nie)",
        "max_thesis_per_slot": "Maksymalna ilość egzaminów na jeden slot",
        "slot_block": "Długość bloku obron dla tego samego składu"
    },
    "GENETIC": {
        "iteration_count": "Liczba iteracji",
        "parents_percent": "Ułamek rodziców w populacji",
        "population_mutation_percent": "Ułamek populacji do mutacji",
        "thesis_mutation_percent": "Ułamek egzaminów do mutacji",
        "timeout": "Limit czasu przeprowadzania modyfikacji"
    }
}
