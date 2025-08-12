import random
from __init__ import *


def cost_random(dictionary: dict, total_cost: int) -> list:
    """
    randomly picks from a dictionary based on costs
    :param dictionary: A dictionary where the keys are the items (to be 'purchased') and the values are their cost
    :param total_cost: An integer of the total cost to spend
    :return: a list of selected items
    """
    final = []
    menu = invert(dictionary)
    while total_cost > 0:
        price = random.randint(1, total_cost)
        if price in menu:
            final.append(random.choice(menu[price]))
            total_cost -= price
        if min(menu) > total_cost:
            break
    return final


def jumble(string: str) -> str:
    """
    randomises the position of each character in a string
    :param string: a string
    :return: a string
    """
    string_list = list(string)
    random.shuffle(string_list)
    return list_to_string(string_list)