from gbdvalidation.engine import EmptyNoneMunch
from datetime import datetime


def get_dates():
    today = datetime.now().strftime('%Y-%m-%d')
    begin_of_time = datetime.strptime('1800-01-01', '%Y-%m-%d').strftime('%Y-%m-%d')
    return today, begin_of_time

def demunch_filter(data):
    if isinstance(data, list):
        new_data = []
        for el in data:
            new_data.append(demunch_filter(el))
        return new_data
    if isinstance(data, EmptyNoneMunch):
        new_data = {}
        for key in list(data.keys()):
            new_data[key] = demunch_filter(data[key])
        return new_data
    return data

def istrademark(brand):
    return brand.type == 'TRADEMARK'

def exists(value):
    return bool(value)

def eachexists(lst, key=None):
    return all(bool(value) for value in lst)

def anyexists(lst):
    return any(bool(value) for value in lst)

def length(value, nb):
    if not value:
        return True
    else:
        return len(value) == nb

def length_min(value, nb):
    if not value:
        return True
    else:
        return len(value) >= nb

def equals(value, *vals):
    if not value:
        return True
    return value in vals

def nequals(value, *vals):
    if not value:
        return True
    return not(value in vals)

def eachshorterthan(lst, limit):
    if not lst:
        return True
    for langs in lst:
        if not langs:
            continue
        for terms in langs.values():
            for term in terms:
                if len(term) > limit:
                    return False
    return True

# all values of list
def eachequals(lst, *vals):
    if not lst:
        return True

    # for l in lst:
    #     if not l in vals:
    #         print(l)

    return all(value in vals or not value for value in lst)

# pluck values from a list of dicts
def pluck(lst, key):
    if not lst:
        return []
    return [item.get(key, None) for item in lst if isinstance(item, dict)]

def concat(lsta, lstb):
    return (lsta or []) + (lstb or [])

def flatten(list_of_lists):
    to_return = []
    for el in list_of_lists or []:
        if el:
            to_return.extend(el)
    return to_return

# if these then that
def ifttt(_, *rules):
    preconditions = all(cond for cond in rules[:-1])
    # not all preconditions qualify
    if not preconditions:
        return True

    return rules[-1]

# date helpers
def ispast(value):
    today, begin_of_time = get_dates()
    if not value:
        return True
    return begin_of_time <= value <= today

def isfuture(value):
    today, begin_of_time = get_dates()
    if not value:
        return True
    return value > today


def isafter(value1, value2):
    if not value1:
        return True
    if not value2:
        return True
    return value1 >= value2
