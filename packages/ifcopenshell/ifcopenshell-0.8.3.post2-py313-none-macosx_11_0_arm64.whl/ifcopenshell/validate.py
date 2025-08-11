# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Data validation module


Can be used to run validation on IFC file from the command line:

.. code-block:: bash

    python -m ifcopenshell.validate /path/to/model.ifc --rules

```
$ python -m ifcopenshell.validate -h
usage: validate.py [-h] [--rules] [--json] [--fields] [--spf] files [files ...]

positional arguments:
  files       The IFC file to validate.

options:
  -h, --help  show this help message and exit
  --rules     Run express rules.
  --json      Output in JSON format.
  --fields    Output more detailed information about failed entities (only with --json).
  --spf       Output entities in SPF format (only with --json).
```

"""

from __future__ import annotations
import os
import sys
import json
import functools
import types
import argparse

from collections import namedtuple
from typing import Union, Any, Optional, TYPE_CHECKING
from collections.abc import Iterator
from logging import Logger, Handler

if sys.version_info >= (3, 10):
    from types import EllipsisType
else:
    EllipsisType = type(...)

import ifcopenshell
import ifcopenshell.ifcopenshell_wrapper
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.express.rule_executor

if TYPE_CHECKING:
    import ifcopenshell.simple_spf

named_type = ifcopenshell.ifcopenshell_wrapper.named_type
aggregation_type = ifcopenshell.ifcopenshell_wrapper.aggregation_type
simple_type = ifcopenshell.ifcopenshell_wrapper.simple_type
type_declaration = ifcopenshell.ifcopenshell_wrapper.type_declaration
enumeration_type = ifcopenshell.ifcopenshell_wrapper.enumeration_type
entity_type = ifcopenshell.ifcopenshell_wrapper.entity
select_type = ifcopenshell.ifcopenshell_wrapper.select_type
attribute = ifcopenshell.ifcopenshell_wrapper.attribute
inverse_attribute = ifcopenshell.ifcopenshell_wrapper.inverse_attribute
schema_definition = ifcopenshell.ifcopenshell_wrapper.schema_definition

attribute_types = Union[simple_type, named_type, enumeration_type, select_type, aggregation_type, type_declaration]


class ValidationError(Exception):
    def __init__(self, message, attribute=None):
        super().__init__(message)
        self.attribute = attribute


log_entry_type = namedtuple("log_entry_type", ("level", "message", "instance", "attribute"))


class json_logger:
    def __init__(self):
        self.statements = []
        self.state = {}

    def set_state(self, key: str, value: Any):
        self.state[key] = value

    def log(self, level, message, *args):
        self.statements.append({"level": level, "message": message % args, **self.state})

    def __getattr__(self, level):
        return functools.partial(self.log, level)


simple_type_python_mapping = {
    # @todo should include unicode for Python2
    "string": str,
    "integer": int,
    "real": float,
    "number": (int, float),
    "boolean": bool,
    "logical": {True, False, "UNKNOWN"},
    "binary": str,  # maps to a str of "0" and "1"
}


def annotate_inst_attr_pos(
    inst: Union[ifcopenshell.entity_instance, W.HeaderEntity],
    pos: Union[int, tuple[int, ...]],
    entity_str: str = "",
) -> str:
    """Add a caret annotation to the entity string at the given attribute index.

    :param inst: Instance to annotate.
    :param pos: Attribute index or a tuple of them to annotate.
    :param entity_str: Entity string to annotate. If not provided, ``str(inst)`` is used.

    Example:

    .. code:: python
        annotate_inst_attr_pos(inst, 2)
        # #7=IfcApplication(#6,'0.8.1-alpha241113-xxxxxxx','Bonsai','Bonsai')
        #                                                  ^^^^^^^^
    """

    if isinstance(pos, int):
        pos = (pos,)

    def get_pos() -> Iterator[int]:
        # -1  - outside of entity attributes or on comma.
        # >=0 - current attribute index
        depth = 0
        idx = -1
        for c in entity_str or str(inst):
            if c == "(":
                depth += 1
                if depth == 1:
                    idx = 0
                    yield -1
                else:
                    yield idx
            elif c == ")":
                depth -= 1
                if depth == 0:
                    idx = -1
                    yield -1
                else:
                    yield idx
            elif depth == 1 and c == ",":
                idx += 1
                yield -1
            else:
                yield idx

    return "".join(" ^"[i in pos] for i in get_pos())


def format(val: Any) -> str:
    if isinstance(val, tuple) and val and isinstance(val[0], ifcopenshell.entity_instance):
        return "[\n%s\n    ]" % "\n".join("      {}. {}".format(*x) for x in enumerate(val, start=1))
    else:
        return repr(val)


def assert_valid_inverse(
    attr: inverse_attribute, val: tuple[ifcopenshell.entity_instance], schema: schema_definition
) -> bool:
    b1, b2 = attr.bound1(), attr.bound2()

    if (b1, b2) == (-1, -1):
        invalid = len(val) != 1
    else:
        invalid = len(val) < b1 or (b2 != -1 and len(val) > b2)

    if invalid:
        ent_ref = attr.entity_reference().name()
        attr_ref = attr.attribute_reference().name()
        aggr = attr.type_of_aggregation_string().upper()

        if aggr:
            aggr_str = f'{aggr} [{b1}:{"?" if b2 == -1 else b2}] OF '
        else:
            aggr_str = ""

        attr_formatted = f"{attr.name()} : {aggr_str}{ent_ref} FOR {attr_ref}"

        raise ValidationError(
            f"With inverse:\n    {attr_formatted}\nValue:\n    {format(val)}\nNot valid\n", attr.name()
        )
    return True


select_members_cache: dict[tuple[str, str], set[str]] = {}


def get_select_members(schema: schema_definition, ty: select_type) -> set[str]:
    cache_key = schema.name(), ty.name()
    from_cache = select_members_cache.get(cache_key)
    if from_cache:
        return from_cache

    def inner(ty: select_type) -> Iterator[str]:
        if isinstance(ty, select_type):
            for st in ty.select_list():
                yield from inner(st)
        elif isinstance(ty, entity_type):
            yield ty.name()
            for st in ty.subtypes():
                yield from inner(st)
        elif isinstance(ty, type_declaration):
            # @todo shouldn't we list subtypes (e.g IfcPositiveLengthMeasure -> IfcLengthMeasure) here as well?
            yield ty.name()
        elif isinstance(ty, enumeration_type):
            yield ty.name()
        else:
            # @todo raise exception?
            pass

    v = select_members_cache[cache_key] = set(inner(ty))
    return v


def assert_valid(
    attr_type: attribute_types,
    val: Any,
    schema: schema_definition,
    no_throw=False,
    attr: Optional[attribute] = None,
):
    type_wrappers = (named_type,)
    if not isinstance(val, ifcopenshell.entity_instance):
        # If val is not an entity instance we need to
        # flatten the type declaration to something that
        # maps to the python types
        type_wrappers += (type_declaration,)

    while isinstance(attr_type, type_wrappers):
        attr_type = attr_type.declared_type()

    invalid = False

    if isinstance(attr_type, simple_type):
        simple_type_python = simple_type_python_mapping[attr_type.declared_type()]
        if type(simple_type_python) == set:
            invalid = val not in simple_type_python
        elif type(simple_type_python) == tuple:
            invalid = not any(type(val) == t for t in simple_type_python)
        else:
            invalid = type(val) != simple_type_python
    elif isinstance(attr_type, entity_type):
        invalid = not isinstance(val, ifcopenshell.entity_instance) or not val.is_a(attr_type.name())
    elif isinstance(attr_type, type_declaration):
        # @nb this only applies to direct type declarations, not those indirectly referenced
        # by means of one or more selects.
        invalid = isinstance(val, ifcopenshell.entity_instance)
    elif isinstance(attr_type, select_type):
        if not isinstance(val, ifcopenshell.entity_instance):
            invalid = True
        else:
            value_type = schema.declaration_by_name(val.is_a())
            if not isinstance(value_type, entity_type):
                # we need to check two things: is (enumeration) literal/value valid
                # for this type and is enumeration/value type valid for this select.
                try:
                    invalid = invalid or not assert_valid(value_type, val.wrappedValue, schema, no_throw=True)
                except RuntimeError as _:
                    invalid = True

            # Previously we relied on `is_a(x) for x in attr_type.select_items()`
            # this was linear in the number of select leafs, which is very large
            # for e.g IfcValue, which is an often used select. Therefore, we now
            # calculate (and cache) the select leafs (including entity subtypes)
            # for the select definition and simply check for membership in this
            # set.
            invalid = invalid or val.is_a() not in get_select_members(schema, attr_type)
    elif isinstance(attr_type, enumeration_type):
        invalid = val not in attr_type.enumeration_items()
    elif isinstance(attr_type, aggregation_type):
        b1, b2 = attr_type.bound1(), attr_type.bound2()
        ty = attr_type.type_of_element()
        invalid = type(val) != tuple or (
            len(val) < b1
            or (b2 != -1 and len(val) > b2)
            or not all(assert_valid(ty, v, schema, attr=attr) for v in val)
        )
    else:
        raise NotImplementedError("Not impl %s %s" % (type(attr_type), attr_type))

    if no_throw:
        return not invalid
    elif invalid:
        raise ValidationError(
            f"With attribute:\n    {attr or attr_type}\nValue:\n    {val}\nNot valid\n",
            *([attr.name()] if attr else []),
        )
    else:
        return True


def log_internal_cpp_errors(f: ifcopenshell.file, filename: str, logger: Union[Logger, json_logger]) -> None:
    import re
    import bisect

    chr_offset_re = re.compile(r"at offset (\d+)\s*")
    for_instance_re = re.compile(r"\s*for instance #(\d+)\s*")

    log = ifcopenshell.get_log()
    msgs = list(map(json.loads, filter(None, log.split("\n"))))
    chr_offsets = [chr_offset_re.findall(m["message"]) for m in msgs]
    if chr_offsets:
        # The file is opened in binary mode, in order
        # to correspond with the offsets reported by
        # IfcOpenShell C++
        lines = list(open(filename, "rb"))
        lengths = list(map(len, lines))
        cumsum = 0
        cs = [cumsum := cumsum + x for x in lengths]

        for offsets, msg in zip(chr_offsets, msgs):
            if offsets:
                line = lines[bisect.bisect_left(cs, int(offsets[0]))].decode("ascii", errors="ignore").rstrip()
                m = chr_offset_re.sub("", msg["message"])

                if isinstance(logger, json_logger):
                    logger.set_state("instance", line)
                    logger.set_state("attribute", None)
                    logger.error("%s:\n\n%s" % (m, line))
                else:
                    logger.error("For instance:\n    %s\n%s", line, m)

    instance_messages = [for_instance_re.findall(m["message"]) for m in msgs]
    if instance_messages:
        for instid, msg in zip(instance_messages, msgs):
            if instid:
                m = for_instance_re.sub("", msg["message"])
                try:
                    inst = f[int(instid[0])]
                except:
                    inst = None
                if isinstance(logger, json_logger):
                    logger.set_state("instance", inst)
                    logger.set_state("attribute", None)
                    logger.error(m)
                elif inst:
                    logger.error("For instance:\n    %s\n%s", inst, m)
                else:
                    logger.error(m)


entity_attribute_map: dict[tuple[str, str], tuple[entity_type, tuple[attribute, ...]]] = {}


def get_entity_attributes(schema: schema_definition, entity: str) -> tuple[entity_type, tuple[attribute, ...]]:
    cache_key = schema.name(), entity
    from_cache = entity_attribute_map.get(cache_key)
    if from_cache:
        return from_cache

    ent = schema.declaration_by_name(entity).as_entity()
    assert ent
    entity_attrs = (ent, ent.all_attributes())

    entity_attribute_map[cache_key] = entity_attrs
    return entity_attrs


def validate(f: Union[ifcopenshell.file, str], logger: Union[Logger, json_logger], express_rules=False) -> None:
    """
    For an IFC population model `f` (or filepath to such a file) validate whether the entity attribute values are correctly supplied. As this
    is a function that is applied after a file has been parsed, certain types of errors in syntax, duplicate
    numeric identifiers or invalidate entity names are not caught by this function. Some of these might have been
    logged and can be retrieved by calling `ifcopenshell.get_log()`. A verification of the type, entity and global
    WHERE rules is also not implemented.

    For every entity instance in the model, it is checked that the entity is not abstract that every attribute value
    is of the correct type and that the inverse attributes are of the correct cardinality.

    Express simple types are checked for their valuation type. For select types it is asserted that the value conforms
    to one of the leaves. For enumerations it is checked that the value is indeed on of the items. For aggregations it
    is checked that the elements and the cardinality conforms. Type declarations (IfcInteger which is an integer) are
    unpacked until one of the above cases is reached.

    It is recommended to supply the path to the file, so that internal C++ errors reported during the parse stage
    are also captured.

    Example:

    .. code:: python

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate("/path/to/model.ifc", logger, express_rules=True)
        from pprint import pprint
        pprint(logger.statements)
    """

    # Originally there was no way in Python to distinguish on an entity instance attribute value whether the
    # value supplied in the model was NIL ($) or 'missing because derived in subtype' (*). For validation this
    # however this may be important, and hence a feature switch has been implemented to return *-values as
    # instances of a dedicated type `ifcopenshell.ifcopenshell_wrapper.attribute_value_derived`.
    attribute_value_derived_org = ifcopenshell.ifcopenshell_wrapper.get_feature("use_attribute_value_derived")
    ifcopenshell.ifcopenshell_wrapper.set_feature("use_attribute_value_derived", True)

    filename = None

    if isinstance(logger, json_logger):
        logger.set_state("type", "schema")

    if not isinstance(f, ifcopenshell.file):
        # get_log() clears log existing output
        ifcopenshell.get_log()
        # @todo restore log format
        ifcopenshell.ifcopenshell_wrapper.set_log_format_json()

        filename = f
        try:
            f = ifcopenshell.open(f)
        except ifcopenshell.SchemaError as e:
            current_dir_files = {fn.lower(): fn for fn in os.listdir(".")}
            schema_name = str(e).split(" ")[-1].lower()
            exists = current_dir_files.get(schema_name + ".exp")
            if exists:
                schema = ifcopenshell.express.parse(exists)
                ifcopenshell.register_schema(schema)

                f = ifcopenshell.open(f)
            else:
                logger.error(f"Unsupported schema: {schema_name}")
                return

        assert isinstance(f, ifcopenshell.file)
        log_internal_cpp_errors(f, filename, logger)

    validate_ifc_header(f, logger)
    validate_ifc_applications(f, logger)

    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(f.schema_identifier)
    used_guids: dict[str, ifcopenshell.entity_instance] = dict()

    for inst in f:
        if isinstance(logger, json_logger):
            logger.set_state("instance", inst)

        guid: Union[str, None, EllipsisType]
        if (guid := getattr(inst, "GlobalId", ...)) is not ...:
            if guid is not None and guid in used_guids:
                rule = "Rule IfcRoot.UR1:\n    The attribute GlobalId should be unique"
                previous_element = used_guids[guid]
                logger.error(
                    "On instance:\n    %s\n    %s\n%s\nViolated by:\n    %s\n    %s",
                    inst,
                    annotate_inst_attr_pos(inst, 0),
                    rule,
                    previous_element,
                    annotate_inst_attr_pos(previous_element, 0),
                )
            else:
                if guid is not None:
                    if (validation_error := validate_guid(guid)) is None:
                        used_guids[guid] = inst
                    else:
                        rule = "IfcGloballyUniqueId base64 validation:\n    The attribute GlobalId should be valid base64 encoded 128-bit number."
                        previous_element = None
                        logger.error(
                            "On instance:\n    %s\n    %s\n%s\nViolated by:\n    %s\n",
                            inst,
                            annotate_inst_attr_pos(inst, 0),
                            rule,
                            validation_error,
                        )

        entity, attrs = get_entity_attributes(schema, inst.is_a())

        if entity.is_abstract():
            e = "Entity %s is abstract" % entity.name()
            if isinstance(logger, json_logger):
                logger.set_state("attribute", None)
                logger.error(e)
            else:
                logger.error("For instance:\n    %s\n%s", inst, e)

        has_invalid_value = False
        values = [None] * len(attrs)
        for i in range(len(attrs)):
            try:
                values[i] = inst[i]
                pass
            except:
                if isinstance(logger, json_logger):
                    logger.set_state("attribute", f"{entity.name()}.{attrs[i].name()}")
                    logger.error("Invalid attribute value")
                else:
                    logger.error(
                        "For instance:\n    %s\n    %s\nInvalid attribute value for %s.%s",
                        inst,
                        annotate_inst_attr_pos(inst, i),
                        entity,
                        attrs[i],
                    )
                has_invalid_value = True

        if not has_invalid_value:
            for i, (attr, val, is_derived) in enumerate(zip(attrs, values, entity.derived())):
                if is_derived and not isinstance(val, ifcopenshell.ifcopenshell_wrapper.attribute_value_derived):
                    if isinstance(logger, json_logger):
                        logger.set_state("attribute", f"{entity.name()}.{attr.name()}")
                        logger.error("Attribute is derived in subtype")
                    else:
                        logger.error(
                            "For instance:\n    %s\n    %s\nWith attribute:\n    %s\nDerived in subtype\n",
                            inst,
                            annotate_inst_attr_pos(inst, i),
                            attr,
                        )

                if val is None and not attr.optional() and not is_derived:
                    if isinstance(logger, json_logger):
                        logger.set_state("attribute", f"{entity.name()}.{attr.name()}")
                        logger.error("Attribute not optional")
                    else:
                        logger.error(
                            "For instance:\n    %s\n    %s\nWith attribute:\n    %s\nNot optional\n",
                            inst,
                            annotate_inst_attr_pos(inst, i),
                            attr,
                        )

                if val is not None and not is_derived:
                    attr_type = attr.type_of_attribute()
                    try:
                        assert_valid(attr_type, val, schema, attr=attr)
                    except ValidationError as e:
                        if isinstance(logger, json_logger):
                            logger.set_state("attribute", e.attribute)
                            logger.error(str(e))
                        else:
                            logger.error(
                                "For instance:\n    %s\n    %s\n%s",
                                inst,
                                annotate_inst_attr_pos(inst, i),
                                e,
                            )

        for attr in entity.all_inverse_attributes():
            try:
                val = getattr(inst, attr.name())
            except Exception as e:
                if isinstance(logger, json_logger):
                    logger.set_state("attribute", f"{entity.name()}.{attr.name()}")
                    logger.error(str(e))
                else:
                    logger.error("For instance:\n    %s\n%s", inst, e)
                continue
            try:
                assert_valid_inverse(attr, val, schema)
            except ValidationError as e:
                if isinstance(logger, json_logger):
                    logger.set_state("attribute", f"{entity.name()}.{attr.name()}")
                    logger.error(str(e))
                else:
                    logger.error("For instance:\n    %s\n%s", inst, e)

    if filename:
        # IfcOpenShell uses lazy-loading, so entity instance
        # attributes aren't parsed yet, and counts aren't verified yet.
        # Re capturing the log when validate() is finished
        # iterating over every instance so that all attribute counts
        # are verified.
        log_internal_cpp_errors(f, filename, logger)

    # Restore the original value for 'use_attribute_value_derived'
    ifcopenshell.ifcopenshell_wrapper.set_feature("use_attribute_value_derived", attribute_value_derived_org)

    if express_rules:
        if isinstance(logger, json_logger):
            logger.set_state("instance", None)
            logger.set_state("attribute", None)
        ifcopenshell.express.rule_executor.run(f, logger)


def validate_guid(guid: str) -> Union[str, None]:
    """Check if a given guid is valid.

    Don't check for `None` as `None` guid will trigger "non-optional" validation error either way.

    :return: `None` if guid is valid, otherwise a string with an error message.
    """
    if len(guid) != 22:
        return "Guid length should be 22 characters."
    if guid[0] not in "0123":
        return "Guid first character must be either a 0, 1, 2, or 3."
    try:
        ifcopenshell.guid.expand(guid)
    except:
        allowed_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$"
        if any(c for c in guid if c not in allowed_characters):
            return "Guid contains invalid characters, allowed characters: '%s'." % allowed_characters
        # NOTE: are there actually cases where guid won't expand, besides invalid characters?
        return "Couldn't decompress guid, it's not base64 encoded."
    return None


def to_string_header_entity(header_entity):
    """Recreate IFC header string representation, like FILE_NAME(...)"""

    # Prefer native .toString() if available (native IfcOpenShell wrapper)
    if isinstance(header_entity, W.HeaderEntity):
        return header_entity.toString()
    elif hasattr(header_entity, "_fields"):
        values = [repr(getattr(header_entity, f)) for f in header_entity._fields]
        return f"{type(header_entity).__name__.upper()}({','.join(values)})"
    else:
        raise TypeError(f"Cannot stringify header_entity of type {type(header_entity)}")


def validate_ifc_header(
    f: Union[ifcopenshell.file, ifcopenshell.simple_spf.file], logger: Union[Logger, json_logger]
) -> None:
    header: Union[W.IfcSpfHeader, types.SimpleNamespace] = f.header
    AGGREGATE_TYPE = "LIST [ 1 : ? ] OF STRING (256)"
    STRING_TYPE = "STRING (256)"

    def log_error(
        header_entity: Union[W.HeaderEntity, tuple], name: str, index: int, expected_type: str, provided_type: str
    ) -> None:
        logger.error(
            (
                "For instance:\n    %s\n    %s\n"
                "Attribute '%s' has invalid type:\n"
                "    Expected: %s\n    Current value type: %s\n"
            ),
            (s := to_string_header_entity(header_entity)),
            annotate_inst_attr_pos(header_entity, index, s),
            name,
            expected_type,
            provided_type,
        )

    def validate_attribute(header_entity: W.HeaderEntity, name: str, index: int, *, aggregate: bool = False) -> None:
        try:
            value = getattr(header_entity, name)
        except RuntimeError as _:
            log_error(header_entity, name, index, AGGREGATE_TYPE if aggregate else STRING_TYPE, "INVALID")
            return
        if aggregate:
            if not isinstance(value, tuple):
                log_error(header_entity, name, index, AGGREGATE_TYPE, type(value).__name__)
                return
            if not value:
                log_error(header_entity, name, index, AGGREGATE_TYPE, "EMPTY LIST")
                return
            if not all(isinstance(last_value := v, str) for v in value):
                log_error(
                    header_entity,
                    name,
                    index,
                    AGGREGATE_TYPE,
                    f"LIST with {type(last_value).__name__} (value: {last_value})",
                )
            return

        if not isinstance(value, str):
            log_error(header_entity, name, index, STRING_TYPE, type(value).__name__)

    # Ignore header.file_schema as file won't load to IfcOpenShell with invalid file_schema.
    file_description: W.FileDescription = header.file_description
    validate_attribute(file_description, "description", 0, aggregate=True)
    validate_attribute(file_description, "implementation_level", 1)
    file_name: W.FileName = header.file_name
    validate_attribute(file_name, "name", 0)
    validate_attribute(file_name, "time_stamp", 1)
    validate_attribute(file_name, "author", 2, aggregate=True)
    validate_attribute(file_name, "organization", 3, aggregate=True)
    validate_attribute(file_name, "preprocessor_version", 4)
    validate_attribute(file_name, "originating_system", 5)
    validate_attribute(file_name, "authorization", 6)


def validate_ifc_applications(f: ifcopenshell.file, logger: Union[Logger, json_logger]) -> None:
    used_names: dict[tuple[str, str], ifcopenshell.entity_instance] = dict()
    used_ids: dict[str, ifcopenshell.entity_instance] = dict()

    for inst in f.by_type("IfcApplication"):
        app_name: tuple[str, str] = (inst.ApplicationFullName, inst.Version)
        app_id: str = inst.ApplicationIdentifier

        if all(x is not None for x in app_name):
            if app_name not in used_names:
                used_names[app_name] = inst
            else:
                if isinstance(logger, json_logger):
                    logger.set_state("instance", inst)
                rule = "Rule IfcApplication.UR2:\n    The combination of attributes ApplicationFullName and Version should be unique"
                previous_element = used_names[app_name]
                logger.error(
                    "On instance:\n    %s\n    %s\n%s\nViolated by:\n    %s\n    %s",
                    inst,
                    annotate_inst_attr_pos(inst, (1, 2)),
                    rule,
                    previous_element,
                    annotate_inst_attr_pos(previous_element, (1, 2)),
                )

        if app_id is not None:
            if app_id not in used_ids:
                used_ids[app_id] = inst
            else:
                if isinstance(logger, json_logger):
                    logger.set_state("instance", inst)
                rule = "Rule IfcApplication.UR1:\n    The attribute ApplicationIdentifier should be unique"
                previous_element = used_ids[app_id]
                logger.error(
                    "On instance:\n    %s\n    %s\n%s\nViolated by:\n    %s\n    %s",
                    inst,
                    annotate_inst_attr_pos(inst, 3),
                    rule,
                    previous_element,
                    annotate_inst_attr_pos(previous_element, 3),
                )


class LogDetectionHandler(Handler):
    message_logged = False

    def __init__(self):
        super().__init__()
        self.default_handler = logging.StreamHandler()

    def emit(self, record):
        if not self.message_logged:
            self.message_logged = True
        self.default_handler.emit(record)


if __name__ == "__main__":
    import sys
    import logging

    def handle_exception(exc_type, exc_value, exc_traceback):
        import traceback

        print(f"Unhandled exception: {exc_value}", file=sys.stderr)
        traceback.print_tb(exc_traceback, file=sys.stderr)
        # Exit with a negative code so that it's possible to distinguish
        # internal errors from invalid files.
        sys.exit(-1)

    sys.excepthook = handle_exception

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="The IFC file to validate.")
    parser.add_argument("--rules", action="store_true", help="Run express rules.")
    parser.add_argument("--json", action="store_true", help="Output in JSON format.")
    parser.add_argument(
        "--fields",
        action="store_true",
        help="Output more detailed information about failed entities (only with --json).",
    )
    parser.add_argument("--spf", action="store_true", help="Output entities in SPF format (only with --json).")
    args = parser.parse_args()

    filenames: list[str] = args.files
    some_file_is_invalid = False

    for fn in filenames:
        handler = None
        if args.json:
            logger = json_logger()
        else:
            logger = logging.getLogger("validate")
            handler = LogDetectionHandler()
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

        print("Validating", fn, file=sys.stderr)
        validate(fn, logger, args.rules)

        if args.json:
            sys.stdout.reconfigure(encoding="utf-8")
            conv = str
            if args.spf:
                conv = lambda x: x.to_string() if isinstance(x, ifcopenshell.entity_instance) else str(x)
            if args.fields:

                def conv(x):
                    if isinstance(x, ifcopenshell.entity_instance):
                        return x.get_info(scalar_only=True)
                    else:
                        return str(x)

            for x in logger.statements:
                print(json.dumps(x, default=conv))

        if handler:
            logger.removeHandler(handler)
            invalid_ifc = handler.message_logged
        else:  # json_logger.
            invalid_ifc = bool(logger.statements)

        if invalid_ifc:
            some_file_is_invalid = True
        else:
            print("No validation issues found.")

    if some_file_is_invalid:
        exit(1)
