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
    delta = abs(range) * 0.1 if abs(range) > 0 else 0.001
    max_r = max + delta
    min_r = min - delta
    return min_r, max_r
