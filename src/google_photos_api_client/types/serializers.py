__all__ = ['to_dict']

from enum import Enum

JSON_DATA_TYPES = [str, int, float, None, list, tuple, dict]


def to_dict(obj):
    """Creates a dictionary from an object. The dictionary will only have
    JSON types so it can be easily serialized to JSON string.

    FIXME: key translation from snake case to camel case is missing
    """
    data = {}

    for key, value in obj.__dict__.items():
        # We don't save None values in the dict
        if value is None:
            continue

        # For the primitive types, we just save them
        if type(value) in JSON_DATA_TYPES:
            data[key] = value
        # For enum types, we save the value part in the dict
        elif issubclass(type(value), Enum):
            data[key] = value.value
        # We expect that all other types have a __dict__ method
        else:
            data[key] = to_dict(value)

    return data
