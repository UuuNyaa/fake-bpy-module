import io
from typing import Any, Dict, List, Optional, Tuple, Union

from parsy import Parser, alt, string

Result = Union[Parser, Any]


class __Node:
    def __init__(self):
        self.children: Dict[str, "__Node"] = {}
        self.value: Optional[Result] = None

    def to_string_with_indent(self, indent: int = 0) -> str:
        return "".join(
            "  " * indent + f"""{n}: {c.value if c.value else ""}\n""" + c.to_string_with_indent(indent + 1)
            for n, c in sorted(self.children.items(), key=lambda x: x[0])
        )


def __build_trie_from_str(*values: str) -> __Node:
    root = __Node()

    for value in values:
        current = root
        for char in value:
            current = current.children.setdefault(char, __Node())
        current.value = value

    return root


def __build_trie_from_tuple(*expected_string_with_result: Tuple[str, Result]) -> __Node:
    root = __Node()

    for match, value in expected_string_with_result:
        current = root
        for char in match:
            current = current.children.setdefault(char, __Node())
        current.value = value

    return root


def __to_radix_tree(trie: __Node) -> __Node:
    def __append(tree: __Node, segment: io.StringIO, trie_node: __Node):
        len_node_children = len(trie_node.children)
        if len_node_children == 1 and trie_node.value is None:
            char, trie_node = next(iter(trie_node.children.items()))
            segment.write(char)
            __append(tree, segment, trie_node)
            return

        if len_node_children == 0:
            new_tree = __Node()
        else:
            new_tree = __to_radix_tree(trie_node)

        if trie_node.value is not None:
            new_tree.value = trie_node.value

        tree.children[segment.getvalue()] = new_tree

    tree = __Node()
    for char, trie in trie.children.items():
        segment = io.StringIO()
        segment.write(char)
        __append(tree, segment, trie)

    return tree


def __to_parser(radix_tree: __Node) -> Parser:
    choices: List[Parser] = []
    for k, v in sorted(radix_tree.children.items(), key=lambda x: -len(x[0])):
        if len(v.children) > 0:
            choices.append(string(k) >> __to_parser(v))

        value = v.value
        if value is None:
            continue

        if isinstance(value, Parser):
            choices.append(string(k) >> value)
        else:
            choices.append(string(k).result(value))

    if len(choices) == 1:
        return choices[0]

    return alt(*choices)


def strings(*expected_strings: str) -> Parser:
    """
    Creates a parser from the passed in argument list of strings.
    Arguments are converted to a prefix tree for fast matching.

    Args:
        *expected_strings: The strings to match.

    Returns:
        A parser that matches the arguments.
    """
    return __to_parser(__to_radix_tree(__build_trie_from_str(*expected_strings)))


def strings_from_tuple(*expected_string_with_result: Tuple[str, Result]) -> Parser:
    """
    Creates a parser from the passed in argument list of string and result tuples.
    Arguments are converted to a prefix tree for fast matching.

    Args:
        *expected_string_with_result: The strings to match and their corresponding result.

    Returns:
        A parser that matches the arguments.
    """
    return __to_parser(__to_radix_tree(__build_trie_from_tuple(*expected_string_with_result)))
