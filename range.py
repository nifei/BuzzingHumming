def calib_range(min, max, value):
    if max == None:
        max = value
    if min == None:
        min = value
    if max < value:
        max = value
    if min > value:
        min = value
    return min, max

def extend_range(min, max):
    range = max - min
    max_r = max + abs(range) * 0.1
    min_r = min - abs(range) * 0.1
    return min_r, max_r
