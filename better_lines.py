import numpy as np

def filter_lines(lines, h , w):
    vertical = {}
    horizontal = {}
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(x1 - x2) < 8:
            line[0][1] = 0
            line[0][3] = h
            vertical = vertical_line(line, vertical)
        elif abs(y1 - y2) < 8:
            line[0][0] = 0
            line[0][2] = w
            horizontal = horizontal_line(line, horizontal)

    sorted_lines = sort_lines(vertical, horizontal)
    return sorted_lines

def vertical_line(line, vertical):
    keys = vertical.keys()
    if len(keys) == 0:
        vertical[line[0][0]] = [list(line[0])]
    else:
        for key in vertical:
            if abs(key - line[0][0]) < 22:
                vertical[key].append(list(line[0]))
                return vertical

        vertical[line[0][0]] = [list(line[0])]
    return vertical

def horizontal_line(line, horizontal):
    keys = horizontal.keys()
    if len(keys) == 0:
        horizontal[line[0][1]] = [list(line[0])]
    else:
        for key in horizontal:
            if abs(key - line[0][1]) < 22:
                horizontal[key].append(list(line[0]))
                return horizontal

        horizontal[line[0][1]] = [list(line[0])]
    return horizontal

def sort_lines(vertical, horizontal):
    sorted_lines = []
    for key in vertical:
        lines = vertical[key]
        if lines != None:
            sorted_lines.append(np.mean(lines, axis=0).astype(np.int64))
    for key in horizontal:
        lines = horizontal[key]
        sorted_lines.append(np.mean(lines, axis=0).astype(np.int64))

    return sorted_lines