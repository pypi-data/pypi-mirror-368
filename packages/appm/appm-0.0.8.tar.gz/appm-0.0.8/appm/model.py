from __future__ import annotations

import re
from collections import Counter
from typing import Self

from pydantic import BaseModel, model_validator
from ruamel.yaml import YAML

from appm.__version__ import __version__
from appm.exceptions import FileFormatMismatch
from appm.utils import slugify

yaml = YAML()

STRUCTURES = {"year", "summary", "internal", "researcherName", "organisationName"}


class Field(BaseModel):
    name: str
    pattern: str
    required: bool = True

    @property
    def regex(self) -> str:
        return f"(?P<{self.name}>{self.pattern})"

    @property
    def js_regex(self) -> str:
        return f"(?<{self.name}>{self.pattern})"

    @classmethod
    def from_tuple(cls, value: tuple[str, str] | list[str]) -> Field:
        assert len(value) == 2
        return Field(name=value[0], pattern=value[1])


class Group(BaseModel):
    components: list[tuple[str, str] | Field | Group]
    sep: str = "-"

    def validate_components(self) -> Self:
        if not self.components:
            raise ValueError(f"Components cannot be empty: {self.components}")
        self._fields: list[Field | Group] = []
        self._normalised_fields: list[Field] = []
        for field in self.components:
            if isinstance(field, tuple | list):
                f = Field.from_tuple(field)
                self._fields.append(f)
                self._normalised_fields.append(f)
            elif isinstance(field, Field):
                self._fields.append(field)
                self._normalised_fields.append(field)
            else:
                self._fields.append(field)
                self._normalised_fields.extend(field.normalised_fields)
        return self

    def validate_names(self) -> Self:
        self._names: list[str] = []
        self._optional_names: set[str] = set()
        for field in self.fields:
            if isinstance(field, Field):
                self._names.append(field.name)
                if not field.required:
                    self._optional_names.add(field.name)
            else:
                self._names.extend(field.names)
                self._optional_names.update(field.optional_names)
        return self

    def validate_regex(self) -> Self:
        regex_str = []
        js_regex_str = []
        for i, field in enumerate(self.fields):
            is_optional = isinstance(field, Field) and not field.required
            pattern = field.regex
            js_pattern = field.js_regex

            if i == 0:
                if is_optional:
                    # First field, no separator; make only field optional
                    regex_str.append(f"(?:{pattern})?")
                    js_regex_str.append(f"(?:{js_pattern})?")
                else:
                    regex_str.append(pattern)
                    js_regex_str.append(js_pattern)
            else:
                if is_optional:
                    # Wrap separator + field together as optional
                    regex_str.append(f"(?:{self.sep}{pattern})?")
                    js_regex_str.append(f"(?:{self.sep}{js_pattern})?")
                else:
                    regex_str.append(f"{self.sep}{pattern}")
                    js_regex_str.append(f"{self.sep}{js_pattern}")
        self._regex = "".join(regex_str)
        self._js_regex = "".join(js_regex_str)
        return self

    @model_validator(mode="after")
    def validate_group(self) -> Self:
        return self.validate_components().validate_names().validate_regex()

    @property
    def normalised_fields(self) -> list[Field]:
        return self._normalised_fields

    @property
    def fields(self) -> list[Field | Group]:
        return self._fields

    @property
    def names(self) -> list[str]:
        return self._names

    @property
    def optional_names(self) -> set[str]:
        return self._optional_names

    @property
    def regex(self) -> str:
        return self._regex

    @property
    def js_regex(self) -> str:
        return self._js_regex


class Extension(Group):
    default: dict[str, str] | None = None

    @property
    def default_names(self) -> set[str]:
        return set() if not self.default else set(self.default.keys())

    @property
    def all_names(self) -> set[str]:
        return set(self.names) | self.default_names

    def validate_regex(self) -> Self:
        super().validate_regex()
        self._regex = f"^{self._regex}(?P<rest>.*)$"
        self._js_regex = f"^{self._js_regex}(?<rest>.*)$"
        return self

    def validate_unique_names(self) -> Self:
        count = Counter(self.names)
        non_uniques = {k: v for k, v in count.items() if v > 1}
        if non_uniques:
            raise ValueError(f"Non-unique field name: {non_uniques}")
        return self

    def validate_reserved_name(self) -> Self:
        if "rest" in self.names:
            raise ValueError("Field component must not contain reserved key: rest")
        return self

    def validate_first_field_must_be_required(self) -> Self:
        if not (field := self.normalised_fields[0]).required:
            raise ValueError(f"First component must be required: {field.name}")
        return self

    @model_validator(mode="after")
    def validate_extension(self) -> Self:
        return (
            self.validate_components()
            .validate_names()
            .validate_regex()
            .validate_unique_names()
            .validate_reserved_name()
            .validate_first_field_must_be_required()
        )

    def match(self, name: str) -> dict[str, str | None]:
        m = re.match(self.regex, name)
        if not m:
            raise FileFormatMismatch(f"Name: {name}. Pattern: {self.regex}")
        result = m.groupdict()
        if self.default:
            for k, v in self.default.items():
                if result.get(k) is None:
                    result[k] = v
        return result


File = dict[str, Extension]


class Layout(BaseModel):
    structure: list[str]
    mapping: dict[str, dict[str, str]] | None = None

    @classmethod
    def from_list(cls, value: list[str]) -> Layout:
        return cls(structure=value)

    @property
    def structure_set(self) -> set[str]:
        return self._structure_set

    @model_validator(mode="after")
    def validate_layout(self) -> Self:
        self._structure_set = set(self.structure)
        if self.mapping and not set(self.mapping.keys()).issubset(self._structure_set):
            raise ValueError(
                f"Mapping keys must be a subset of structure. Mapping keys: {set(self.mapping.keys())}, structure: {self.structure}"
            )
        return self

    def get_path(self, components: dict[str, str | None]) -> str:
        result: list[str] = []
        for key in self.structure:
            value = components.get(key)
            if self.mapping and key in self.mapping and value in self.mapping[key]:
                value = self.mapping[key][value]
            if value is None:
                raise ValueError(
                    f"None value for key: {key}. Either set a default for Extension definition, change Extension pattern to capture key value, or rename file."
                )
            result.append(value)
        return "/".join(result)


class NamingConv(BaseModel):
    sep: str = "_"
    structure: list[str] = [
        "year",
        "summary",
        "internal",
        "researcherName",
        "organisationName",
    ]

    @model_validator(mode="after")
    def validate_naming_convention(self) -> Self:
        """Validate structure value

        structure:
            - cannot be empty
            - cannot have repeated component(s)
            - cannot have a field component that is not one of the metadata fields.
        """
        counter: dict[str, int] = {}
        if len(self.structure) == 0:
            raise ValueError("Invalid naming structure - empty structure")
        for field in self.structure:
            counter[field] = counter.get(field, 0) + 1
            if counter[field] > 1:
                raise ValueError(f"Invalid naming structure - repetition: {field}")
            if field not in STRUCTURES:
                raise ValueError(
                    f"Invalid naming structure - invalid field: {field}. Structure must be a non empty permutation of {STRUCTURES}"
                )
        return self


class Template(BaseModel):
    layout: Layout | list[str]
    file: File
    naming_convention: NamingConv = NamingConv()
    version: str = __version__

    def validate_layout(self) -> Self:
        if isinstance(self.layout, list):
            self._layout = Layout.from_list(self.layout)
        else:
            self._layout = self.layout
        return self

    def validate_file_non_empty(self) -> Self:
        if not self.file:
            raise ValueError("Empty extension")
        return self

    def validate_file_name_subset_layout(self) -> Self:
        for ext, decl in self.file.items():
            for field in self.parsed_layout.structure_set:
                if field not in decl.all_names:
                    raise ValueError(
                        f"Component fields must be a superset of layout fields: {field}. Ext: {ext}"
                    )
                if field in decl.optional_names and field not in decl.default_names:
                    raise ValueError(
                        f"Optional field that is also a layout field must have a default value: {field}. Ext: {ext}"
                    )
        return self

    @property
    def parsed_layout(self) -> Layout:
        return self._layout

    @model_validator(mode="after")
    def validate_template(self) -> Self:
        return self.validate_layout().validate_file_non_empty().validate_file_name_subset_layout()


class Metadata(BaseModel):
    year: int
    summary: str
    internal: bool = True
    researcherName: str | None = None
    organisationName: str | None = None


class Project(Template):
    meta: Metadata

    @property
    def project_name(self) -> str:
        """Project name based on metadata and naming convention definition"""
        fields = self.naming_convention.structure
        name: list[str] = []
        for field in fields:
            value = getattr(self.meta, field)
            if value is not None:
                if isinstance(value, str):
                    name.append(slugify(value))
                elif field == "year":
                    name.append(str(value))
                elif field == "internal":
                    value = "internal" if value else "external"
                    name.append(value)
        return self.naming_convention.sep.join(name)
