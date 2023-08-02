def update_dict(d1: dict, d2: dict):
    """
    Updates dictionary 1 with dictionary 2 without overwriting the sub dictionaries.

    Stolen from https://stackoverflow.com/questions/22093793/generic-way-of-updating-python-dictionary-without-overwriting-the-subdictionarie
    """
    c = d1.copy()
    for key in d2:
        if key in d1:c[key].update(d2[key])
        else:c[key] = d2[key]
    return c