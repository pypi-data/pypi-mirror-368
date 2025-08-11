import ast
from typing import List

from rastless.custom_exceptions import ColorMapParseError


def parse_string_colors(colors: str):
    try:
        parsed_list = ast.literal_eval(colors)
    except SyntaxError:
        raise ColorMapParseError(
            'colors list could not be parsed, needs to be in the following format: "[[int,int,int,int]]"'
        )
    for item in parsed_list:
        if not len(item) == 4:
            raise ColorMapParseError(
                f"colors list could not be parsed, every item needs to be a list of 4 integers "
                f"representing rgba, but instead one item had a length of {len(item)}"
            )
        for num in item:
            if not isinstance(num, int):
                raise ColorMapParseError(
                    f"colors list could not be parsed, every item needs to be a list of 4 integers "
                    f"representing rgba, but instead one item was of type{type(item)}"
                )
    return parsed_list


def parse_string_values(values: str) -> List[int]:
    try:
        parsed_list = ast.literal_eval(values)
    except SyntaxError:
        raise ColorMapParseError('values list could not be parsed, needs to be in the following format: "[int,int]"')
    for item in parsed_list:
        if not isinstance(item, int):
            raise ColorMapParseError('values list could not be parsed, all elements have to be integers: "[int,int]"')
    return parsed_list


def parse_string_labels(labels):
    try:
        parsed_list = ast.literal_eval(labels)
    except ValueError:
        raise ColorMapParseError(
            'labels list could not be parsed, needs to be in the following format: "["str","str"]"'
        )
    for item in parsed_list:
        if not isinstance(item, str):
            raise ColorMapParseError(
                'labels list could not be parsed, all elements have to be strings: "["str","str"]"'
            )
    return parsed_list
