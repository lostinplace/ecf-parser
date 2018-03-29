import typing
from os import path
import jsonpickle
from ecf_parser.utils import get_header_string, consume_ecf_line, get_property_string, parse_header_line, \
    read_ecf_lines, strip_whitespace




def parse_ecf_entry(ecf: str) -> 'Entry':
    if not isinstance(ecf, list):
        ecf = ecf.split("\n")

    current_entry = None
    for line in ecf:
        current_entry, entry_closed = consume_ecf_line(line, current_entry)
        if entry_closed:
            return current_entry

    raise ValueError("unterminated ecf block")


def entry_to_ecf(an_entry: 'Entry') -> str:
    header = get_header_string(an_entry)
    output_lines = [header]
    if hasattr(an_entry, "Properties"):
        for prop in an_entry.Properties:
            if isinstance(prop, dict):
                output_lines.append("  " + get_property_string(prop))
            if isinstance(prop, Entry):
                result = entry_to_ecf(prop)
                mapped = map(lambda x: "  " + x, result.split("\n"))
                output_lines = output_lines + list(mapped)
    output_lines.append("}")
    return "\n".join(output_lines)


class Entry:

    def __init__(self, header_dict=None):
        self.Id = None
        self.Name = None
        self.Ref = None
        self.Type = None
        if header_dict is not None: self.add_header(header_dict)

    def add_header(self, header_dict:typing.Dict[str, str]):
        if isinstance(header_dict, str):
            header_dict = utils.parse_header_line(header_dict)
        self.Id = header_dict.get("Id")
        self.Name = header_dict.get("Name")
        self.Ref = header_dict.get("Ref")
        self.Type = header_dict.get("Type")

    def add_property(self, property:typing.Union['Entry', typing.Dict[str, str]]):
        if not hasattr(self, "Properties"):
            self.Properties = [property]
        else:
            self.Properties.append(property)


def entries_from_ecf_file(file_path:str) -> typing.Generator[Entry, None, None]:
    file_path = path.abspath(file_path)
    with open(file_path, 'r') as f:
        lines = f.readlines()
        yield from read_ecf_lines(lines)


def entries_from_jsonl_file(file_path:str) -> typing.Generator[Entry, None, None]:
    file_path = path.abspath(file_path)
    with open(file_path, 'r') as f:
        lines = f.readlines()
        yield from map(jsonpickle.decode, lines)


def ecf_file_to_json(file_path) -> typing.Generator[str, None, None]:
    """
    reads an ecf file and converts it into json lines
    :param file_path:
    :return:
    """
    return map(jsonpickle.encode, entries_from_ecf_file(file_path))


def jsonl_file_to_ecf(file_path) -> typing.Generator[str, None, None]:
    """
    reads a json lines finle of entries and converts to ecf format
    :param file_path:
    :return:
    """

    return map(entry_to_ecf, entries_from_jsonl_file(file_path))


def print_ecf2json():
    import sys

    for line in ecf_file_to_json(sys.argv[1]):
        print(line)


def print_json2ecf():
    import sys

    for line in jsonl_file_to_ecf(sys.argv[1]):
        print(line)
