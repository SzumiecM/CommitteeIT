import copy


def get_by_repr(list_, y):
    return [x for x in list_ if x.__repr__() == y.__repr__()].pop()


def get_by_id(list_, id_):
    # todo maybe replace with some clever lambda
    return [x for x in list_ if x.id == id_].pop()


def assign_employees(thesis, employees):
    thesis, employees = copy.deepcopy(thesis), copy.deepcopy(employees)

    thesis.head_of_committee = get_by_repr(employees, thesis.head_of_committee)

    thesis.head_of_committee.available_slots.remove(
        get_by_repr(thesis.head_of_committee.available_slots, thesis.slot))
    thesis.head_of_committee.assigned_slots.append(thesis.slot)
    if not thesis.individual:
        thesis.head_of_committee.assigned_slots.append(
            get_by_id(thesis.head_of_committee.available_slots, thesis.slot.id + 1))
        thesis.head_of_committee.available_slots.remove(
            get_by_id(thesis.head_of_committee.available_slots, thesis.slot.id + 1))

    for member in thesis.committee_members:
        member = get_by_repr(employees, member)
        member.available_slots.remove(get_by_repr(member.available_slots, thesis.slot))
        member.assigned_slots.append(thesis.slot)
        if not thesis.individual:
            member.assigned_slots.append(get_by_id(member.available_slots, thesis.slot.id + 1))
            member.available_slots.remove(get_by_id(member.available_slots, thesis.slot.id + 1))

    return thesis, employees
