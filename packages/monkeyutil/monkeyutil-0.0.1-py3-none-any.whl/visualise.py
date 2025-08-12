from colours import *


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
