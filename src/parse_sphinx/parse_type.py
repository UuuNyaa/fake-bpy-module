import dataclasses
import logging
import os
from collections.abc import Collection, Sequence
from enum import IntFlag
import re
from types import NoneType
from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Set, Tuple, TypeGuard, Union
import typing

from parsy import Result, alt, char_from, eof, regex, seq, string
from parsy_utils import strings, strings_from_tuple
import parse_xml

_REGEX_SUB_TEXT_SPACES = re.compile(r"\s+")

_logger = logging.getLogger(__name__)


def parse_type(parse_xml_type: parse_xml.Type) -> "DataType":
    type_element_length = len(parse_xml_type.elements)
    if type_element_length == 0 and parse_xml_type.document_text is None:
        return RESULT_ANY
    if type_element_length == 1 and parse_xml_type.document_text is None:
        return data_types(_qualifier(parse_xml_type.elements[0].qualifier))

    normalized_document_text = document_text = _REGEX_SUB_TEXT_SPACES.sub(" ", parse_xml_type.document_text.strip())

    if type_element_length > 0:
        element_indices = sorted(
            ((e, i) for i, e in enumerate(parse_xml_type.elements)),
            key=lambda t: len(t[0].text),
            reverse=True,
        )

        for element, element_index in element_indices:
            regex_sub = re.compile(rf"\b{re.escape(element.text)}\b")
            if element.is_qualifier():
                new_normalized_document_text = regex_sub.sub(rf"<<<{element_index}>>>", normalized_document_text)
            elif element.is_reference():
                new_normalized_document_text = regex_sub.sub(rf"==={element_index}===", normalized_document_text)
            else:
                raise ValueError(f"Invalid element: {element}")

            if new_normalized_document_text == normalized_document_text:
                _logger.warning("Failed to replace element: %s", element)

            normalized_document_text = new_normalized_document_text

        if parse_xml_type.signature_text is not None:
            normalized_document_text = re.sub(
                rf"\b{re.escape(parse_xml_type.signature_text)}\b", r"!!!!!!", normalized_document_text
            )

    result: Result = DATA_TYPE_PARSER(normalized_document_text, 0)

    if not result.status:
        _logger.debug("Failed to parse type: %s", document_text)
        return RESULT_ANY

    data_type: DataType = result.value

    def replace(t: Any) -> Any:
        if isinstance(t, QualifierIndex):
            return _qualifier(element_indices[t.index][0].qualifier)
        elif isinstance(t, str):
            return _qualifier(t)
        elif isinstance(t, Qualifier):
            t.types = [replace(e) for e in t.types]
            return t
        elif isinstance(t, ReferenceIndex):
            return Any
        elif (o := typing.get_origin(t)) is not None:
            return o[*(replace(a) for a in typing.get_args(t))]
        elif isinstance(t, (type, bool)):
            return t

        raise ValueError(f"Invalid type: {t}")

    data_type.type = replace(data_type.type)
    return data_type


# Result types ##################################################################
class Qualifier:
    types: List[Any]

    def __init__(self, arg: Any, types: Optional[List[Any]] = None) -> "Qualifier":
        if types is None:
            self.types = []
        else:
            self.types = types

        self.types.append(arg)

    def __call__(self, arg: Any, *args: Any) -> "Qualifier":
        return Qualifier(arg if len(args) == 0 else (arg, *args), self.types.copy())

    def __repr__(self) -> str:
        return f"""{self.types[0]}{"".join(f"[{_get_name(t)}]" for t in self.types[1:])}"""


class QualifierIndex:
    index: int

    def __init__(self, index: int) -> "QualifierIndex":
        self.index = index

    def __repr__(self) -> str:
        return f"<<<{self.index}>>>"


class ReferenceIndex:
    index: int

    def __init__(self, index: int) -> "ReferenceIndex":
        self.index = index

    def __repr__(self) -> str:
        return f"==={self.index}==="


class Hint(IntFlag):
    NONE = 0
    READONLY = 1
    OPTIONAL = 2
    NEVER_NONE = 4

    @staticmethod
    def join(hints: Iterable["Hint"]) -> "Hint":
        result = Hint.NONE
        for h in hints:
            result |= h
        return result


@dataclasses.dataclass
class AnomalyParameterType:
    name: str
    type: type


@dataclasses.dataclass
class DataType:
    type: type
    default_value: Any
    hints: Hint

    def update(self, other: "DataType") -> "DataType":
        if self.type is not None and other.type is not None:
            raise ValueError(f"Can not update type: {self} to {other}")

        if self.default_value is not None and other.default_value is not None:
            raise ValueError(f"Can not update default value: {self} to {other}")

        self.type = other.type
        self.default_value = other.default_value
        self.hints |= other.hints


RESULT_ANY = DataType(Any, None, Hint.NONE)

# Utility functions #############################################################


def _get_name(t: Any) -> str:
    if _is_collection_instance(t):
        return ",".join(_get_name(e) for e in t)
    return {
        bool: "bool",
        bytes: "bytes",
        int: "int",
        float: "float",
        str: "str",
        bool: "bool",
        NoneType: "NoneType",
    }.get(t, str(t))


def _make_type(t: Any) -> Callable[[Union[Tuple[Any], Any]], type]:
    outer_exception = Exception()

    def _make_type_with_single_parameter(p: Any) -> type:
        try:
            if _is_collection_instance(p):
                return t(*p) if isinstance(t, Qualifier) else t[*p]
            return t(p) if isinstance(t, Qualifier) else t[p]
        except Exception as e:
            raise ValueError(f"Can not make type: {t} with parameter: {p}{os.linesep}").with_traceback(
                outer_exception.__traceback__
            ) from e

    return _make_type_with_single_parameter


def __apply_parameters(t: type, p: Iterable) -> type:
    return t[*p]


def __apply_parameter(t: type, p: Any) -> type:
    return t[p]


def _is_collection_instance(i: Any) -> TypeGuard[Collection]:
    if isinstance(i, str):
        return False
    return isinstance(i, Collection)


def _literal(i: Any) -> Literal:
    if _is_collection_instance(i):
        if len(i) == 0:
            return Literal[""]
        return __apply_parameters(Literal, i)
    return __apply_parameter(Literal, i)


def _qualifier(q: Union[str, QualifierIndex, type]) -> Union[Qualifier, type]:
    if isinstance(q, (str, QualifierIndex)):
        return Qualifier(q)
    elif isinstance(q, type):
        return q
    raise TypeError(f"Invalid qualifier type: {q!r}")


def _sequence(t: type, *n: int) -> Union[Sequence, Tuple]:
    return Union[*(Tuple[(t,) * i] for i in n), Sequence[t]]


def _default(t: type) -> Callable[[Any], DataType]:
    return lambda v: DataType(t, v, Hint.NONE) if v else t


def _default_type_and_value(tv: Tuple[type, Any]) -> DataType:
    t, v = tv
    return DataType(t, v, Hint.NONE) if v else t


# Tokens ########################################################################
SPACE = string(" ")
SINGLE_QUOTE = string("'")
DOUBLE_QUOTE = string('"')
DOT = string(".")
COMMA_SPACE = string(", ")
BRACK_L = string("[")
BRACK_R = string("]")
BRACE_L = string("{")
BRACE_R = string("}")
PAREN_L = string("(")
PAREN_R = string(")")

DIGITS = char_from("0123456789")
NAME = string("!!!!!!").result(_qualifier("!!!!!!"))
QUALIFIER = strings_from_tuple(
    ("<<<0>>>, sequence", QualifierIndex(0)),
    ("<<<0>>> subclass", QualifierIndex(0)),
    ("<<<0>>>", QualifierIndex(0)),
    ("<<<1>>>", QualifierIndex(1)),
    ("<<<2>>>", QualifierIndex(2)),
    ("<<<3>>>", QualifierIndex(3)),
    ("<<<4>>>", QualifierIndex(4)),
    ("<<<5>>>", QualifierIndex(5)),
    ("<<<6>>>", QualifierIndex(6)),
    ("<<<7>>>", QualifierIndex(7)),
    ("<<<8>>>", QualifierIndex(8)),
    ("<<<9>>>", QualifierIndex(9)),
    ("Any type.", Any),
    ("Any type", Any),
    ("any", Any),
    ("BMesh", "bmesh.types.BMesh"),
    ("bpy.types.FluidSimulationModifier", "bpy.types.FluidSimulationModifier"),  # for Blender 2.7
    ("bpy.types.GreasePencilLayer", "bpy.types.GreasePencilLayer"),
    ("bpy.types.IDPropertyUIManager", "bpy.types.IDPropertyUIManager"),  # for Blender 3.1
    ("CyclesCurveRenderSettings", "bpy.types.CyclesCurveRenderSettings"),
    ("CyclesLightSettings", "CyclesLightSettings"),
    ("CyclesMaterialSettings", "CyclesMaterialSettings"),
    ("CyclesMeshSettings", "CyclesMeshSettings"),
    ("CyclesObjectSettings", "bpy.types.CyclesObjectSettings"),
    ("CyclesRenderLayerSettings", "bpy.types.CyclesRenderLayerSettings"),
    ("CyclesRenderSettings", "bpy.types.CyclesRenderSettings"),
    ("CyclesView3DShadingSettings", "CyclesView3DShadingSettings"),
    ("CyclesVisibilitySettings", "CyclesVisibilitySettings"),
    ("CyclesWorldSettings", "CyclesWorldSettings"),
    ("Depsgraph", "bpy.types.Depsgraph"),
    ("FEdge", "freestyle.types.FEdge"),
    ("idprop.type.IDPropertyGroupViewItems", "idprop.type.IDPropertyGroupViewItems"),
    ("idprop.type.IDPropertyGroupViewKeys", "idprop.type.IDPropertyGroupViewKeys"),
    ("idprop.type.IDPropertyGroupViewValues", "idprop.type.IDPropertyGroupViewValues"),
    ("ImBuf", "imbuf.types.ImBuf"),
    ("IntegrationType", "freestyle.types.IntegrationType"),
    ("Interface0DIterator", "freestyle.types.Interface0DIterator"),
    ("Mesh", "bpy.types.Mesh"),
    ("Module", "types.ModuleType"),
    ("numpy.ndarray", "numpy.ndarray"),
    ("Object", "bpy.types.Object"),
    ("type", type),
    ("UnaryFunction0D", "freestyle.types.UnaryFunction0D"),
    ("Vector", "mathutils.Vector"),
    # ("bpy_prop_collection", "bpy.types.bpy_prop_collection"),
).map(_qualifier)

REFERENCE = strings_from_tuple(
    ("===0===", ReferenceIndex(0)),
    ("===1===", ReferenceIndex(1)),
    ("===2===", ReferenceIndex(2)),
    ("===3===", ReferenceIndex(3)),
    ("===4===", ReferenceIndex(4)),
    ("===5===", ReferenceIndex(5)),
    ("===6===", ReferenceIndex(6)),
    ("===7===", ReferenceIndex(7)),
    ("===8===", ReferenceIndex(8)),
    ("===9===", ReferenceIndex(9)),
)

# Literals #######################################################################
## Primitive literals

LITERAL_STRING = (DOUBLE_QUOTE >> regex(r'[^"]*') << DOUBLE_QUOTE).desc("LITERAL_STRING")
LITERAL_BOOL = string("False").result(False) | string("True").result(True)
LITERAL_INT = regex(r"[-+]?\d+").map(int).desc("LITERAL_INT")
LITERAL_INT_OR_INFINITY = LITERAL_INT | regex(r"[-+]?inf").map(float).desc("LITERAL_INT_OR_INFINITY")
LITERAL_FLOAT = regex(r"[-+]?(?:(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?|inf)").map(float).desc("LITERAL_FLOAT")

ENUM_STRING = (SINGLE_QUOTE >> regex(r"[\w-]+") << SINGLE_QUOTE).desc("ENUM_STRING")

## Complex literals

LITERAL_INT_TUPLE = PAREN_L >> LITERAL_INT.sep_by(COMMA_SPACE).map(tuple) << PAREN_R

LITERAL_FLOAT2 = PAREN_L >> LITERAL_FLOAT.sep_by(COMMA_SPACE, min=2, max=2).map(tuple) << PAREN_R
LITERAL_FLOAT3 = PAREN_L >> LITERAL_FLOAT.sep_by(COMMA_SPACE, min=3, max=3).map(tuple) << PAREN_R
LITERAL_FLOAT4 = PAREN_L >> LITERAL_FLOAT.sep_by(COMMA_SPACE, min=4, max=4).map(tuple) << PAREN_R
LITERAL_FLOAT_TUPLE = PAREN_L >> LITERAL_FLOAT.sep_by(COMMA_SPACE).map(tuple) << PAREN_R

LITERAL_MATRIX33 = PAREN_L >> LITERAL_FLOAT3.sep_by(COMMA_SPACE, min=3, max=3).map(tuple) << PAREN_R
LITERAL_MATRIX44 = PAREN_L >> LITERAL_FLOAT4.sep_by(COMMA_SPACE, min=4, max=4).map(tuple) << PAREN_R
LITERAL_MATRIX_FLOAT = PAREN_L >> LITERAL_FLOAT_TUPLE.sep_by(COMMA_SPACE).map(tuple) << PAREN_R

ENUM_STRING_LIST = BRACK_L >> ENUM_STRING.sep_by(COMMA_SPACE).map(list) << BRACK_R
ENUM_STRING_SET = BRACE_L >> ENUM_STRING.sep_by(COMMA_SPACE).map(set) << BRACE_R
ENUM_LIST = ENUM_STRING_LIST.map(_literal) | REFERENCE

# Primitive types ################################################################
NONE = strings_from_tuple(
    ("None", NoneType),
    ("NoneType", NoneType),
)
BYTES = strings_from_tuple(
    ("bytes", bytes),
    # ("bytes.", bytes),
)
STRING = strings_from_tuple(
    ("string", str),
    ("str", str),
)
BOOL = strings_from_tuple(
    ("boolean", bool),
    ("bool", bool),
)
INT = strings_from_tuple(
    ("integer", int),
    ("int", int),
)
UINT = strings_from_tuple(
    ("uint", int),
    ("unsigned int", int),
)
FLOAT = strings_from_tuple(
    ("float", float),
    ("double", float),
)
PRIMITIVE = strings_from_tuple(
    ("bytes", bytes),
    ("string", str),
    ("str", str),
    ("boolean", bool),
    ("bool", bool),
    ("integer", int),
    ("int", int),
    ("float", float),
    ("double", float),
)

# Primitive types with constraints ###############################################

STRING_WITH_CONSTRAINT = strings_from_tuple(
    ("str", str),
    ("string", str),
    ("string in ", ENUM_LIST),
    ("string, default ", LITERAL_STRING.map(_default(str))),
)

BOOL_WITH_CONSTRAINT = strings_from_tuple(
    ("bool", bool),
    ("boolean", bool),
    ("bool, default ", LITERAL_BOOL.map(_default(bool))),
)
LITERAL_TUPLE_BOOL = PAREN_L >> LITERAL_BOOL.sep_by(COMMA_SPACE).map(tuple) << PAREN_R

ARRAY_BOOL = string("boolean array")
ARRAY_BOOL_WITH_CONSTRAINT = strings_from_tuple(
    ("boolean array", List[bool]),
    ("boolean array of ", LITERAL_INT.result(List[bool]) << string(" items")),
    ("boolean array", string(", default ") >> LITERAL_TUPLE_BOOL.result(_default(List[bool]))),
)
CONSTANT_VALUE_INT = string("Constant value ") >> LITERAL_INT.map(_literal)

RANGE_INT = seq(
    BRACK_L >> LITERAL_INT_OR_INFINITY,
    COMMA_SPACE >> LITERAL_INT_OR_INFINITY << BRACK_R,
)

INT_WITH_CONSTRAINT = (
    string("int in ") >> RANGE_INT >> (string(", default ") >> LITERAL_INT_OR_INFINITY).optional().map(_default(int))
)

RANGE_FLOAT = seq(BRACK_L >> LITERAL_FLOAT, COMMA_SPACE >> LITERAL_FLOAT << BRACK_R)
FLOAT_WITH_CONSTRAINT = (
    string("float in ") >> RANGE_FLOAT >> (string(", default ") >> LITERAL_FLOAT).optional().map(_default(float))
)

# Complex types with constraints #################################################
ENUM_WITH_CONSTRAINT = seq(
    string("enum in ") >> ENUM_LIST,
    (string(", default ") >> ENUM_STRING).optional(),
).map(_default_type_and_value)

ENUM_SET = ENUM_STRING_SET | REFERENCE
ENUM_SET_WITH_CONSTRAINT = seq(
    string("enum set in ") >> ENUM_SET.result(Set[str]),
    (string(", default ") >> ENUM_STRING_SET).optional(),
).map(_default_type_and_value)

ARRAY_INT_WITH_CONSTRAINT = strings_from_tuple(
    ("int array", List[int]),
    (
        "int array of ",
        LITERAL_INT
        >> string(" items in ")
        >> RANGE_INT
        >> (string(", default ") >> LITERAL_INT_TUPLE).optional().map(_default(List[int])),
    ),
)

ARRAY_FLOAT_WITH_CONSTRAINT = (
    string("float array of ")
    >> LITERAL_INT
    >> string(" items in ")
    >> RANGE_FLOAT
    >> (string(", default ") >> LITERAL_FLOAT_TUPLE).optional().map(_default(List[float]))
)

VECTOR2 = regex(r"2[Dd] [Vv]ector").result(_qualifier("mathutils.Vector")) | QUALIFIER.map(
    lambda t: Union[t, List[float], Tuple[float, float]]
) << string(", list or tuple of 2 real numbers")
VECTOR2_WITH_CONSTRAINT = seq(
    QUALIFIER << string(" of 2 items in ") << RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT2).optional(),
).map(_default_type_and_value)

VECTOR3 = regex(r"3[Dd] [Vv]ector").result(_qualifier("mathutils.Vector")) | QUALIFIER.map(
    lambda t: Union[t, List[float], Tuple[float, float, float]]
) << string(", list or tuple of 3 real numbers")
VECTOR3_WITH_CONSTRAINT = seq(
    QUALIFIER << (SPACE << (string("rotation") | NAME)).optional() << string(" of 3 items in ") << RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT3).optional(),
).map(_default_type_and_value)

VECTOR4 = QUALIFIER.map(lambda t: Union[t, List[float], Tuple[float, float, float, float]]) << string(
    ", list or tuple of 4 float values"
)
VECTOR4_WITH_CONSTRAINT = seq(
    QUALIFIER << string(" rotation").optional() << string(" of 4 items in ") << RANGE_FLOAT,
    (string(", default ") >> LITERAL_FLOAT4).optional(),
).map(_default_type_and_value)

MATRIX33 = string("3x3 ") >> QUALIFIER
MATRIX33_WITH_CONSTRAINT = seq(
    QUALIFIER << string(" of 3 * 3 items in ") << RANGE_FLOAT,
    (string(", default ") >> LITERAL_MATRIX33).optional(),
).map(_default_type_and_value)

MATRIX44 = string("4x4 ") >> QUALIFIER
MATRIX44_WITH_CONSTRAINT = seq(
    QUALIFIER << string(" of 4 * 4 items in ") << RANGE_FLOAT,
    (string(", default ") >> LITERAL_MATRIX44).optional(),
).map(_default_type_and_value)

MATRIX_FLOAT_WITH_CONSTRAINT = (
    string("float multi-dimensional array")
    >> string(" of ")
    >> LITERAL_INT
    >> string(" * ")
    >> LITERAL_INT
    >> string(" items in ")
    >> RANGE_FLOAT
    >> (string(", default ") >> LITERAL_MATRIX_FLOAT).optional().map(_default(_qualifier("mathutils.Matrix")))
)

CALLABLE = strings("callable", "Callable", "function").result(Callable)
CALLABLE_WITH_CONSTRAINT = CALLABLE >> (
    string(" that takes a string and returns a ") >> (BOOL | STRING).map(lambda t: Callable[[str], t])
    | string("[[], Union[float, None]]").result(Callable[[], Union[float, None]])
)


## Collection types ##############################################################

TUPLE_ELEMENT = PRIMITIVE | QUALIFIER
TUPLE_ = PAREN_L >> TUPLE_ELEMENT.sep_by(COMMA_SPACE).map(_make_type(Tuple)) << PAREN_R
TUPLE_WITH_CONSTRAINT = (
    strings_from_tuple(
        ("tuple", TUPLE_.optional()),
        ("tuple pair.", Tuple),
        (
            "tuple of ",
            (
                (STRING << string("s").optional() | QUALIFIER << string("'s").optional()).map(lambda t: Tuple[t, ...])
                | string("2 floats").result(Tuple[float, float])
            ),
        ),
    )
    | TUPLE_
    | QUALIFIER.map(lambda q: Tuple[q, ...]) << string(" tuple")
)

FLOAT3 = string("float triplet").result(Tuple[float, float, float])
TUPLE_FLOAT_NAME = strings(
    "b",
    "blue",
    "g",
    "green",
    "width",
    "height",
    "i1",
    "i2",
    "nx",
    "ny",
    "nz",
    "q",
    "r",
    "red",
    "s",
    "t",
    "u1",
    "u2",
    "v",
    "v1",
    "v2",
    "w",
    "x",
    "x1",
    "x2",
    "xsize",
    "y",
    "y1",
    "y2",
    "z",
)
TUPLE_FLOAT_WITH_NAME = (
    (TUPLE_FLOAT_NAME << string(",") << string(" ").optional())
    .at_least(1)
    .map(lambda v: [AnomalyParameterType(p, float) for p in v])
)

SEQUENCE = string("sequence").result(Sequence)
_SEQUENCE_OF = (
    strings_from_tuple(
        ("1, 2, 3 or 4 values", _sequence(float, 1, 2, 3, 4)),
        ("2 or 3 floats", _sequence(float, 2, 3)),
        ("3 or 4 floats", _sequence(float, 3, 4)),
        ("bools", Sequence[bool]),
        ("strings", Sequence[str]),
        ("strings.", Sequence[str]),
        ("float", Sequence[float]),
        ("floats", Sequence[float]),
        ("floats, ints, vectors or matrices", Sequence[Union[float, int, "mathutils.Vector"]]),
        ("3 or more 3d vector", Sequence["mathutils.Vector"]),
        ("numbers", Sequence[float]),
    )
    | TUPLE_WITH_CONSTRAINT.map(_make_type(Sequence))
    | QUALIFIER.map(_make_type(Sequence))
)

SEQUENCE_WITH_CONSTRAINT = strings_from_tuple(
    ("Sequence of ", _SEQUENCE_OF),
    ("sequence of ", _SEQUENCE_OF),
    ("byte sequence.", Sequence[bytes]),
    ("any sequence of 3 floats", _sequence(float, 3)),
    ("byte sequence.", Sequence[bytes]),
    ("byte sequence.", Sequence[bytes]),
)

LIST = string("list").result(List)
LIST_ELEMENT = PRIMITIVE | TUPLE_WITH_CONSTRAINT | QUALIFIER << string(" object").optional()
LIST_WITH_CONSTRAINT = strings("list of ", "List of ") >> LIST_ELEMENT.map(_make_type(List)) << strings("s", "'s").optional()

DICT = string("dict").result(Dict)
DICT_WITH_CONSTRAINT = strings_from_tuple(
    ("dict", Dict),
    (
        "dict mapping vert/edge/face types to ",
        (FLOAT | regex(r"[\w ,]+").result(Any)).map(lambda t: Dict[str, t]),
    ),
    ("dict with string keys", Dict[str, Any]),
)

SET = string("set").result(Set)
SET_ELEMENT = strings_from_tuple(
    ("str.", string),
    ("strings", string),
    ("vert/edge/face type", Union["bmesh.types.BMVert", "bmesh.types.BMEdge", "bmesh.types.BMFace"]),
)
SET_WITH_CONSTRAINT = seq(
    strings_from_tuple(
        ("set of ", SET_ELEMENT.map(_make_type(Set))),
        ("set of flags from ", ENUM_LIST.map(_make_type(Set))),
    ),
    (string(", default ") >> (ENUM_STRING_SET | string("set()").result(set()))).optional(),
).map(_default_type_and_value)

ACCESSOR_FOR = (
    string("Accessor for ")
    >> strings(
        "Freestyle edge layer.",
        "Freestyle face layer.",
        "<<<0>>> UV (as a 2D Vector).",
        "paint mask layer.",
        "skin layer.",
    )
    >> string(", type: ")
    >> QUALIFIER
)

PAIR_ELEMENT = PRIMITIVE | LIST | QUALIFIER
PAIR_WITH_CONSTRAINT = (
    strings("pair of ", "tuple pair of ") >> (PAIR_ELEMENT | CALLABLE).map(lambda t: Tuple[t, t]) << string("s").optional()
    | (FLOAT | INT).map(lambda t: Tuple[t, t]) << string(" pair")
    | PAREN_L >> PAIR_ELEMENT.sep_by(COMMA_SPACE, min=2, max=2).map(_make_type(Tuple)) << PAREN_R << string(" pair").optional()
)


OPTIONAL_ELEMENT = PRIMITIVE | PAIR_WITH_CONSTRAINT | TUPLE_WITH_CONSTRAINT | QUALIFIER
OPTIONAL = (
    string("collection of strings or None.").result(Optional[Collection[str]])
    | OPTIONAL_ELEMENT.map(_make_type(Optional)) << string(" or ") << NONE
)

UNION_ELEMENT = PAIR_WITH_CONSTRAINT | PRIMITIVE | LIST | SET | DICT | SEQUENCE_WITH_CONSTRAINT | MATRIX33 | QUALIFIER | NONE

UNION = seq(
    UNION_ELEMENT.sep_by(COMMA_SPACE, min=1),
    strings(" or ", ", or ") >> UNION_ELEMENT,
).map(lambda v1: Union[*v1[0], v1[1]])

BPY_PROPERTY_COLLECTION_ELEMENT = strings_from_tuple(
    ("NodeSetting", _qualifier("NodeSetting")),
    ("BatchRenameAction", _qualifier("BatchRenameAction")),
    ("OperatorFileListElement", _qualifier("bpy.types.OperatorFileListElement")),
    ("OperatorMousePath", _qualifier("bpy.types.OperatorMousePath")),
    ("OperatorStrokeElement", _qualifier("bpy.types.OperatorStrokeElement")),
    ("SelectedUvElement", _qualifier("bpy.types.SelectedUvElement")),
)

BPY_PROPERTY_COLLECTION_OF_ELEMENT = string("bpy_prop_collection of ") >> BPY_PROPERTY_COLLECTION_ELEMENT.map(
    _make_type(_qualifier("bpy.types.bpy_prop_collection"))
)

QUALIFIER_OF_QUALIFIER = QUALIFIER << (SPACE << QUALIFIER).optional() << string(" of ") << QUALIFIER

QUALIFILER_WITH_NOTE = QUALIFIER << strings_from_tuple(
    (r" int buffer.", 0),
    (r" char buffer.", 0),
    (
        r" object. Depends on function prototype.",
        strings(
            " ('v' prototypes)",
            " (for 'v' prototypes only)",
        ).optional(),
    ),
    (r" object", 0),
    (r" object.", 0),
    (r" char.", 0),
    (r" I{GL_INT}", 0),
    (r" object I{type GL_INT}", 0),
    (r" object I{GL_FLOAT}", 0),
)

CACHE_QUALIFIER = strings_from_tuple(
    ("Generic ", regex(r"[\w\d(), -]+\., type: ") >> QUALIFIER),
)

TYPE_ENUMERATED_CONSTANT = strings(
    "Enumerated constant",
    "Enumerated constant(s)",
).result(Any)

TYPE_ERROR_CORRECTION = strings_from_tuple(
    ("bpy.types.GPUShader", _qualifier("gpu.types.GPUShader")),
    ("bpy.types.GPUShaderCreateInfo", _qualifier("gpu.types.GPUShaderCreateInfo")),
    ("bpy.types.GreasePencilLayer", _qualifier("bpy.types.GreasePencilLayers")),
    ("bpy.types.GreasePencilv3", _qualifier("bpy.types.GreasePencil")),
    ("bpy.types.IDPropertyGroup", _qualifier("idprop.types.IDPropertyGroup")),
)


CATCH_NAME = strings(
    "alpha",
    "angle",
    "animated",
    "begin",
    "border",
    "buffer",
    "bufSize",
    "cap",
    "coord",
    "count",
    "data",
    "depth",
    "dfactor",
    "dimensions",
    "do_linked_ids",
    "do_local_ids",
    "do_recursive",
    "end",
    "entry",
    "equation",
    "face",
    "factor",
    "fail",
    "flag",
    "format",
    "frame",
    "func",
    "get",
    "height",
    "i",
    "i2",
    "impulseResponse",
    "infoLog",
    "internalformat",
    "j",
    "length",
    "level",
    "light",
    "m",
    "map",
    "mapsize",
    "mask",
    "maxCount",
    "maxLength",
    "mode",
    "n",
    "name",
    "nz",
    "opcode",
    "order",
    "param",
    "params",
    "pixels",
    "plane",
    "pname",
    "points",
    "program",
    "q",
    "query",
    "random",
    "range",
    "ref",
    "s",
    "set",
    "sfactor",
    "shader",
    "shaders",
    "size",
    "skip",
    "sound",
    "source",
    "stride",
    "target",
    "template",
    "texture",
    "textures",
    "threadPool",
    "type",
    "u",
    "u2",
    "un",
    "units",
    "uorder",
    "ustride",
    "v",
    "v2",
    "values",
    "vn",
    "vorder",
    "vstride",
    "w",
    "width",
    "y",
    "y1",
    "y2",
    "z",
    "zfail",
    "zFar",
    "zNear",
    "zpass",
)

HINT = strings_from_tuple(
    ("never None", Hint.NEVER_NONE),
    ("optional argument", Hint.OPTIONAL),
    ("optional", Hint.OPTIONAL),
    ("readonly", Hint.READONLY),
)
HINTS = PAREN_L >> HINT.sep_by(COMMA_SPACE) << PAREN_R

TYPE_SPECIFIER = alt(
    UNION,
    LIST_WITH_CONSTRAINT,
    PAIR_WITH_CONSTRAINT,
    TUPLE_WITH_CONSTRAINT,
    ENUM_WITH_CONSTRAINT,
    ENUM_SET_WITH_CONSTRAINT,
    SET_WITH_CONSTRAINT,
    ARRAY_BOOL_WITH_CONSTRAINT,
    BOOL_WITH_CONSTRAINT,
    ARRAY_INT_WITH_CONSTRAINT,
    INT_WITH_CONSTRAINT,
    ARRAY_FLOAT_WITH_CONSTRAINT,
    FLOAT_WITH_CONSTRAINT,
    BPY_PROPERTY_COLLECTION_OF_ELEMENT,
    MATRIX_FLOAT_WITH_CONSTRAINT,
    MATRIX44_WITH_CONSTRAINT,
    MATRIX33_WITH_CONSTRAINT,
    VECTOR4_WITH_CONSTRAINT,
    VECTOR3_WITH_CONSTRAINT,
    VECTOR2_WITH_CONSTRAINT,
    STRING_WITH_CONSTRAINT,
    CALLABLE_WITH_CONSTRAINT,
    DICT_WITH_CONSTRAINT,
    CONSTANT_VALUE_INT,
    OPTIONAL,
    VECTOR4,
    VECTOR3,
    VECTOR2,
    MATRIX33,
    MATRIX44,
    FLOAT3,
    BOOL,
    UINT,
    INT,
    LIST,
    SET,
    CALLABLE,
    SEQUENCE_WITH_CONSTRAINT,
    SEQUENCE,
    FLOAT,
    QUALIFIER_OF_QUALIFIER,
    QUALIFILER_WITH_NOTE,
    QUALIFIER,
    NAME,
    ACCESSOR_FOR,
    TUPLE_FLOAT_WITH_NAME,
    TYPE_ENUMERATED_CONSTANT,
    TYPE_ERROR_CORRECTION,
    CACHE_QUALIFIER,
)

DOCUMENT_HEAD_DASH = string(" -") << SPACE.optional()
DOCUMENT = regex(r".+$")


def data_types(t: Union[type, DataType], hints: Optional[Iterable[Hint]] = None) -> DataType:
    result = DataType(None, None, Hint.join(hints) if hints else Hint.NONE)

    if isinstance(t, DataType):
        result.update(t)
        return result

    if isinstance(t, (str, int, float, bool)):
        raise TypeError(f"Invalid type: {t!r}")

    result.update(DataType(t, None, Hint.NONE))
    return result


TYPE_SPECIFIER_WITH_HINT = seq(TYPE_SPECIFIER, (SPACE.optional() >> COMMA_SPACE >> HINTS).optional()).map(
    lambda v: data_types(v[0], v[1])
)
NAME_TYPE_SPECIFIER_WITH_HINT = (
    (NAME | CATCH_NAME) >> SPACE >> PAREN_L >> SPACE.optional() >> TYPE_SPECIFIER_WITH_HINT << DOT.optional() << PAREN_R
)
TYPE_SPECIFIER_WITH_HINT_DOCUMENT = (NAME_TYPE_SPECIFIER_WITH_HINT | TYPE_SPECIFIER_WITH_HINT) << (
    (DOCUMENT_HEAD_DASH | COMMA_SPACE) << DOCUMENT.optional()
).optional()


LINE_CATCH_HANDLER = (
    strings_from_tuple(
        ("on a compositing ", Callable),
        ("on canceling ", Callable),
        ("on completing ", Callable),
        ("on completion ", Callable),
        ("on depsgraph update ", Callable),
        ("on drawing ", Callable),
        ("on ending ", Callable),
        ("on failure ", Callable),
        ("on initialization ", Callable),
        ("on loading ", Callable),
        ("on printing ", Callable),
        ("on render ", Callable),
        ("on saving ", Callable),
        ("on starting ", Callable),
        ("on writing ", Callable),
    )
    << DOCUMENT
)

LINE_CATCH_ITERABLE_OBJECT = (
    NAME
    >> SPACE
    >> PAREN_L
    >> string("iterable object")
    >> PAREN_R
    >> DOCUMENT_HEAD_DASH
    >> (FLOAT3 | PAIR_WITH_CONSTRAINT).map(_make_type(Iterable))
    << DOCUMENT
)

LINE_CATCH_CLASS = (
    NAME
    >> SPACE
    >> PAREN_L
    >> string("class")
    >> PAREN_R
    >> DOCUMENT_HEAD_DASH
    >> (
        string("A subclass of ") >> QUALIFIER.sep_by(string(" or ")) << DOT
        | string("Blender type class in: ") >> QUALIFIER.sep_by(COMMA_SPACE)
    ).map(_make_type(Union))
)

LINE_CATCH_PAIR_INT = (
    NAME
    >> SPACE
    >> PAREN_L
    >> string("tuple.")
    >> PAREN_R
    >> DOCUMENT_HEAD_DASH
    >> string("Pair of ints.").result(Tuple[int, int])
)

LINE_CATCH_LIST = string("A list of ") >> regex(r"[\w\d()., *-]+, ").result(List) << HINTS

LINE_CATCH_OPTIONAL = OPTIONAL << strings(" when ") << DOCUMENT

DATA_TYPE = (
    LINE_CATCH_HANDLER
    | LINE_CATCH_ITERABLE_OBJECT
    | LINE_CATCH_CLASS
    | LINE_CATCH_PAIR_INT
    | TYPE_SPECIFIER_WITH_HINT_DOCUMENT
    | LINE_CATCH_LIST
    | LINE_CATCH_OPTIONAL
).map(data_types)

DATA_TYPE_PARSER = DATA_TYPE << eof
