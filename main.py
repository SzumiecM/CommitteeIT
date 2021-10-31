from assemblers.genetic_hybrid_assembler import GeneticHybridAssembler
from xlsx_reader import EmployeesReader, ThesisReader
from assemblers.genetic_only_assembler import GeneticOnlyAssembler
from assemblers.heuristic_assembler import HeuristicAssembler
from multiprocessing import Process

if __name__ == '__main__':
    employee_reader = EmployeesReader('pracownicy.xlsx')
    thesis_reader = ThesisReader('prace.xlsx')

    thesis_reader.map_employees(employee_reader.employees)

    assembler_params = {
        'thesis': thesis_reader.thesis,
        'employees': employee_reader.employees,
        'employees_per_slot': 3,
        'population_count': 20,
        'max_slots_per_employee': True,
        # todo check in genetic during crossovers and stuff
        'max_thesis_per_slot': 5
    }

    genetic_params = {
        'iteration_count': 80,
        'parents_percent': 0.8,
        'population_mutation_percent': 0.8,
        'thesis_mutation_percent': 0.2
    }

    assemblers = [
        GeneticOnlyAssembler(
            **assembler_params,
            **genetic_params
        ),
        HeuristicAssembler(
            **assembler_params
        ),
        GeneticHybridAssembler(
            **assembler_params,
            **genetic_params
        )
    ]

    processes = []
    for assembler in assemblers:
        p = Process(target=assembler.assemble)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
