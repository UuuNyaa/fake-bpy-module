import os
import re
from typing import Tuple

SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_FILE)

INPUT_DATA_FILE = os.path.join(SCRIPT_DIR, "blender-4.0-data_types.txt")


## DataTypeRefiner


def OR(*args):
    if len(args) == 1:
        return args[0]
    return rf"""(?:{"|".join(rf"({arg})" for arg in args)})"""


def NAMED_OR(*args: Tuple[str, str]):
    return rf"""(?:{"|".join(rf"(?P<{n}>{t})" for n, t in args)})"""


NAME = r"[a-zA-Z_]\w*"
NAME_GRAVE_QUOTE = rf"`{NAME}`"

PRIMARY = rf"{NAME}(\.{NAME})*"

PRIMARY_GRAVE_QUOTE = rf"`{PRIMARY}`"
PRIMARY_SINGLE_QUOTE = rf"'{PRIMARY}'"


NONE = r"None"
ANY = r"[Aa]ny"
BOOL = OR(
    r"bool",
    r"boolean",
)
FLOAT = r"float"
INT = r"int"
STRING = OR(
    r"string",
    r"str",
)

CONTAINER_TYPE = OR(
    r"[Ll]ist",
    r"tuple",
    r"set",
    r"pair",
    r"sequence",
    r"`bpy_prop_collection`",
    r"`BMElemSeq`",
)

REF_RNA_ENUM = rf":ref:`rna_enum_\w+`"

ENUM_STRING = rf"'[\w-]+'"
ENUM_STRING_LIST = rf"\[{ENUM_STRING}(?:, {ENUM_STRING})*\]"
ENUM_LIST = OR(
    ENUM_STRING_LIST,
    REF_RNA_ENUM,
)
ENUM_IN = rf"enum in {ENUM_LIST}(?:, default {ENUM_STRING})?"

ENUM_STRING_SET = rf"{{{ENUM_STRING}(?:, {ENUM_STRING})*}}"
ENUM_SET = OR(
    ENUM_STRING_SET,
    REF_RNA_ENUM,
)
ENUM_SET_IN = rf"enum set in {ENUM_SET}(?:, default {ENUM_STRING_SET})?"

NUMBER_INT = OR(
    r"[-+]?\d+",
    r"[-+]?inf",
)

NUMBER_FLOAT = OR(
    r"[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?",
    r"[-+]?inf",
)

INT_RANGE = rf"\[{NUMBER_INT}, {NUMBER_INT}\]"
FLOAT_RANGE = rf"\[{NUMBER_FLOAT}, {NUMBER_FLOAT}\]"

FLOAT2 = rf"\({NUMBER_FLOAT}, {NUMBER_FLOAT}\)"
FLOAT3 = rf"\({NUMBER_FLOAT}, {NUMBER_FLOAT}, {NUMBER_FLOAT}\)"
FLOAT4 = rf"\({NUMBER_FLOAT}, {NUMBER_FLOAT}, {NUMBER_FLOAT}, {NUMBER_FLOAT}\)"

VECTOR2_IN = rf"`mathutils.Vector` of 2 items in {FLOAT_RANGE}(?:, default {FLOAT2})?"
VECTOR3_IN = rf"`mathutils.Vector` of 3 items in {FLOAT_RANGE}(?:, default {FLOAT3})?"
VECTOR4_IN = rf"`mathutils.Vector` of 4 items in {FLOAT_RANGE}(?:, default {FLOAT4})?"
COLOR3_IN = rf"`mathutils.Color` of 3 items in {FLOAT_RANGE}(?:, default {FLOAT3})?"
EULER3_IN = (
    rf"`mathutils.Euler` rotation of 3 items in {FLOAT_RANGE}(?:, default {FLOAT3})?"
)
QUATERNION4_IN = rf"`mathutils.Quaternion` rotation of 4 items in {FLOAT_RANGE}(?:, default {FLOAT4})?"

MATRIX33 = rf"\({FLOAT3}, {FLOAT3}, {FLOAT3}\)"
MATRIX33_IN = (
    rf"`mathutils.Matrix` of 3 \* 3 items in {FLOAT_RANGE}(?:, default {MATRIX33})?"
)

MATRIX44 = rf"\({FLOAT4}, {FLOAT4}, {FLOAT4}, {FLOAT4}\)"
MATRIX44_IN = (
    rf"`mathutils.Matrix` of 4 \* 4 items in {FLOAT_RANGE}(?:, default {MATRIX44})?"
)


INT_IN = rf"int in {INT_RANGE}(?:, default {NUMBER_INT})?"
FLOAT_IN = rf"float in {FLOAT_RANGE}(?:, default {NUMBER_FLOAT})?"

# rarely used
STRING_IN = rf"string in {ENUM_LIST}(?:, default {ENUM_STRING})?"

COLLECTION = rf"{CONTAINER_TYPE} of {NAME_GRAVE_QUOTE}"
NAMED_COLLECTION = rf"{PRIMARY_GRAVE_QUOTE} {COLLECTION}"

SIMPLE_TYPE_SPECIFIER = OR(
    NONE,
    ANY,
    BOOL,
    FLOAT,
    INT,
    STRING,
    # PRIMARY,
    PRIMARY_SINGLE_QUOTE,
    PRIMARY_GRAVE_QUOTE,
    COLLECTION,
    NAMED_COLLECTION,
)

SUM_TYPE = (
    rf"{SIMPLE_TYPE_SPECIFIER}(?:, {SIMPLE_TYPE_SPECIFIER})* or {SIMPLE_TYPE_SPECIFIER}"
)
TUPLE = rf"\({SIMPLE_TYPE_SPECIFIER}(?:, {SIMPLE_TYPE_SPECIFIER})*\)(?: pair)?"

TYPE_SPECIFIER = NAMED_OR(
    ("INT_IN", INT_IN),
    ("FLOAT_IN", FLOAT_IN),
    ("ENUM_IN", ENUM_IN),
    ("ENUM_SET_IN", ENUM_SET_IN),
    ("VECTOR2_IN", VECTOR2_IN),
    ("VECTOR3_IN", VECTOR3_IN),
    ("VECTOR4_IN", VECTOR4_IN),
    ("COLOR3_IN", COLOR3_IN),
    ("EULER3_IN", EULER3_IN),
    ("QUATERNION4_IN", QUATERNION4_IN),
    ("MATRIX33_IN", MATRIX33_IN),
    ("MATRIX44_IN", MATRIX44_IN),
    ("STRING_IN", STRING_IN),
    ("SUM_TYPE", SUM_TYPE),
    ("TUPLE", TUPLE),
    ("SIMPLE_TYPE_SPECIFIER", SIMPLE_TYPE_SPECIFIER),
    # PRIMARY,
)

HINT = OR(
    "readonly",
    "optional",
    "optional argument",
    "never None",
)

HINTS = rf"\({HINT}(?:, {HINT})*\)"

TYPE_QUALIFIER = OR(
    rf"{TYPE_SPECIFIER}(?:, {HINTS})?",
)

DATA_TYPE = OR(
    f"{TYPE_QUALIFIER}",
)

REGEX_DATA_TYPE = re.compile(DATA_TYPE)

print(DATA_TYPE)

with open(INPUT_DATA_FILE, "rt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        m = REGEX_DATA_TYPE.fullmatch(line)
        if m:
            # print(f"{[k for k, v in m.groupdict().items() if v is not None][0]}\t{line}")
            pass
        else:
            print(line)
