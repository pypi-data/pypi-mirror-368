def _only_small_errors(a, b, e=1e-14):
    if hasattr(a, "__iter__"):
        for i in range(len(a)):
            if abs(a[i] - b[i]) > e:
                return False
    elif abs(a - b) > e:
        return False
    return True
