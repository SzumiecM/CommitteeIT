from assemblers.hybrid_assembler import HybridAssembler
from xlsx_reader import EmployeesReader, ThesisReader
from assemblers.genetic_assembler import GeneticAssembler
from assemblers.heuristic_assembler import HeuristicAssembler

employee_reader = EmployeesReader('pracownicy.xlsx')
thesis_reader = ThesisReader('prace.xlsx')

thesis_reader.map_employees(employee_reader.employees)

assembler_params = {
    'thesis': thesis_reader.thesis,
    'employees': employee_reader.employees,
    'employees_per_slot': 3,
    'population_count': 10,
    'max_slots_per_employee': True,
    'max_thesis_per_slot': 5
}

genetic_assembler = GeneticAssembler(
    **assembler_params,
    iteration_count=10,
)

heuristic_assembler = HeuristicAssembler(
    **assembler_params
)

hybrid_assembler = HybridAssembler(
    **assembler_params,
    iteration_count=10
)

# genetic_assembler.assemble()
# heuristic_assembler.assemble()
hybrid_assembler.assemble()
