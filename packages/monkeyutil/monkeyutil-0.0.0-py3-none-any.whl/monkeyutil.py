import random


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


def columns(column_data: list) -> str:
    """
    ONLY WORKS WITH MONOSPACED FONTS
    returns a string that converts the list into columns
    :param column_data: a list, each item on the list is a column,
    if the item is a list then each of those items are rows
    :return: a string
    """
    all_lines = ""
    width = 0
    height = 0
    for column in column_data:
        if len(column) > height:
            height = len(column)
        for row in column:
            length = len(colour_check(row))
            if length > width:
                width = length
    width += 4
    for a in range(0, height):
        current_line = "|"
        for b in column_data:
            try:
                # tests if there is an item on that line
                item = b[a]
            except IndexError:
                current_line += [" " for gap in range(0, width)] + "|"
            else:
                length = len(colour_check(item))
                spacing = (width - length)/2
                space = [" " for gap in range(0, int(spacing))]
                other_space = space
                if spacing != int(spacing):
                    other_space += " "
                current_line += space + b[a] + other_space + "|"
        if a < height-1:
            all_lines += current_line + "\n"
        else:
            all_lines += current_line
    return all_lines


def instance_of(item_to_search_for, iterable_object: iter) -> iter:
    """
    returns an iterable of all the appearances of an object within another iterable
    :param item_to_search_for: either a object to match with an element in the iterable object, or a list with multiple
    objects to match with list components
    :param iterable_object: an iterable object to search through
    :return: an iter() object of all items in the iterable_object parameter that match the item_to_search_for's value/s
    """
    if isinstance(item_to_search_for, list):
        for item in iterable_object:
            if item in item_to_search_for:
                yield item
    else:
        for item in iterable_object:
            if item_to_search_for == item:
                yield item


def query(text: str, data_type: str = "str", possible_outcomes: list = None):
    """
    data validates an input
    :param text: the text for the input function
    :param data_type: the data type for the response to be tested against. defaults to str, but choices include:
        - int: an integer.
        - strint: a string containing an integer.
        - flat: a string that has been stripped and lowered.
        - float: a float.
        - bool: a boolean (True if the response is y, true, or yes, returns False if the response is n, false, or no).
    :param possible_outcomes: A list of the possible outcomes, repeating the input until the user's response matches a
    specified outcome. all valid answer permitted if omitted
    :return: either an int, str, float, or bool dependant on parameters
    """
    response = input(text)
    data_type = data_type.lower()
    if data_type == "int" or data_type == "strint":
        try:
            response = int(response)
            if data_type == "strint":
                response = str(response)
        except ValueError:
            return query(text, "int", possible_outcomes)
    elif data_type == "flat":
        response = response.strip().lower()
    elif data_type == "float":
        try:
            response = float(response)
        except ValueError:
            return query(text, "float", possible_outcomes)
    elif data_type == "bool":
        if response in ["y", "true", 'yes']:
            return True
        elif response in ["n", "false", "no"]:
            return False
        else:
            return query(text, "bool")
    if possible_outcomes:
        if data_type == "flat":
            for item in possible_outcomes:
                possible_outcomes[possible_outcomes.index(item)].lower().strip()
        if response not in possible_outcomes:
            return query(text, data_type, possible_outcomes)
    return response


def any_in(database: iter, item_to_search_for) -> bool:
    """
    checks if an object is present in another object
    :param database: an iterable object
    :param item_to_search_for: an object to search for
    :return: Boolean True if item_to_search_for is in database, else False
    """
    for data_item in database:
        if data_item in item_to_search_for:
            return True
    return False


def list_to_string(array: list, spacer: str = "") -> str:
    """
    Converts a list into a string
    :param array: the list to convert
    :param spacer: a string object to go between each list object. defaults to nothing
    :return: a string version of the list
    """
    final = ""
    for a in array:
        final += str(a) + spacer
    return final


def int_flatten(int_or_float: (int, float)) -> (int, float):
    """
    If the given object is a float with no trailing numbers, converts it to a int object
    :param int_or_float: either an int or float object
    :return: either an int or float object, if it has trailing numbers after a decimal place returns a float,
    otherwise it returns an int
    """
    if str(int_or_float)[-2:] == ".0":
        return int(int_or_float)
    else:
        return float(int_or_float)


def invert(dictionary: dict, unique: bool = False) -> dict:
    """
    Flips a dictionary inside out, having the values as keys whose values are lists of all previous keys who shared
    that value. If unique is set to true, the the values are instead the last value in the dictionary
    :param dictionary: a dictionary object
    :param unique: Boolean
    :return: an inverted dictionary object (when compared to the given parameter)
    """
    final = {}
    if unique:
        for item in dictionary:
            final[dictionary[item]] = item
    else:
        for item in dictionary:
            try:
                final[dictionary[item]].append(item)
            except KeyError:
                final[dictionary[item]] = [item]
    return final


def max_array(dictionary: dict) -> list:
    """
    returns a list of all keys in the dictionary whose values are the greatest
    :param dictionary: a dictionary object where all values are numerical
    :return: a list object
    """
    max_num = dictionary[list(dictionary)[0]]
    for item in dictionary:
        if dictionary[item] > max_num:
            max_num = dictionary[item]
    final = []
    for item in dictionary:
        if dictionary[item] == max_num:
            final.append(item)
    return final


def value_list(dictionary: dict) -> list:
    """
    returns a list of all the values in a dictionary
    :param dictionary: a dictionary object
    :return: a list object
    """
    final = []
    for item in dictionary:
        final.append(dictionary[item])
    return final


def index(database: dict, index_of_item: int, get_value: bool = False):
    """
    gets the item at the specified index of an dictionary object
    :param database: a dictionary objects
    :param index_of_item: a positive integer
    :param get_value: if True, returns the value at the specified index, else returns the key. defaults to False
    :return: the key at the specified index
    """
    count = 0
    if index_of_item < 0:
        return False
    for a in database:
        if count == index_of_item:
            if get_value:
                return database[a]
            else:
                return a
        else:
            count += 1


def flatten(list_of_lists: list) -> list:
    """
    flattens a list of lists into a single list
    :param list_of_lists: a list
    :return: a list
    """
    final = []
    for nested_item in list_of_lists:
        if isinstance(nested_item, list):
            final.append(flatten(nested_item))
        else:
            final.append(nested_item)
    return final


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
