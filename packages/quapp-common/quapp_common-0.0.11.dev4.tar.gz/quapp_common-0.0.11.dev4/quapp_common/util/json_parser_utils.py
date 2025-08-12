"""
    QApp Platform Project json_parser_utils.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from datetime import datetime
from enum import Enum

import numpy as np


def parse(unparsed_input):
    if isinstance(unparsed_input, (complex, datetime)):
        return unparsed_input.__str__()

    if isinstance(unparsed_input, (np.int64, np.int32)):
        return int(unparsed_input)

    if isinstance(unparsed_input, (Enum,)):
        return str(unparsed_input)

    if isinstance(unparsed_input,
                  (str, int, float, bool,)) or unparsed_input is None:
        return unparsed_input

    if isinstance(unparsed_input, (set, tuple)):
        return parse(list(unparsed_input))

    if isinstance(unparsed_input, np.ndarray):
        return parse(unparsed_input.tolist())

    if isinstance(unparsed_input, dict):
        data_holder = {}
        for key, value in unparsed_input.items():
            data_holder[key] = parse(value)
        return data_holder

    if isinstance(unparsed_input, (list,)):
        data_list_holder = []
        for data in unparsed_input:
            data = __resolve_type(data)
            data_list_holder.append(parse(data))
        return data_list_holder

    dir_obj = dir(unparsed_input)

    if dir_obj.__contains__('to_dict'):
        return parse(unparsed_input.to_dict())

    if dir_obj.__contains__('__dict__'):
        return parse(unparsed_input.__dict__)

    return unparsed_input.__str__()


def __resolve_type(element):
    if isinstance(element, (complex, datetime)):
        return element.__str__()

    if isinstance(element, (np.int64, np.int32)):
        return int(element)

    if isinstance(element,
                  (dict, str, int, float, bool, Enum)) or element is None:
        return element

    if isinstance(element, np.ndarray):
        return __resolve_type(element.tolist())
    if isinstance(element, slice):
        return str(element)
    if isinstance(element, (list, tuple,)):
        data_holder = []
        for data in element:
            data_holder.append(__resolve_type(data))
        return data_holder

    return element.__dict__
