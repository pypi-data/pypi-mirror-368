from __init__ import *
from strings import *


def colour_check(test_string: str) -> str:
    """
    Removes ascii colouration from a given string
    :param test_string: a string
    :return: a string without ascii colouration
    """
    if not isinstance(test_string, BetterString):
        test_string = BetterString(test_string)
    while "" in test_string:
        esc_index = list(test_string).index("")
        del test_string[esc_index, list(test_string).index("m", esc_index)+1]
    return str(test_string)
