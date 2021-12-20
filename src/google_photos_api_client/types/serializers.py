__all__ = ['to_dict']

from enum import Enum

JSON_DATA_TYPES = [str, int, float, None, list, tuple, dict]


def to_dict(obj):
    """Creates a dictionary from an object. The dictionary will only have
    JSON types so it can be easily serialized to JSON string.
    """
    data = {}

    for key, value in obj.__dict__.items():
        # We don't save None values in the dict
        if value is None:
            continue

        camel_case_key = snake_case_to_camel_case(key)

        # For the primitive types, we just save them
        if type(value) in JSON_DATA_TYPES:
            data[camel_case_key] = value
        # For enum types, we save the value part in the dict
        elif issubclass(type(value), Enum):
            data[camel_case_key] = value.value
        # We expect that all other types have a __dict__ method
        else:
            data[camel_case_key] = to_dict(value)

    return data


def snake_case_to_camel_case(snake_case: str):
    # Splitting snake case string into words
    words = snake_case.split('_')

    # Capitalizing every word except the first one and adding the first word at the beginning
    camel_case = words[0] + ''.join(word.capitalize() for word in words[1:])

    return camel_case
