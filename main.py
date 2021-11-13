from assemblers.assembler import Assembler
from assemblers.genetic_hybrid_assembler import GeneticHybridAssembler
from xlsx_components.xlsx_reader import EmployeesReader, ThesisReader
from assemblers.genetic_only_assembler import GeneticOnlyAssembler
from assemblers.heuristic_assembler import HeuristicAssembler
from multiprocessing import Process, Manager

from xlsx_components.xlsx_writer import XlsxWriter


def assemble_in_process(assembler: Assembler, return_dict):
    assembler.assemble()
    return_dict[assembler.assembler_name] = assembler


if __name__ == '__main__':
    employee_reader = EmployeesReader('files\\pracownicy.xlsx')
    thesis_reader = ThesisReader('files\\prace.xlsx')

    thesis_reader.map_employees(employee_reader.employees)

    assembler_params = {
        'thesis': thesis_reader.thesis,
        'employees': employee_reader.employees,
        'employees_per_slot': 3,
        'population_count': 20,
        'max_slots_per_employee': True,
        'max_thesis_per_slot': 5
    }

    genetic_params = {
        'iteration_count': 30,
        'parents_percent': 1,
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

    return_dict = Manager().dict()
    processes = []
    for assembler in assemblers:
        p = Process(target=assemble_in_process, args=(assembler, return_dict))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    xlsx_writer = XlsxWriter('files\\prace.xlsx')
    xlsx_writer.write(return_dict['genetic'].populations[0])
    xlsx_writer.write(return_dict['hybrid'].populations[0])
