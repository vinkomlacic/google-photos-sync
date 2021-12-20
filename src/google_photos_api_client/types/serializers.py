__all__ = ['to_dict']

from typing import Sequence

JSON_DATA_TYPES = [str, int, float, None, Sequence, dict]


def to_dict(obj):
    """Creates a dictionary from an object. The dictionary will only have
    JSON types so it can be easily serialized to JSON string.

    FIXME: key translation from snake case to camel case is missing
    """
    data = {}

    for key, value in obj.__dict__.items():
        if type(value) not in JSON_DATA_TYPES:
            data[key] = to_dict(value)
        else:
            data[key] = value

    return data
