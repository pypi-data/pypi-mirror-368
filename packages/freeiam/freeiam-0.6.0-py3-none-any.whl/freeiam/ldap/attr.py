# SPDX-FileCopyrightText: 2025 Florian Best
# SPDX-License-Identifier: MIT OR Apache-2.0
"""LDAP Attributes."""

import contextlib
import typing


class Attributes(dict):  # noqa: FURB189
    """LDAP Attributes."""

    ALIASES: typing.ClassVar = {}
    SCHEMA = None

    def __getitem__(self, key):
        with contextlib.suppress(KeyError):
            return super().__getitem__(key)
        return self.__missing__(key)

    def __missing__(self, key):
        key = self.ALIASES.get(key, key)
        return {k.lower(): v for k, v in self.items()}[key.lower()]

    @classmethod
    def set_schema(cls, subschema):
        """Set aliases from schema."""
        cls.SCHEMA = subschema
        cls.ALIASES.update(subschema.get_attribute_aliases())
