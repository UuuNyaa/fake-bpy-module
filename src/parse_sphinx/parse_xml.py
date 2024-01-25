import dataclasses
import enum
import functools
import logging
import re
import sys
from abc import abstractproperty
from typing import Dict, List, Optional, Tuple
import unicodedata

import lxml.etree
from lxml.etree import ElementBase as Element

_logger = logging.getLogger(__name__)


def parse_module(xml_path: str) -> "Module":
    document: Element = lxml.etree.parse(xml_path)
    return Module(
        path=xml_path,
        datas=[_to_data(e) for e in document.xpath("//section/desc[@desctype='data']")],
        functions=[f for e in document.xpath("//section/desc[@desctype='function']") for f in _to_fuctions(e)],
        classes=[_to_class(e) for e in document.xpath("//desc[@desctype='class']")],
    )


# Result types ##################################################################
class TypeElementKind(str, enum.Enum):
    QUALIFIER = "QUALIFIER"
    REFERENCE = "REFERENCE"
    STRONG = "STRONG"
    EMPHASIS = "EMPHASIS"
    LITERAL = "LITERAL"
    NAME = "NAME"
    TEXT = "TEXT"


@dataclasses.dataclass(frozen=True)
class TypeElement:
    text: str

    @abstractproperty
    def kind(self) -> TypeElementKind:
        raise NotImplementedError()

    def is_qualifier(self) -> bool:
        return self.kind == TypeElementKind.QUALIFIER

    def is_reference(self) -> bool:
        return self.kind == TypeElementKind.REFERENCE

    def is_strong(self) -> bool:
        return self.kind == TypeElementKind.STRONG

    def is_emphasis(self) -> bool:
        return self.kind == TypeElementKind.EMPHASIS

    def is_literal(self) -> bool:
        return self.kind == TypeElementKind.LITERAL

    def is_name(self) -> bool:
        return self.kind == TypeElementKind.NAME

    def is_text(self) -> bool:
        return self.kind == TypeElementKind.TEXT


@dataclasses.dataclass(frozen=True)
class TypeElementQualifier(TypeElement):
    qualifier: str

    @property
    def kind(self) -> TypeElementKind:
        return TypeElementKind.QUALIFIER

    def __repr__(self) -> str:
        return f"`{self.qualifier}`"


@dataclasses.dataclass(frozen=True)
class TypeElementReference(TypeElement):
    reference: str

    @property
    def kind(self) -> TypeElementKind:
        return TypeElementKind.REFERENCE

    def __repr__(self) -> str:
        return f"ref:{self.reference}"


@dataclasses.dataclass(frozen=True)
class TypeElementStrong(TypeElement):
    @property
    def kind(self) -> TypeElementKind:
        return TypeElementKind.STRONG

    def __repr__(self) -> str:
        return f"*{self.text}*"


@dataclasses.dataclass(frozen=True)
class TypeElementEmphasis(TypeElement):
    @property
    def kind(self) -> TypeElementKind:
        return TypeElementKind.EMPHASIS

    def __repr__(self) -> str:
        return f"_{self.text}_"


@dataclasses.dataclass(frozen=True)
class TypeElementLiteral(TypeElement):
    @property
    def kind(self) -> TypeElementKind:
        return TypeElementKind.LITERAL

    def __repr__(self) -> str:
        return f"'{self.text}'"


@dataclasses.dataclass(frozen=True)
class TypeElementName(TypeElement):
    @property
    def kind(self) -> TypeElementKind:
        return TypeElementKind.NAME

    def __repr__(self) -> str:
        return f"{self.text}"


@dataclasses.dataclass(frozen=True)
class TypeElementText(TypeElement):
    @property
    def kind(self) -> TypeElementKind:
        return TypeElementKind.TEXT

    def __repr__(self) -> str:
        return f"{self.text}"


@dataclasses.dataclass(unsafe_hash=True)
class Type:
    elements: Tuple[TypeElement]
    signature_text: Optional[str]
    document_text: Optional[str]

    def count_qualifiers(self) -> int:
        return sum(1 for e in self.elements if e.is_qualifier())

    def update(self, other: "Type"):
        def join_text(this: Optional[str], that: Optional[str]) -> Optional[str]:
            if this is None:
                return that
            if that is None:
                return this
            return this + ", " + that

        self.elements = self.elements + other.elements
        self.signature_text = join_text(self.signature_text, other.signature_text)
        self.document_text = join_text(self.document_text, other.document_text)

    __REGEX_SEARCH_TYPE_TEXT_OR_NONE = re.compile(r" or None\b")
    __REGEX_SEARCH_TYPE_TEXT_READONLY = re.compile(r"\breadonly\b")


TYPE_NONE = Type(
    elements=(TypeElementQualifier(text="None", qualifier="None"),),
    signature_text="None",
    document_text=None,
)


@dataclasses.dataclass
class Data:
    name: str
    type: Type
    annotations: List[str]
    description: Optional[str] = None


@dataclasses.dataclass
class Attribute:
    name: str
    type: Type
    annotations: List[str]
    description: Optional[str] = None


@dataclasses.dataclass
class Parameter:
    name: str
    type: Type
    operator: Optional[str]
    default_value: Optional[str]
    description: Optional[str] = None


@dataclasses.dataclass
class Method:
    name: str
    return_type: Type
    parameters: List[Parameter]
    annotations: List[str]
    description: Optional[str] = None


@dataclasses.dataclass
class Class:
    name: str
    module: str
    full_name: str
    base_class_types: List[Type]
    attributes: List[Attribute]
    datas: List[Data]
    methods: List[Method]
    annotations: List[str]


@dataclasses.dataclass
class Module:
    path: str
    datas: List[Data]
    functions: List[Method]
    classes: List[Class]


def _to_data(data_desc_element: Element) -> Data:
    desc_signature: Optional[Element] = data_desc_element.find("desc_signature")
    name: str = desc_signature.attrib.get("ids", _get_text(desc_signature))
    # type_paragraphs: List[Element] = data_desc_element.findall("desc_content/paragraph")
    type_paragraphs: List[Element] = data_desc_element.xpath("desc_content//paragraph[not(ancestor::paragraph)]")
    #         "desc_content/field_list/field/field_name[text()='Return type']/following-sibling::field_body/paragraph"

    return Data(name=name, type=_to_type_from_paragraphs(type_paragraphs), annotations=[])


def _to_class(class_desc_element: Element) -> Class:
    base_classes_paragraph = class_desc_element.xpath(
        "self::desc/preceding-sibling::paragraph[starts-with(text(),'base class')]"
    )
    desc_signature: Optional[Element] = class_desc_element.find("desc_signature")
    if desc_signature is None:
        _raise_element_error(class_desc_element, "No desc_signature found")

    full_qualified_name = desc_signature.attrib["ids"]
    full_name = desc_signature.attrib["fullname"]
    module = desc_signature.attrib["module"]

    return Class(
        name=full_qualified_name,
        module=module,
        full_name=full_name,
        base_class_types=[_to_type_from_paragraph(p) for p in base_classes_paragraph]
        if base_classes_paragraph is not None
        else [],
        attributes=[_to_member_attribute(e) for e in class_desc_element.findall("desc_content/desc[@desctype='attribute']")],
        datas=[_to_member_data(e) for e in class_desc_element.findall("desc_content/desc[@desctype='data']")],
        methods=[m for e in class_desc_element.findall("desc_content/desc[@desctype='method']") for m in _to_fuctions(e)],
        annotations=[],
    )


def _to_member_attribute(member_desc_element: Element) -> Attribute:
    name: Optional[Element] = _get_text(member_desc_element.find("desc_signature/desc_name"))
    type_paragraphs: List[Element] = member_desc_element.xpath("desc_content/field_list//paragraph[not(ancestor::paragraph)]")

    if len(type_paragraphs) == 0:
        type_paragraphs.extend(member_desc_element.xpath("desc_content//paragraph[not(ancestor::paragraph)]"))
        if len(type_paragraphs) == 0:
            _raise_element_error(member_desc_element, "No type paragraph found")

    return Attribute(name=name, type=_to_type_from_paragraphs(type_paragraphs), annotations=[])


def _to_member_data(member_desc_element: Element) -> Data:
    name: Optional[Element] = _get_text(member_desc_element.find("desc_signature/desc_name"))
    type_paragraphs: List[Element] = member_desc_element.xpath("desc_content/field_list//paragraph[not(ancestor::paragraph)]")

    if len(type_paragraphs) == 0:
        type_paragraphs.extend(member_desc_element.xpath("desc_content//paragraph[not(ancestor::paragraph)]"))
        if len(type_paragraphs) == 0:
            _raise_element_error(member_desc_element, "No type paragraph found")

    return Data(name=name, type=_to_type_from_paragraphs(type_paragraphs), annotations=[])


def _to_fuctions(function_desc_element: Element) -> List[Method]:
    methods: List[Method] = []

    desc_signatures: List[Element] = function_desc_element.findall("desc_signature")
    if len(desc_signatures) == 0:
        _raise_element_error(function_desc_element, "No desc_signature found")

    # field_paragraphs are shared by all desc_signatures
    field_paragraphs_cache = __to_field_paragraphs(function_desc_element)

    return_type = __to_return_type(function_desc_element)

    for desc_signature in desc_signatures:
        name: str = _get_text(desc_signature.find("desc_name"))
        annotations: List[str] = __to_annotations_from_desc_signature(desc_signature)

        desc_parameters: List[Element] = desc_signature.xpath("desc_parameterlist/desc_parameter")
        field_paragraphs = field_paragraphs_cache.copy()

        desc_parameters_length = len(desc_parameters)
        desc_parameter_name2counts: Dict[str, int] = functools.reduce(
            lambda acc, name: {**acc, name: acc.get(name, 0) + 1},
            (_to_parameter_name_from_parameter(p) for p in desc_parameters),
            {},
        )
        if desc_parameters_length != len(desc_parameter_name2counts):
            _raise_element_error(function_desc_element, f"Duplicate parameter names: {desc_parameter_name2counts}")

        parameters: List[Parameter] = []

        while len(desc_parameters) > 0 and len(field_paragraphs) > 0:
            target_name = _to_parameter_name_from_parameter(desc_parameters[0])

            if target_name == "":
                parameters.append(__new_parameter_from_parameter(desc_parameters.pop(0)))
                continue

            field_paragraphs_search_range_index = next(
                iter(i + 1 for i, v in enumerate(desc_parameters[1:]) if _to_parameter_name_from_parameter(v) == target_name),
                len(field_paragraphs),
            )

            # find all field_paragraphs values with the same name as target_name
            match_field_paragraphs_index2values = {
                i: v
                for i, v in enumerate(field_paragraphs[:field_paragraphs_search_range_index])
                if _to_parameter_name_from_paragraph(v) == target_name
            }

            # if there are any field_paragraphs values with the same name as target_name, add them to the result
            if len(match_field_paragraphs_index2values) > 0:
                parameter = desc_parameters.pop(0)
                type = _to_type_from_parameter(parameter)

                for v in match_field_paragraphs_index2values.values():
                    type.update(_to_type_from_paragraph(v))

                # remove match_field_paragraphs_index2values.keys() from field_paragraphs
                field_paragraphs = [
                    v for i, v in enumerate(field_paragraphs) if i not in match_field_paragraphs_index2values.keys()
                ]

                parameters.append(__new_parameter_from_parameter(parameter, type))
                continue

            field_paragraph_name = _to_parameter_name_from_paragraph(field_paragraphs[0])
            match_desc_parameters_index = next(
                iter(i for i, v in enumerate(desc_parameters) if _to_parameter_name_from_parameter(v) == field_paragraph_name),
                None,
            )

            if match_desc_parameters_index is not None and len(field_paragraphs) > match_desc_parameters_index:
                # move field_paragraphs[0] to desc_parameters cooresponding position
                field_paragraphs.insert(match_desc_parameters_index, field_paragraphs.pop(0))

            parameter = desc_parameters.pop(0)
            parameters.append(__new_parameter_from_parameter(parameter))

        remain_desc_parameters_length = len(desc_parameters)
        remain_field_paragraphs_length = len(field_paragraphs)

        # append the remaining desc_parameters
        for parameter in desc_parameters:
            new_parameter = __new_parameter_from_parameter(parameter)
            if new_parameter.name != "":
                _log_warning(parameter, f"Unmatched parameter: {_to_parameter_name_from_parameter(parameter)} in {name}")
            parameters.append(__new_parameter_from_parameter(parameter))

        if (len(desc_signatures) == 1 and desc_parameters_length == 0) or remain_desc_parameters_length > 0:
            # corrupted desc_parameters or remaining desc_parameters
            # append the remaining field_paragraphs
            for paragraph in field_paragraphs:
                _log_warning(paragraph, f"Unmatched parameter: {_to_parameter_name_from_paragraph(paragraph)} in {name}")
                parameters.append(__new_parameter_from_paragraph(paragraph))

        methods.append(
            Method(
                name=name,
                return_type=return_type,
                parameters=parameters,
                annotations=annotations,
            )
        )
    return methods


def _to_type_elements(element: Element) -> List[TypeElement]:
    type_elements = []

    element: Element
    for element in element.getchildren():
        if element.tag == "reference":
            if "reftitle" in element.attrib:
                type_elements.append(
                    TypeElementQualifier(
                        text=_get_text(element).strip(),
                        qualifier=element.attrib["reftitle"],
                    )
                )
            else:
                type_elements.append(
                    TypeElementReference(
                        text=_get_text(element).strip(),
                        reference=element.attrib["refuri"],
                    )
                )
        elif element.tag in ("literal_emphasis", "emphasis"):
            pass
            # type_elements.append(TypeElementEmphasis(text=_get_text(element)))
        elif element.tag in ("literal_strong", "strong"):
            pass
            # type_elements.append(TypeElementStrong(text=_get_text(element)))
        elif element.tag in ("literal", "paragraph", "bullet_list", "title_reference"):
            pass
            # type_elements.append(TypeElementText(text=_strip(_get_text(element))))
        elif element.tag == "field_list":
            field: Element
            for field in element.findall("field"):
                # type_elements.append(TypeElementName(text=_get_text(field.find("field_name"))))
                type_elements.extend(_to_type_elements(field.find("field_body")))
        elif element.tag in ("warning", "seealso", "note"):
            # it has no type information
            pass
        else:
            _raise_element_error(element, "Unexpected element")

    return tuple(type_elements)


_REGEX_MATCH_DESC_EXPRESSION = re.compile(r"N: (N)$")
_TAG_TO_DESC_EXPRESSION_CHARACTERS = {
    "desc_sig_name": "N",
    "desc_sig_operator": "O",
    "desc_sig_punctuation": ":",
    "desc_sig_space": " ",
    "inline": "I",
}


def _to_type_from_parameter(desc_parameter: Element) -> Type:
    desc_sigs: List[Element] = desc_parameter.findall("*")
    desc_expression = "".join(_TAG_TO_DESC_EXPRESSION_CHARACTERS.get(e.tag, "?") for e in desc_sigs)
    if unexpected_element_index := desc_expression.find("?") >= 0:
        _raise_element_error(desc_parameter, f"Unexpected element: <{desc_sigs[unexpected_element_index].tag}>")

    if m := _REGEX_MATCH_DESC_EXPRESSION.match(desc_expression):
        desc_sig_name = desc_sigs[m.pos]
        type_elements = (
            TypeElementQualifier(
                text=_get_text(desc_sig_name).strip(),
                qualifier=desc_sig_name.text,
            ),
        )
    else:
        type_elements: Tuple[TypeElement] = ()
        if unexpected_element_index := desc_expression.find(":") >= 0:
            _raise_element_error(desc_parameter, f"desc_sig_punctuation: <{desc_sigs[unexpected_element_index].tag}>")

    return Type(
        elements=type_elements,
        signature_text=_to_parameter_name_from_parameter(desc_parameter),
        document_text=None,
    )


def _to_type_from_paragraph(type_paragraph: Element) -> Type:
    return Type(
        elements=_to_type_elements(type_paragraph),
        signature_text=None,
        document_text=_get_text(type_paragraph),
    )


def _to_parameter_name_from_paragraph(parameter_paragraph: Element) -> str:
    literal_strong: Optional[Element] = parameter_paragraph.find("literal_strong")
    if literal_strong is not None:
        return _get_text(literal_strong)
    else:
        return _get_text(parameter_paragraph)


def _to_parameter_name_from_parameter(desc_parameter: Element) -> str:
    desc_sig_name: Optional[Element] = desc_parameter.find("desc_sig_name")

    if desc_sig_name is None:
        return ""

    return _get_text(desc_sig_name)


def _to_type_from_paragraphs(type_paragraphs: List[Element]) -> Type:
    if len(type_paragraphs) == 0:
        raise ValueError("No type paragraph found")

    type: Optional[Type] = None
    for type_paragraph in type_paragraphs:
        new_type = _to_type_from_paragraph(type_paragraph)
        if type is None:
            type = new_type
            continue

        type.update(new_type)

    return type


def __to_annotations_from_desc_signature(desc_signature: Element) -> List[str]:
    desc_annotations: List[Element] = desc_signature.xpath("desc_annotation")
    annotations: List[str] = []
    for desc_annotation in desc_annotations:
        annotation = _get_text(desc_annotation).strip()
        if annotation == "static":
            annotation = "staticmethod"
            _log_warning(desc_signature, f"[Recover] Use staticmethod instead of static")

        elif annotation not in ("classmethod", "staticmethod"):
            _raise_element_error(desc_signature, f"Unknown annotation: {annotation}")
        annotations.append(annotation)
    return annotations


def __to_field_paragraphs(function_desc_element: Element) -> List[Element]:
    field_paragraphs: List[Element] = function_desc_element.xpath(
        "desc_content/field_list/field/field_name[text()='Parameters']/following-sibling::field_body//paragraph[not(ancestor::paragraph)]"
    )
    paragraphs_length = len(field_paragraphs)
    paragraph_name2counts: Dict[str, int] = functools.reduce(
        lambda acc, name: {**acc, name: acc.get(name, 0) + 1},
        (_to_parameter_name_from_paragraph(p) for p in field_paragraphs),
        {},
    )
    if paragraphs_length != len(paragraph_name2counts):
        _log_warning(function_desc_element, f"[Recover] Merge duplicate parameters: {paragraph_name2counts}")

    return field_paragraphs


def __to_return_type(function_desc_element: Element) -> Type:
    return_type_paragraphs: List[Element] = function_desc_element.xpath(
        "desc_content/field_list/field/field_name[text()='Return type']/following-sibling::field_body/paragraph"
    )
    return_paragraphs: List[Element] = function_desc_element.xpath(
        "desc_content/field_list/field/field_name[text()='Returns']/following-sibling::field_body/paragraph"
    )

    # merge return_type_paragraphs and return_paragraphs,
    # because the return type is sometimes in the return_paragraphs
    return_type_paragraphs.extend(return_paragraphs)
    return_type = _to_type_from_paragraphs(return_type_paragraphs) if len(return_type_paragraphs) > 0 else TYPE_NONE
    return return_type


def __new_parameter_from_parameter(desc_parameter: Element, type: Optional[Type] = None) -> Parameter:
    def get_desc_sig_operator_from_parameter(desc_parameter: Element) -> Optional[str]:
        desc_sig_operator: Optional[Element] = desc_parameter.find("desc_sig_operator")
        if desc_sig_operator is None:
            return None

        operator_text = _get_text(desc_sig_operator)
        if operator_text not in ("=", "*", "**"):
            _raise_element_error(desc_sig_operator, f"Unknown operator: {operator_text}")

        return _get_text(desc_sig_operator)

    def get_default_value_from_parameter(desc_parameter: Element) -> Optional[str]:
        inline: Optional[Element] = desc_parameter.find("inline")
        if inline is None:
            return None

        inline_classes = inline.attrib["classes"]
        if inline_classes != "default_value":
            _raise_element_error(inline, f"Unexpected inline classes: {inline_classes}")
        return _get_text(inline)

    name = _to_parameter_name_from_parameter(desc_parameter)
    operator = get_desc_sig_operator_from_parameter(desc_parameter)

    # if target_name is empty, it must be a keyword-only parameter
    if name == "" and operator != "*":
        _raise_element_error(desc_parameter, f"Parameter name is empty in {name}")

    return Parameter(
        name=name,
        type=type or _to_type_from_parameter(desc_parameter),
        operator=operator,
        default_value=get_default_value_from_parameter(desc_parameter),
    )


def __new_parameter_from_paragraph(paragraph: Element) -> Parameter:
    return Parameter(
        name=_to_parameter_name_from_paragraph(paragraph),
        type=_to_type_from_paragraph(paragraph),
        operator=None,
        default_value=None,
    )


_TRANSLATE_TABLE = dict(
    (
        (ord(x), ord(y))
        for x, y in zip(
            r"""‘’´“”–-""",
            r"""'''""--""",
        )
    )
)


def _get_text(element: Element) -> str:
    return unicodedata.normalize("NFKD", "".join(element.itertext())).translate(_TRANSLATE_TABLE)


def _log_warning(element: Element, message: str, *args, **kwargs):
    _logger.warning(
        f"""{message}\n  File {element.getroottree().docinfo.URL}:{element.sourceline} in <{element.tag}>""", *args, **kwargs
    )


def _raise_element_error(element: Element, message: str) -> None:
    raise ValueError(f"""{message}\n  File {element.getroottree().docinfo.URL}:{element.sourceline} in <{element.tag}>""")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        document: lxml.etree._ElementTree = lxml.etree.parse(arg)
        for class_desc_element in document.xpath("//desc[@desctype='class']"):
            _to_class(class_desc_element)

        for data_desc_element in document.xpath("//section/desc[@desctype='data']"):
            _to_data(data_desc_element)

        for function_desc_element in document.xpath("//section/desc[@desctype='function']"):
            _to_fuctions(function_desc_element)
