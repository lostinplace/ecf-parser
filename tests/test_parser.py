import json
import os

from ecf_parser.utils import strip_whitespace, get_header_string, \
    get_property_string, consume_ecf_line, parse_header_line, classify_line, \
    parse_property_line

from ecf_parser import entry_to_ecf, parse_ecf_entry, ecf_file_to_json, Entry,\
    jsonl_file_to_ecf

wd = os.getcwd()

basename = os.path.basename(wd)

sample_data_folder = 'sample-data/'
if basename == "tests":
    sample_data_folder = '../sample-data/'


def test_line_classifier_returns_null_on_garbage():
    result = classify_line("dsljdsfjhlsdkfj dsf")
    assert result is None


def test_classifies_all_lines_in_file_correctly():
    from os import path

    file_path = path.abspath(sample_data_folder + "Config_Example.ecf")

    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            result = classify_line(line)
            assert result is not None
            if result == "ENTRY_START":
                header_dict = parse_header_line(line)
                tmp = Entry(header_dict)
                header_line = get_header_string(tmp)
                assert strip_whitespace(line) == strip_whitespace(header_line)
                continue
            if result == "PROPERTY_LINE":
                tmp = parse_property_line(strip_whitespace(line))
                property_string = get_property_string(tmp)
                assert strip_whitespace(line) == strip_whitespace(property_string)


KNOWN_EXCEPTIONS = [
    # there's a rogue "category: ingredients" property in french fries
    lambda entry, ecf_block: entry.Id == "2424",
    # there's extra whitespace on the Zascosium alloy template
    lambda entry, ecf_block: entry.Type == "Template" and entry.Name == "ZascosiumAlloy",
    # there's extra whitespace on the Erestrum gel template
    lambda entry, ecf_block: entry.Type == "Template" and entry.Name == "ErestrumGel",
]


def test_constructs_entries_from_file():
    from os import path

    file_path = path.abspath(sample_data_folder + "Config_Example.ecf")

    with open(file_path, 'r') as f:
        lines = f.readlines()
        entry_count = 0
        expected_entry_count = 1421
        current_entry = None
        current_entry_lines = []
        for line in lines:
            current_entry, entry_closed = consume_ecf_line(line, current_entry)
            if current_entry is not None:
                current_entry_lines.append(line.rstrip(" \r\n"))
            if entry_closed:
                current_entry_lines_string = "\n".join(current_entry_lines)
                ecf_output = entry_to_ecf(current_entry)
                exceptions = filter(lambda x: x(current_entry, current_entry_lines_string), KNOWN_EXCEPTIONS)
                if not any(exceptions):
                    entry_count += 1
                    assert current_entry_lines_string == ecf_output
                current_entry = None
                current_entry_lines = list()

        assert entry_count == expected_entry_count - len(KNOWN_EXCEPTIONS)


def test_header_parse_sample():
    cases = [
        ("{ Item Id: 2393, Name: AntidoteInjection, Ref: FoodTemplate", "Item", "2393", "AntidoteInjection",
         "FoodTemplate"),
        ("{ Template Name: ContainerAmmoSmall", "Template", None, "ContainerAmmoSmall", None),
        ("{ Block Id: 950, Name: HoloScreen01", "Block", "950", "HoloScreen01", None),
        ("{ Block Id: 278, Name: GravityGeneratorMS", "Block", "278", "GravityGeneratorMS", None),
        ("{ Template Name: SlowRocketHoming", "Template", None, "SlowRocketHoming", None),
        ("{ Block Id: 1145, Name: TurretMSCannon", "Block", "1145", "TurretMSCannon", None),
        ("{ Block Id: 1444, Name: StairShapesShortWood, Ref: StairShapes", "Block", "1444", "StairShapesShortWood",
         "StairShapes"),
        ("{ Block Id: 711, Name: ConstructorSurvival", "Block", "711", "ConstructorSurvival", None),
        ("{ Block Id: 811, Name: Window_cr1x1, Ref: Window_v1x1", "Block", "811", "Window_cr1x1", "Window_v1x1"),
        ("{ Template Name: Fiber", "Template", None, "Fiber", None),
        ("{ Child Inputs ", "Child Inputs", None, None, None),
        ("{ ", None, None, None, None)
    ]

    for i in cases:
        header_dict = parse_header_line(i[0])
        tmp = Entry(header_dict)
        assert tmp.Type == i[1]
        assert tmp.Id == i[2]
        assert tmp.Name == i[3]
        assert tmp.Ref == i[4]
        roundtrip_string = get_header_string(tmp)
        assert i[0].strip() == roundtrip_string.strip()


def test_property_parse_sample():
    cases = [
        ("Target:", {"Name": "Target", "Value": None}),
        ("Tracer: Weapons/Projectiles/TracerOrange1",
         {"Name": "Tracer", "Value": "Weapons/Projectiles/TracerOrange1"}),
        ("Range: 4.5", {"Name": "Range", "Value": "4.5"}),
        ("Damage: 300", {"Name": "Damage", "Value": "300"}),
        ("DamageMultiplier_1: 0.01, data: wood",
         {"Name": "DamageMultiplier_1", "Value": "0.01", "Attributes": {"data": "wood"}}),
        ("DamageMultiplier_1: 3.5, data: head, display: DmgMultiplierHead",
         {"Name": "DamageMultiplier_1", "Value": "3.5",
          "Attributes": {"data": "head", "display": "DmgMultiplierHead"}}),
        ('Target: "SurvC,SmallC,LargeC,AdvC,Furn"',
         {"Name": "Target", "Value": "SurvC,SmallC,LargeC,AdvC,Furn"}),
        ("EnergyIn: 10, type: int, display: true, formatter: Watt",
         {"Name": "EnergyIn", "Value": "10", "Attributes": {"type": "int", "display": "true", "formatter": "Watt"}}),
    ]

    import json
    for i in cases:
        tmp = parse_property_line(i[0])
        assert json.dumps(tmp) == json.dumps(i[1])
        prop_line = get_property_string(tmp)
        assert i[0].strip() == prop_line.strip()


simple_ecf_blocks = [
    """{ Block Id: 256, Name: CapacitorMS
  Material: metal
  ShowBlockName: true
  IsAccessible: false, type: bool
  Info: bkiGenNoFunction, display: true
  StackSize: 5
  TemplateRoot: DecoBlocks2
  Mass: 200, type: int, display: true, formatter: Kilogram
  EnergyIn: 1, type: int, display: true, formatter: Watt
  Category: Deco Blocks
  BlastRadius: 3
  BlastDamage: 100
}""",
    """{ Item Id: 2424, Name: FrenchFries, Ref: FoodTemplate
  Category: Food
  {
    Category: Ingredients
    ROF: 1, type: float
    AddHealth: 24, display: HealthValue
    AddStamina: 6, display: StaminaValue
    AddFood: 91, display: FoodValue
    AddOxygen: 0
  }
}""",
    """{ Template Name: ZascosiumAlloy
  OutputCount: 1
  CraftTime: 5
  Target: AdvC
  { Child Inputs
    ErestrumIngot: 5
    ZascosiumIngot: 5
  }
}""",
    """{ Template Name: ErestrumGel
  OutputCount: 1
  CraftTime: 5
  Target: AdvC
  { Child Inputs
    ErestrumIngot: 2
  }
}""",
]


def test_ecf_entry_roundtrip():
    for block in simple_ecf_blocks:
        entry = parse_ecf_entry(block)
        to_ecf = entry_to_ecf(entry)
        assert block == to_ecf


def test_ecf_file_to_json():
    for v in ecf_file_to_json(sample_data_folder + 'Config_Example.ecf'):
        tmp = json.loads(v)
        assert tmp is not None


def test_json_file_to_ecf():
    for v in jsonl_file_to_ecf(sample_data_folder + 'config_example.jsonl'):
        header = v.split("\n")[0]

        assert classify_line(header) == "ENTRY_START"
