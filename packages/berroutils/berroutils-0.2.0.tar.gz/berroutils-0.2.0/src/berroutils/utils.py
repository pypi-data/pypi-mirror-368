from math import isnan


def is_empty_or_nan(entry) -> bool:
    """check if entry is empty or nan"""

    if entry is None:
        return True
    if isinstance(entry, float):
        return True if isnan(entry) == True else False
    if isinstance(entry, str):
        return True if any([entry.strip() == "",
                            entry == "nan",
                            entry == "NAN"]) else False
    if isinstance(entry, int):
        return False
    if hasattr(entry, '__len__'):
        return True if len(entry) == 0 else False
    else:
        raise NotImplementedError(f"type {type(entry)} not yet implemented")
