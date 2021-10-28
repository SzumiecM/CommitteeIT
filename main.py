from xlsx_reader import EmployeesReader, ThesisReader
from assemblers.genetic_assembler import GeneticAssembler
from assemblers.heuristic_assembler import HeuristicAssembler

employee_reader = EmployeesReader('pracownicy.xlsx')
thesis_reader = ThesisReader('prace.xlsx')

thesis_reader.map_employees(employee_reader.employees)

assembler_params = {
    'thesis': thesis_reader.thesis,
    'employees': employee_reader.employees,
    'slots': employee_reader.slots,
    'employees_per_slot': 3
}

genetic_assembler = GeneticAssembler(
    **assembler_params,
    max_thesis_per_slot=5,
    population_count=20,
    iteration_count=10,
    max_slots_per_employee=True
)

heuristic_assembler = HeuristicAssembler(
    **assembler_params
)

# genetic_assembler.assemble()
heuristic_assembler.assemble()
