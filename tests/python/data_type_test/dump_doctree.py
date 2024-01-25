import dataclasses
import enum
import functools
import logging
import re
import sys
from typing import Dict, List, Optional

import lxml.etree
from lxml.etree import ElementBase as Element


class TypeElementKind(enum.Enum):
    QUALIFIER = enum.auto()
    REFERENCE = enum.auto()
    STRONG = enum.auto()
    EMPHASIS = enum.auto()
    LITERAL = enum.auto()
    NAME = enum.auto()
    TEXT = enum.auto()


@dataclasses.dataclass
class TypeElement:
    kind: TypeElementKind
    text: str


@dataclasses.dataclass
class TypeElementQualifier(TypeElement):
    qualifier: str

    def __repr__(self) -> str:
        return f"`{self.qualifier}`"


@dataclasses.dataclass
class TypeElementReference(TypeElement):
    reference: str

    def __repr__(self) -> str:
        return f"ref:{self.reference}"


@dataclasses.dataclass
class TypeElementStrong(TypeElement):
    def __repr__(self) -> str:
        return f"*{self.text}*"


@dataclasses.dataclass
class TypeElementEmphasis(TypeElement):
    def __repr__(self) -> str:
        return f"_{self.text}_"


@dataclasses.dataclass
class TypeElementLiteral(TypeElement):
    def __repr__(self) -> str:
        return f"'{self.text}'"


@dataclasses.dataclass
class TypeElementName(TypeElement):
    def __repr__(self) -> str:
        return f"{self.text}"


@dataclasses.dataclass
class TypeElementText(TypeElement):
    def __repr__(self) -> str:
        return f"{self.text}"


@dataclasses.dataclass
class Type:
    text: str
    elements: List[TypeElement]

    @property
    def is_optional(self) -> bool:
        return Type.__REGEX_SEARCH_TYPE_TEXT_OR_NONE.search(self.text) is not None

    @property
    def is_readonly(self) -> bool:
        return Type.__REGEX_SEARCH_TYPE_TEXT_READONLY.search(self.text) is not None

    def update(self, other: "Type"):
        self.text += "\n" + other.text
        self.elements.extend(other.elements)

    __REGEX_SEARCH_TYPE_TEXT_OR_NONE = re.compile(r" or None\b")
    __REGEX_SEARCH_TYPE_TEXT_READONLY = re.compile(r"\breadonly\b")


TYPE_NONE = Type(text="None", elements=[])


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
    base_classes: List[str]
    attributes: List[Attribute]
    datas: List[Data]
    methods: List[Method]
    annotations: List[str]


def _get_text(element: Element) -> str:
    return "".join(element.itertext())


def _get_type_elements(element: Element, type_elements: Optional[List[TypeElement]] = None) -> List[TypeElement]:
    type_elements = type_elements or []

    element: Element
    for element in element.getchildren():
        if element.tag == "reference":
            if "reftitle" in element.attrib:
                type_elements.append(
                    TypeElementQualifier(
                        kind=TypeElementKind.QUALIFIER,
                        text=_get_text(element),
                        qualifier=element.attrib["reftitle"],
                    )
                )
            else:
                type_elements.append(
                    TypeElementReference(
                        kind=TypeElementKind.REFERENCE,
                        text=_get_text(element),
                        reference=element.attrib["refuri"],
                    )
                )
        elif element.tag in ("literal_emphasis", "emphasis"):
            type_elements.append(TypeElementEmphasis(kind=TypeElementKind.EMPHASIS, text=_get_text(element)))
        elif element.tag in ("literal_strong", "strong"):
            type_elements.append(TypeElementStrong(kind=TypeElementKind.STRONG, text=_get_text(element)))
        elif element.tag in ("literal", "paragraph", "bullet_list", "title_reference"):
            type_elements.append(TypeElementText(kind=TypeElementKind.TEXT, text=_get_text(element)))
        elif element.tag == "field_list":
            field: Element
            for field in element.findall("field"):
                type_elements.append(TypeElementName(kind=TypeElementKind.NAME, text=_get_text(field.find("field_name"))))
                type_elements.extend(_get_type_elements(field.find("field_body"), type_elements))
        elif element.tag == "warning":
            pass
        else:
            _raise_element_error(element, "Unexpected element")

    return type_elements


def _get_type_from_paragraph(type_paragraph: Element) -> Type:
    return Type(text=_get_text(type_paragraph), elements=_get_type_elements(type_paragraph))


def _get_type_from_paragraphs(type_paragraphs: List[Element]) -> Type:
    type: Optional[Type] = None

    for type_paragraph in type_paragraphs:
        new_type = _get_type_from_paragraph(type_paragraph)
        if type is None:
            type = new_type
            continue

        type.update(new_type)

    return type


def _get_type_from_parameter(desc_parameter: Element) -> Type:
    return Type(text=_get_parameter_name_from_parameter(desc_parameter), elements=[])


def _get_parameter_name_from_paragraph(parameter_paragraph: Element) -> str:
    literal_strong: Optional[Element] = parameter_paragraph.find("literal_strong")
    if literal_strong is not None:
        return _get_text(literal_strong)
    else:
        return _get_text(parameter_paragraph)


def _get_parameter_name_from_parameter(desc_parameter: Element) -> str:
    desc_sig_name: Optional[Element] = desc_parameter.find("desc_sig_name")

    if desc_sig_name is None:
        return ""

    return _get_text(desc_sig_name)


def _parse_member_attribute(member_desc_element: Element) -> Attribute:
    name: Optional[Element] = _get_text(member_desc_element.find("desc_signature/desc_name"))
    type_paragraphs: List[Element] = member_desc_element.findall("desc_content/field_list//paragraph")

    return Attribute(name=name, type=_get_type_from_paragraphs(type_paragraphs), annotations=[])


def _parse_member_data(member_desc_element: Element) -> Data:
    name: Optional[Element] = _get_text(member_desc_element.find("desc_signature/desc_name"))
    type_paragraphs: List[Element] = member_desc_element.findall("desc_content/field_list//paragraph")

    return Data(name=name, type=_get_type_from_paragraphs(type_paragraphs), annotations=[])


def _parse_class(class_desc_element: Element) -> Class:
    base_classes_paragraph = class_desc_element.xpath(
        "self::desc/preceding-sibling::paragraph[starts-with(text(),'base class')]"
    )
    class_full_qualified_name = class_desc_element.find("desc_signature").attrib["ids"]

    return Class(
        name=class_full_qualified_name,
        base_classes=[_get_type_from_paragraph(p) for p in base_classes_paragraph]
        if base_classes_paragraph is not None
        else [],
        attributes=[_parse_member_attribute(e) for e in class_desc_element.findall("desc_content/desc[@desctype='attribute']")],
        datas=[_parse_member_data(e) for e in class_desc_element.findall("desc_content/desc[@desctype='data']")],
        methods=[m for e in class_desc_element.findall("desc_content/desc[@desctype='method']") for m in _parse_fuction(e)],
        annotations=[],
    )


def _parse_data(data_desc_element: Element) -> Data:
    desc_signature: Optional[Element] = data_desc_element.find("desc_signature")
    name: str = desc_signature.attrib.get("ids", _get_text(desc_signature))
    type_paragraphs: List[Element] = data_desc_element.findall("desc_content/paragraph")

    return Data(name=name, type=_get_type_from_paragraphs(type_paragraphs), annotations=[])


def _parse_fuction(function_desc_element: Element) -> List[Method]:
    def get_annotations_from_desc_signature(desc_signature: Element) -> List[str]:
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

    def get_field_paragraphs(function_desc_element):
        field_paragraphs: List[Element] = function_desc_element.xpath(
            "desc_content/field_list/field/field_name[text()='Parameters']/following-sibling::field_body//paragraph[not(ancestor::paragraph)]"
        )
        paragraphs_length = len(field_paragraphs)
        paragraph_name2counts: Dict[str, int] = functools.reduce(
            lambda acc, name: {**acc, name: acc.get(name, 0) + 1},
            (_get_parameter_name_from_paragraph(p) for p in field_paragraphs),
            {},
        )
        if paragraphs_length != len(paragraph_name2counts):
            _log_warning(function_desc_element, f"[Recover] Merge duplicate parameters: {paragraph_name2counts}")

        return field_paragraphs

    def get_return_type(function_desc_element):
        return_type_paragraphs: List[Element] = function_desc_element.xpath(
            "desc_content/field_list/field/field_name[text()='Return type']/following-sibling::field_body/paragraph"
        )
        return_paragraphs: List[Element] = function_desc_element.xpath(
            "desc_content/field_list/field/field_name[text()='Returns']/following-sibling::field_body/paragraph"
        )

        # merge return_type_paragraphs and return_paragraphs,
        # because the return type is sometimes in the return_paragraphs
        return_type_paragraphs.extend(return_paragraphs)
        return_type = _get_type_from_paragraphs(return_type_paragraphs) if len(return_type_paragraphs) > 0 else TYPE_NONE
        return return_type

    methods: List[Method] = []

    desc_signatures: List[Element] = function_desc_element.findall("desc_signature")
    if len(desc_signatures) == 0:
        _raise_element_error(function_desc_element, "No desc_signature found")

    # field_paragraphs are shared by all desc_signatures
    field_paragraphs_cache = get_field_paragraphs(function_desc_element)

    return_type = get_return_type(function_desc_element)

    for desc_signature in desc_signatures:
        name: str = _get_text(desc_signature.find("desc_name"))
        annotations: List[str] = get_annotations_from_desc_signature(desc_signature)

        desc_parameters: List[Element] = desc_signature.xpath("desc_parameterlist/desc_parameter")
        field_paragraphs = field_paragraphs_cache.copy()

        desc_parameters_length = len(desc_parameters)
        desc_parameter_name2counts: Dict[str, int] = functools.reduce(
            lambda acc, name: {**acc, name: acc.get(name, 0) + 1},
            (_get_parameter_name_from_parameter(p) for p in desc_parameters),
            {},
        )
        if desc_parameters_length != len(desc_parameter_name2counts):
            _raise_element_error(function_desc_element, f"Duplicate parameter names: {desc_parameter_name2counts}")

        parameters: List[Parameter] = []

        def new_parameter_from_parameter(desc_parameter: Element, type: Optional[Type] = None) -> Parameter:
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

            name = _get_parameter_name_from_parameter(desc_parameter)
            operator = get_desc_sig_operator_from_parameter(desc_parameter)

            # if target_name is empty, it must be a keyword-only parameter
            if name == "" and operator != "*":
                _raise_element_error(parameter, f"Parameter name is empty in {name}")

            return Parameter(
                name=name,
                type=type or _get_type_from_parameter(desc_parameter),
                operator=operator,
                default_value=get_default_value_from_parameter(desc_parameter),
            )

        def new_parameter_from_paragraph(paragraph: Element) -> Parameter:
            return Parameter(
                name=_get_parameter_name_from_paragraph(paragraph),
                type=_get_type_from_paragraph(paragraph),
                operator=None,
                default_value=None,
            )

        while len(desc_parameters) > 0 and len(field_paragraphs) > 0:
            target_name = _get_parameter_name_from_parameter(desc_parameters[0])

            if target_name == "":
                parameters.append(new_parameter_from_parameter(desc_parameters.pop(0)))
                continue

            field_paragraphs_search_range_index = next(
                iter(i + 1 for i, v in enumerate(desc_parameters[1:]) if _get_parameter_name_from_parameter(v) == target_name),
                len(field_paragraphs),
            )

            # find all field_paragraphs values with the same name as target_name
            match_field_paragraphs_index2values = {
                i: v
                for i, v in enumerate(field_paragraphs[:field_paragraphs_search_range_index])
                if _get_parameter_name_from_paragraph(v) == target_name
            }

            # if there are any field_paragraphs values with the same name as target_name, add them to the result
            if len(match_field_paragraphs_index2values) > 0:
                parameter = desc_parameters.pop(0)
                type = _get_type_from_parameter(parameter)

                for v in match_field_paragraphs_index2values.values():
                    type.update(_get_type_from_paragraph(v))

                # remove match_field_paragraphs_index2values.keys() from field_paragraphs
                field_paragraphs = [
                    v for i, v in enumerate(field_paragraphs) if i not in match_field_paragraphs_index2values.keys()
                ]

                parameters.append(new_parameter_from_parameter(parameter, type))
                continue

            field_paragraph_name = _get_parameter_name_from_paragraph(field_paragraphs[0])
            match_desc_parameters_index = next(
                iter(i for i, v in enumerate(desc_parameters) if _get_parameter_name_from_parameter(v) == field_paragraph_name),
                None,
            )

            if match_desc_parameters_index is not None and len(field_paragraphs) > match_desc_parameters_index:
                # move field_paragraphs[0] to desc_parameters cooresponding position
                field_paragraphs.insert(match_desc_parameters_index, field_paragraphs.pop(0))

            parameter = desc_parameters.pop(0)
            parameters.append(new_parameter_from_parameter(parameter))

        remain_desc_parameters_length = len(desc_parameters)
        remain_field_paragraphs_length = len(field_paragraphs)

        # append the remaining desc_parameters
        for parameter in desc_parameters:
            new_parameter = new_parameter_from_parameter(parameter)
            if new_parameter.name != "":
                _log_warning(parameter, f"Unmatched parameter: {_get_parameter_name_from_parameter(parameter)} in {name}")
            parameters.append(new_parameter_from_parameter(parameter))

        if (len(desc_signatures) == 1 and desc_parameters_length == 0) or remain_desc_parameters_length > 0:
            # corrupted desc_parameters or remaining desc_parameters
            # append the remaining field_paragraphs
            for paragraph in field_paragraphs:
                _log_warning(paragraph, f"Unmatched parameter: {_get_parameter_name_from_paragraph(paragraph)} in {name}")
                parameters.append(new_parameter_from_paragraph(paragraph))

        methods.append(
            Method(
                name=name,
                return_type=return_type,
                parameters=parameters,
                annotations=annotations,
            )
        )
    return methods


def _log_warning(element: Element, message: str, *args, **kwargs):
    logging.warning(
        f"""{message}\n  File {element.getroottree().docinfo.URL}:{element.sourceline} in <{element.tag}>""", *args, **kwargs
    )


def _raise_element_error(element: Element, message: str) -> None:
    raise ValueError(f"""{message}\n  File {element.getroottree().docinfo.URL}:{element.sourceline} in <{element.tag}>""")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        document: lxml.etree._ElementTree = lxml.etree.parse(arg)
        for class_desc_element in document.xpath("//desc[@desctype='class']"):
            _parse_class(class_desc_element)

        for data_desc_element in document.xpath("//section/desc[@desctype='data']"):
            _parse_data(data_desc_element)

        for function_desc_element in document.xpath("//section/desc[@desctype='function']"):
            _parse_fuction(function_desc_element)
