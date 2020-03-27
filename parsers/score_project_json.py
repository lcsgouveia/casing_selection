import re


class JSONTest:

    def __init__(self):
        self.input = None
        self.errors = None
        self.custom_scenarios = CustomScenariosDummy()


class CustomScenariosDummy:

    def __init__(self):
        pass

    def all(self):
        return None

def convert(s):
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return a.sub(r'_\1', s).lower()


def convert_json(j):
    out = {}
    for k in j:
        new_key = convert(k)
        if isinstance(j[k], dict):
            out[new_key] = convert_json(j[k])
        elif isinstance(j[k], list):
            out[new_key] = convert_array(j[k])
        else:
            out[new_key] = j[k]
    return out


def convert_array(a):
    new_array = []
    for i in a:
        if isinstance(i, list):
            new_array.append(convert_array(i))
        elif isinstance(i, dict):
            new_array.append(convert_json(i))
        else:
            new_array.append(i)
    return new_array