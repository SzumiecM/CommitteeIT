from xlsx_reader import EmployeesReader, ThesisReader
from genetic_assembler import GeneticAssembler
# from heuristic_assembler import HeurisiticAssebler

employee_reader = EmployeesReader('pracownicy.xlsx')
thesis_reader = ThesisReader('prace.xlsx')

thesis_reader.map_employees(employee_reader.employees)

assembler = GeneticAssembler(
    thesis=thesis_reader.thesis,
    employees=employee_reader.employees,
    slots=employee_reader.slots,
    max_thesis_per_slot=5,
    population_count=20,
    iteration_count=10,
    max_slots_per_employee=True
)

assembler.assemble()
