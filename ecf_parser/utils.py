import typing

import ecf_parser
from ecf_parser.patterns import *


def strip_whitespace(line):
    return line.strip(' \t\n\r')


def value_formatter(value):
    if value is None:
        return ""
    if "," in value:
        return f'"{value}"'
    return value


def get_property_string(prop: dict):
    tmp = [
        (prop["Name"], value_formatter(prop["Value"]))
    ]

    attributes = prop.get("Attributes")
    if attributes:
        tmp = tmp + list(attributes.items())

    mapped = map(lambda x: f"{x[0]}: {x[1]}", tmp)
    result = ", ".join(mapped)
    return result.rstrip(" ")


def classify_line(line):
    clean_line = strip_whitespace(line)
    if clean_line == "":
        return "EMPTY"
    for k, v in LINE_PATTERN_DICT.items():
        match = v.fullmatch(clean_line)
        if match is not None:
            return k
    return None


def parse_empty_property_string(a_string):
    pattern = PATTERN_DICT["EMPTY_PROPERTY"]
    match = pattern.match(a_string)
    result ={
        "Name": match.group(1),
        "Value": None
    }
    return result


def parse_simple_property_string(a_string):
    pattern = PATTERN_DICT["SIMPLE_PROPERTY"]
    match = pattern.match(a_string)
    result = {
        "Name": match.group(1),
        "Value": match.group(2).strip('"')
    }
    return result


def parse_complex_property(a_string):
    pattern = PATTERN_DICT["SIMPLE_PROPERTY"]
    matches = pattern.findall(a_string)
    need_main_value = True
    result = dict()

    for m in matches:
        if need_main_value:
            result["Name"] = m[0]
            result["Value"] = m[1]
            need_main_value = False
        else:
            attributes = result.get("Attributes", dict())
            attributes[m[0]] = m[1]
            result["Attributes"] = attributes

    return result


def parse_property_line(line):
    pattern = LINE_PATTERN_DICT["PROPERTY_LINE"]
    full_match = pattern.fullmatch(line)

    # complex value groups: 1-13
    # simple value groups: 14-19
    # empty value group: 20

    if full_match.group(20):
        return parse_empty_property_string(full_match.group(20))

    if full_match.group(14):
        return parse_simple_property_string(full_match.group(14))

    return parse_complex_property(full_match.group(1))


def parse_header_line(line):
    line = strip_whitespace(line)
    normal_header_match = PATTERN_DICT["ENTRY_START"].fullmatch(line)
    result = dict()
    result["Type"] = normal_header_match.group(3)
    prop_string = normal_header_match.group(7)
    if prop_string is not None:
        prop_string = prop_string.strip()
        prop_pattern = PATTERN_DICT["SIMPLE_PROPERTY"]
        prop_matches = prop_pattern.findall(prop_string)
        for match in prop_matches:
            result[match[0]] = match[1]

    return result



def consume_ecf_line(line, entry=None) -> typing.Tuple['Entry', bool]:
    """
    consumes a line and adds it to the provided entry which can be none

    the boolean value represents whether the entry has seen an "ENTRY_END" signal, and should be considered closed
    """

    line = strip_whitespace(line)
    line_class = classify_line(line)
    if entry is not None:
        active_entry = entry if not hasattr(entry, "_active_child") else entry._active_child
    if line_class == "PROPERTY_LINE":
        prop = parse_property_line(line)
        active_entry.add_property(prop)
        return entry, False
    if line_class == "ENTRY_START":
        header_dict = parse_header_line(line)
        tmp_entry = ecf_parser.Entry(header_dict)
        if entry is None:
            return tmp_entry, False
        entry.add_property(tmp_entry)
        entry._active_child = tmp_entry
        return entry, False
    if line_class == "ENTRY_END":
        if active_entry is not entry:
            delattr(entry, "_active_child")
            return entry, False
        return entry, True
    return entry, False


def get_header_string(an_entry: 'ecf_parser.Entry'):
    type_string = an_entry.Type or ""
    props = []

    if an_entry.Id:
        props.append(f"Id: {an_entry.Id}")

    if an_entry.Name:
        props.append(f"Name: {an_entry.Name}")

    if an_entry.Ref:
        props.append(f"Ref: {an_entry.Ref}")

    prop_string = ", ".join(props)

    final_string = f"{{ {type_string} {prop_string}"

    return final_string.rstrip(" ")


def read_ecf_lines(ecf_lines) -> typing.Generator['Entry', None, None]:
    """
    Reads the lines from an ECF files and generates entries at the blocks close

    :param ecf_lines: the contents of a .ecf file
    :return: a generator of entries
    """
    if isinstance(ecf_lines, str):
        ecf_lines = ecf_lines.split("\n")

    current_entry = None

    for line in ecf_lines:
        current_entry, entry_closed = consume_ecf_line(line, current_entry)
        if entry_closed:
            yield current_entry
            current_entry = None

    if current_entry: raise ValueError("unterminated ecf block")