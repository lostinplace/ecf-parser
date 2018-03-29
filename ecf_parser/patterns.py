import re


structure = '''
CONTENTS = (PROPERTY|INTERNAL_ENTRY) +

ENTRY = { HEADER
  CONTENTS
}
'''


class Patterns:
    COMMENT = """^\s*#.*"""

    KEY = "[\w\d]+"
    VALUE = """(([\+\w\d\s\./-]+)|("[\+\w\d\s\./,-]+"))"""
    EMPTY = """^\s*$"""
    SIMPLE_PROPERTY = f"""({KEY}): ({VALUE})"""
    COMPLEX_PROPERTY = f"""{SIMPLE_PROPERTY}, ({SIMPLE_PROPERTY}(, )?)+"""
    EMPTY_PROPERTY = f"""({KEY}):"""
    PROPERTY = f"""({COMPLEX_PROPERTY})|({SIMPLE_PROPERTY})|({EMPTY_PROPERTY})"""
    NORMAL_HEADER = f"""( ({VALUE})(( {COMPLEX_PROPERTY})|( {SIMPLE_PROPERTY}))?)"""

    ENTRY_START = f"""^\{{({NORMAL_HEADER})?$"""
    PROPERTY_LINE = f"""^{PROPERTY}$"""
    ENTRY_END = f"""^}}$"""

    # ENTRY =
    #   ENTRY_START
    #   PROPERTY_LINE | ENTRY
    #   ENTRY_END

    @staticmethod
    def get_pattern_strings():
        property_names = [(p, re.compile(getattr(Patterns, p))) for p in dir(Patterns) \
                          if isinstance(getattr(Patterns, p), str)]
        return property_names

    @staticmethod
    def get_pattern_dict():
        return dict(Patterns.get_pattern_strings())


PATTERN_DICT = Patterns.get_pattern_dict()
LINE_PATTERN_KVS = list(
    filter(
        lambda x: x[0] in ("COMMENT", "PROPERTY_LINE", "ENTRY_START", "ENTRY_END"),
        PATTERN_DICT.items()
    )
)
LINE_PATTERN_DICT = dict(LINE_PATTERN_KVS)