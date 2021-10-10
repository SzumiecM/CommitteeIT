from xlsx_reader import EmployeesReader, ThesisReader
from committee_assembler import CommitteeAssembler

employee_reader = EmployeesReader('pracownicy.xlsx')
thesis_reader = ThesisReader('prace.xlsx')

thesis_reader.map_employees(employee_reader.employees)

assembler = CommitteeAssembler(
    thesis=thesis_reader.thesis,
    employees=employee_reader.employees,
    slots=employee_reader.slots,
    max_thesis_per_slot=5,
    population_count=100
)

assembler.create_initial_population()
assembler.calculate_fitness()
assembler.select_parents()
assembler.crossover()
