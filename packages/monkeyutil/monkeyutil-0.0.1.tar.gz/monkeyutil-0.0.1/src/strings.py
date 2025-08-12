from __init__ import *
from randomness import *


def delete(string, index1, index2=None):
    letters = list(string)
    if index2:
        del letters[index1:index2]
    else:
        del letters[index1]
    return list_to_string(letters)


class BetterString(str):
    def __init__(self, value):
        super().__init__()
        if isinstance(value, list):
            self.value = list_to_string(value)
        else:
            self.value = str(value)

    def __delitem__(self, key):
        data = list(self.value)
        del data[key]
        self.value = list_to_string(data)

    def __delslice__(self, i, j):
        data = list(self.value)
        del data[i:j]
        self.value = list_to_string(data)

    def jumble(self):
        self.value = jumble(self.value)
