import copy
import random
import time


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


def assign_to_thesis_heuristically(thesis, head_of_committee_list, committee_member_list, block,
                                   slots_to_assign, max_slots_per_employee):
    for i in range(0, len(thesis), block):
        start = time.time()
        head_of_committee_list.sort()
        committee_member_list.sort()
        head_counter = 0
        slot_counter = 0
        # print(f'running thesis {i}-{i + block - 1}')

        while True:
            if time.time() - start > 1:
                raise TimeoutError

            if len(head_of_committee_list) <= head_counter:
                slot_counter = 0
                head_counter = 0
                continue

            # head_of_committee = head_of_committee_list[head_counter]
            head_of_committee = random.choice(head_of_committee_list)

            if len(head_of_committee.available_slots) < block * slots_to_assign or len(
                    head_of_committee.assigned_slots) >= max_slots_per_employee:
                head_of_committee_list.remove(head_of_committee)
                slot_counter = 0
                continue

            if len(head_of_committee.available_slots) < (slot_counter + block) * slots_to_assign:
                slot_counter = 0
                head_counter += 1
                continue

            slots = head_of_committee.available_slots[
                    slot_counter * slots_to_assign:(slot_counter + block) * slots_to_assign]

            if len(set([b - a for a, b in zip(slots[:-1], slots[1:]) if b - a != 15])) != 1:
                # todo dynamically read break
                slot_counter += 1
                continue

            compatible_committee_members = [committee_member for committee_member in committee_member_list
                                            if all(
                    slot in [x.id for x in committee_member.available_slots] for slot in
                    [x.id for x in slots]) and len(
                    committee_member.assigned_slots) <= (max_slots_per_employee - block) * slots_to_assign]

            if len(compatible_committee_members) < 2:
                slot_counter += 1
                continue

            # compatible_committee_members = compatible_committee_members[:2]
            compatible_committee_members = random.sample(compatible_committee_members, 2)

            for j, slot in enumerate(slots):
                if i + j > len(thesis) - 1:
                    continue

                if slots_to_assign == 2 and j % 2 == 1:
                    continue
                thesis[i + j].slot = slot
                thesis[i + j].head_of_committee = head_of_committee
                thesis[i + j].committee_members = compatible_committee_members

                head_of_committee.assigned_slots.append(slot)
                head_of_committee.available_slots.remove(slot)

                if slots_to_assign == 2:
                    if slot.id + 1 not in [slot.id for slot in slots]:
                        # todo continue also upper loop
                        raise TimeoutError

                    slot_2 = get_by_id(slots, slot.id + 1)
                    head_of_committee.assigned_slots.append(slot_2)
                    head_of_committee.available_slots.remove(slot_2)
                for member in compatible_committee_members:
                    member.assigned_slots.append(slot)
                    member.available_slots.remove(get_by_repr(member.available_slots, slot))
                    if slots_to_assign == 2:
                        member.assigned_slots.append(slot_2)
                        member.available_slots.remove(get_by_repr(member.available_slots, slot_2))

            # for member in compatible_committee_members:
            #     committee_member_list.remove(member)
            # head_of_committee_list.remove(head_of_committee)

            break
