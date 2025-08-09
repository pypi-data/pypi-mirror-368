#!/usr/bin/env python3
"""Generate documented YAML files from documented dataclasses."""

import dataclasses
import functools
import logging
import textwrap
from typing import get_args, get_origin

import yaml
from docstring_parser import parse as parse_docstring

from .typing import type_to_string


LOGGER = logging.getLogger(__name__)


class DataclassDocumenter:
    """Generate markdown and YAML documentation from documented dataclasses."""

    def __init__(self, datacls, name=None, width=120, indent_unit="  "):
        """
        Args:
            datacls:
                The dataclass to document.

            name:
                The name to use for this class in the documentation. If None,
                the name of the dataclass will be used.

            width:
                The target output width for wrapped comments.

            indent_unit:
                The string to repeat at the start of each line for each level of
                indentation.
        """
        if not dataclasses.is_dataclass(datacls):
            raise ValueError("First argument is not a dataclass.")
        self.datacls = datacls
        self.name = datacls.__name__ if name is None else name
        self.width = int(width)
        self.indent_unit = indent_unit

    @functools.cached_property
    def docstring(self):
        """The parsed docstring."""
        return parse_docstring(self.datacls.__doc__)

    @functools.cached_property
    def fields(self):
        """The fields of the dataclass."""
        return dataclasses.fields(self.datacls)

    @functools.cached_property
    def params(self):
        """The dict mapping parameter names to DocstrignParam values."""
        return {param.arg_name: param for param in self.docstring.params}

    def get_param_desc(self, param, default=None, warn=False):
        """
        Get the description of a parameter.

        Args:
            param:
                The parameter name.

            default:
                The default value to return if the parameter lacks a description.

            warn:
                If True, log a warning when the description is missing.

        Returns:
            The parameter description.
        """
        try:
            return self.params[param].description
        except KeyError:
            if warn:
                LOGGER.warning("%s is not documented in the docstring.", param)
            return default

    def get_param_type(self, param):
        """
        Get the type of a parameter.

        Args:
            param:
                The parameter name.

        Returns:
            The parameter type.
        """
        return self.datacls.__annotations__[param]

    def _wrap_yaml_comment(self, comment, indent):
        """
        Wrap a YAML comment.

        Args:
            comment:
                The comment to wrap.

            indent:
                The indentation for each line.

        Returns:
            The wrapped lines.
        """
        indent = f"{indent}# "
        for line in textwrap.wrap(
            comment, width=self.width, initial_indent=indent, subsequent_indent=indent
        ):
            yield line.rstrip()

    def _default_as_yaml(self, name, value, indent):
        """
        Wrap YAML output for embedding in another YAML document.

        Args:
            name:
                The field name.

            value:
                The value.

            indent:
                The indentation for the first line.

            commented:
                If True, comment fields.

        Returns:
            The wrapped YAML lines.
        """
        obj = {name: value}
        text = yaml.dump(obj)
        # Replace list markers for subsequent lines.
        indent2 = indent.replace("-", " ")
        for i, line in enumerate(text.splitlines()):
            ind = indent if i == 0 else indent2
            yield f"{ind}{line}"

    def _get_nested_dado(self, datacls):
        """
        Get another instance of this class with the same parameters for emitting
        nested YAML.
        """
        return self.__class__(datacls, width=self.width, indent_unit=self.indent_unit)

    def _get_indents(self, level, commented, in_list, first):
        """
        Internal method for getting indents.

        Args:
            indent:
                The base indent for the current level.

            commented:
                If True, comment the field.

            in_list:
                If True, add extra padding for list items.

            first:
                If True, emit the list marker.

        Returns:
            The field and non-field indent strings.
        """

        field_indent = indent = self.indent_unit * level
        if commented:
            field_indent = f"{indent}# "

        if in_list:
            if first:
                field_indent += f"-{self.indent_unit[1:]}"
            else:
                field_indent += self.indent_unit

        return field_indent, indent

    def get_yaml_blocks(self, level=0, header=None, commented=False, origin=None):
        """
        Get commented YAML input for the dataclass.

        Args:
            level:
                The indentation level.

            header:
                An optional header to emit as a comment at the start of the
                output.

            commented:
                If True, comment all fields.

            origin:
                The optional container type for this object, either dict, list
                or None.

        Returns:
            A generator over blocks of YAML.
        """
        in_list = origin is list
        field_indent, indent = self._get_indents(level, commented, in_list, False)
        empty_line = ""
        if origin is dict:
            yield f"{indent}# String key"
            yield f"{field_indent}key:"
            yield from self.get_yaml_blocks(
                level=level + 1, header=header, commented=commented
            )
            return
        if header is not None:
            yield from self._wrap_yaml_comment(header, indent)
            yield empty_line
        for i, field in enumerate(self.fields):
            field_indent, indent = self._get_indents(level, commented, in_list, i == 0)

            # Output the description from the docstring.
            yield from self._wrap_yaml_comment(
                self.get_param_desc(field.name, default="Undocumented.", warn=True),
                indent,
            )

            # Recursively document dataclasses.
            if dataclasses.is_dataclass(field.type):
                yield f"{field_indent}{field.name}:"
                dado = self._get_nested_dado(field.type)
                yield from dado.get_yaml_blocks(level=level + 1, commented=commented)
                continue

            meta = f"{indent}# Type: {type_to_string(field.type)}"
            if field.default is dataclasses.MISSING:
                if field.default_factory is dataclasses.MISSING:
                    yield f"{meta} [REQUIRED]"
                    yield f"{field_indent}{field.name}: ..."
                else:
                    yield f"{meta} [OPTIONAL]"
                    default = field.default_factory()
                    yield from self._default_as_yaml(
                        field.name,
                        default,
                        field_indent,
                    )
            else:
                yield f"{meta} [OPTIONAL]"
                yield from self._default_as_yaml(
                    field.name,
                    field.default,
                    field_indent,
                )
            emit_empty_line = True
            for arg in get_args(field.type):
                if dataclasses.is_dataclass(arg):
                    dado = self._get_nested_dado(arg)
                    yield from dado.get_yaml_blocks(
                        header=arg.__name__,
                        level=level + 1,
                        commented=True,
                        origin=get_origin(field.type),
                    )
                    emit_empty_line = False

            if emit_empty_line:
                yield empty_line

    def get_yaml(self, level=0, commented=False):
        """
        Get commented YAML input for the dataclass.

        Args:
            level:
                Markdown header level.

            commented:
                If True, comment all lines.
        """
        header = self.name
        return "\n".join(
            self.get_yaml_blocks(level=level, header=header, commented=commented)
        )

    def get_markdown(self, level=0):
        """
        Get a markdown description of the dataclass that contains a commented
        example YAML input file.

        Args:
            level:
                Markdown header level.

        Returns:
            The markdown string.
        """
        level = max(level + 1, 1)
        header_prefix = "#" * level

        docstring = self.docstring
        cls_desc = (docstring.short_description, docstring.long_description)
        cls_desc = [desc for desc in cls_desc if desc]
        if cls_desc:
            cls_desc = "\n\n".join(cls_desc)
        return f"""{header_prefix} {self.name}

{cls_desc}

{header_prefix}# Input

~~~yaml
{self.get_yaml()}
~~~

"""
