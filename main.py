from assemblers.genetic_hybrid_assembler import GeneticHybridAssembler
from xlsx_reader import EmployeesReader, ThesisReader
from assemblers.genetic_only_assembler import GeneticOnlyAssembler
from assemblers.heuristic_assembler import HeuristicAssembler

employee_reader = EmployeesReader('pracownicy.xlsx')
thesis_reader = ThesisReader('prace.xlsx')

thesis_reader.map_employees(employee_reader.employees)

assembler_params = {
    'thesis': thesis_reader.thesis,
    'employees': employee_reader.employees,
    'employees_per_slot': 3,
    'population_count': 10,
    # todo CHECK MAX SLOTS PER EMPLOYEE
    'max_slots_per_employee': True,
    # todo CHECK IN HEURISTIC
    'max_thesis_per_slot': 5
}

genetic_assembler = GeneticOnlyAssembler(
    **assembler_params,
    iteration_count=10,
)

heuristic_assembler = HeuristicAssembler(
    **assembler_params
)

hybrid_assembler = GeneticHybridAssembler(
    **assembler_params,
    iteration_count=10
)

genetic_assembler.assemble()
heuristic_assembler.assemble()
hybrid_assembler.assemble()

genetic_assembler.save_results()
heuristic_assembler.save_results()
hybrid_assembler.save_results()
