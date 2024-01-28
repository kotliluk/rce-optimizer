from typing import Dict


def get_nested(d: Dict, path: str):
    """
    Returns value of the given path in the given dictionary.
    If the path does not exists, returns None.
    """
    if d is None:
        return None

    steps = path.split('.')
    cur = d

    for s in steps[:-1]:
        cur = cur.get(s, {})

    return cur.get(steps[-1])
