import io
import logging
import os
import sys
from types import NoneType
from typing import Final, Iterable, Union, cast

import parse_xml
from parse_xml import Attribute, Class, Data, Method, Module, Parameter, Type, TypeElementQualifier
from parse_type import DataType, parse_type, Hint

_logger = logging.getLogger(__name__)


def render_data_type(out: io.StringIO, data_type: DataType):
    t = data_type.type
    out.write(
        {
            bool: "bool",
            bytes: "bytes",
            int: "int",
            float: "float",
            str: "str",
            bool: "bool",
            NoneType: "None",
            type: "type",
        }.get(t, str(t))
    )


def render_type(type: Type) -> Union[str, DataType]:
    data_type = parse_type(type)


def render_type(out: io.StringIO, type: Type):
    render_data_type(out, parse_type(type))


def render_member_attribute(out: io.StringIO, attribute: Attribute):
    data_type = parse_type(attribute.type)

    if data_type.hints in Hint.READONLY:
        out.write(f"    @property")
        out.write(os.linesep)
        out.write(f"    def {attribute.name}() -> ")
        render_data_type(out, data_type)
        out.write(f": ...")
        out.write(os.linesep)

    else:
        out.write(f"    {attribute.name}: ")
        render_data_type(out, data_type)

        if data_type.default_value is not None:
            out.write(f" = {data_type.default_value}")
        out.write(os.linesep)


def render_member_data(out: io.StringIO, data: Data):
    render_member_attribute(out, data)


def render_class(out: io.StringIO, cls: Class):
    def render_base_classes(base_class_types: Iterable[Type]):
        need_separator = False
        for base_class_type in base_class_types:
            for element in base_class_type.elements:
                if not element.is_qualifier():
                    raise ValueError(f"Unexpected type element kind: {element.kind}")

                if need_separator:
                    out.write(", ")
                else:
                    need_separator = True

                out.write(cast(TypeElementQualifier, element).qualifier)

    out.write(f"class {cls.full_name}")
    if len(cls.base_class_types) > 0:
        out.write("(")
        render_base_classes(cls.base_class_types)
        out.write(")")
    out.write(":")
    out.write(os.linesep)

    for attribute in cls.attributes:
        render_member_attribute(out, attribute)

    for data in cls.datas:
        render_member_data(out, data)

    for method in cls.methods:
        render_method(out, method)

    out.write(os.linesep)


def render_method(out: io.StringIO, method: Method):
    need_separator = False
    out.write(f"    def {method.name}(")
    for parameter in method.parameters:
        if need_separator:
            out.write(", ")
        else:
            need_separator = True
        render_parameter(out, parameter)
    out.write(")")
    if method.return_type is not None:
        return_data_type = parse_type(method.return_type)
        if return_data_type.hints in Hint.READONLY:
            _logger.debug("Unsupport return type (readonly): %s", str(method))

        out.write(" -> ")
        render_data_type(out, return_data_type)
    out.write(": ...")
    out.write(os.linesep)


def render_parameter(out: io.StringIO, parameter: Parameter):
    if parameter.operator and parameter.operator != "=":
        # * or **
        out.write(parameter.operator)

    if parameter.name != "":
        out.write(f"{parameter.name}: ")

        data_type = parse_type(parameter.type)
        if Hint.READONLY in data_type.hints:
            _logger.warning("Unsupport parameter type (readonly): %s", data_type)

        render_data_type(out, data_type)

    if data_type.default_value is not None:
        if parameter.default_value is not None:
            _logger.warning("Conflict default value: %s, %s", parameter, data_type.default_value)
            out.write(f" = {parameter.default_value}")
        else:
            out.write(f" = {data_type.default_value}")
    elif parameter.default_value is not None:
        out.write(f" = {parameter.default_value}")


def render_data(out: io.StringIO, data: Data):
    out.write(f"{data.name}: ")
    data_type = parse_type(data.type)
    if Hint.READONLY in data_type.hints:
        data_type = DataType(Final[data_type.type], data_type.default_value, data_type.hints)
    render_data_type(out, data_type)

    if data_type.default_value is not None:
        out.write(f" = {data_type.default_value!r}")
    out.write(os.linesep)


def render_function(out: io.StringIO, function: Method):
    need_separator = False
    out.write(f"def {function.name}(")
    for parameter in function.parameters:
        if need_separator:
            out.write(", ")
        else:
            need_separator = True
        render_parameter(out, parameter)
    out.write(")")
    if function.return_type is not None:
        out.write(" -> ")
        render_type(out, function.return_type)
    out.write(": ...")
    out.write(os.linesep)


def render_module(out: io.StringIO, module: Module):
    for data in module.datas:
        render_data(out, data)
        out.write(os.linesep)

    for function in module.functions:
        render_function(out, function)
        out.write(os.linesep)

    for cls in module.classes:
        render_class(out, cls)
        out.write(os.linesep)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s | %(levelname)-.4s | %(name)s | %(message)s",
        level=logging.INFO,
    )

    _logger.info("Start")

    for arg in sys.argv[1:]:
        print(arg)
        module = parse_xml.parse_module(arg)

        render_module(sys.stdout, module)
