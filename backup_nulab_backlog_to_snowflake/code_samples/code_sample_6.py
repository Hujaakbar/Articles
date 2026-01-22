from dataclasses import dataclass
from pprint import pprint
from types import NoneType, UnionType
from typing import (
    Annotated,
    Any,
    Literal,
    NoReturn,
    TypedDict,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

# Create table definition from dataclass metadata


@dataclass(frozen=True, kw_only=True)
class BacklogActivity:
    activity_id: int
    type_id: int
    activity_type: str
    project_id: int
    project_key: str
    project_name: str
    content: dict[str, Any]
    creator_id: int
    creator_name: str
    creator_email_address: str | None
    creator_nulab_account_id: str
    creator_nulab_unique_id: str
    created_at: Annotated[str, "timestamp_ntz"]


class ColumnDefinition(TypedDict):
    name: str
    type: str
    nullable: bool


class ClassParser:
    """
    Parses the class attributes that use type hinting and generates column definitions compatible with Snowflake Snowpark API.
    If class attribute does not use type hinting, it is omitted from generated column definitions.
    """

    def __init__(self):
        pass

    @property
    def snowflake_supported_types(self):
        return {
            "string",
            "integer",
            "float",
            "decimal",
            "double",
            "short",
            "long",
            "boolean",
            "variant",
            "timestamp",
            "timestamp_tz",
            "timestamp_ltz",
            "timestamp_ntz",
            # There are more supported types
        }

    @snowflake_supported_types.setter
    def snowflake_supported_types(self, value: Any) -> NoReturn:
        raise ValueError("Assigning value is not allowed")

    def parse_class(self, _class: object) -> dict[str, list[ColumnDefinition]]:
        """
        takes a class, not a class instance, and returns a dictionary of column definitions inferred from class attributes.

        class fields cannot contain more than two types.
        If a field contains two types, one of the types must be NoneType.

        To specify Snowflake specific field such as TIMESTAMP_NTZ, use Annotated type hints
        e.g.

        ```python
        class A:
            field1: Annotated[str, "timestamp_ntz"]
        ```
        """

        columns: list[ColumnDefinition] = []
        for fieldname, type_hint in get_type_hints(_class, include_extras=True).items():
            result = self._parse_type_hint(type_hint)
            datatype, nullable = result
            columns.append(
                ColumnDefinition(name=fieldname, type=datatype, nullable=nullable)
            )
        return {"fields": columns}

    def _parse_type_hint(self, type_hint: object | UnionType) -> tuple[str, bool]:
        """
        returns a tuple of (datatype, nullable): tuple[str, bool]
        """
        datatype = ""
        nullable = False

        if res := self._parse_annotated_type(type_hint):
            if res["snowflake_type"]:
                datatype = res["snowflake_type"]
                nullable = True if self._parse_union_type(res["origin_type"]) else False
                return (datatype, nullable)
            type_hint = res["origin_type"]

        # get_origin function supports generic types, Callable, Tuple, Union, Literal, Final, ClassVar,
        # Annotated, and others. Returns None for unsupported types.
        # get_origin never returns Optional, instead it returns Union
        complex_type = get_origin(type_hint)
        if res := self._parse_union_type(type_hint):
            main_type, nullable = res[0], res[1]
            type_hint = main_type  # main type is any type hint except for None
            complex_type = get_origin(main_type)
        if complex_type is Literal:
            atomic_type = get_args(type_hint)[0]
            datatype = self._translate_atomic_type(atomic_type)
        if complex_type in [dict, list, TypedDict, tuple]:
            datatype = "variant"
        if not complex_type:
            datatype = self._translate_atomic_type(type_hint)
        return (datatype, nullable)

    def _parse_annotated_type(self, type_hint: Any) -> dict[str, Any] | None:
        """
        returns dict of snowflake_type:str and origin_type: Any

        returns None if given type_hint is not Annotated

        If Annotated does not contain Snowflake data types,
        it returns `{"snowflake_type": "", "original_type": origin_type}`
        """
        if get_origin(type_hint) is not Annotated:
            return

        metadata = [
            metadata.strip().lower()
            for metadata in type_hint.__metadata__
            if isinstance(metadata, str)
        ]
        snow_types = self.snowflake_supported_types.intersection(metadata)

        if len(snow_types) > 1:
            raise ValueError(
                "Annotated cannot contain more than one snowflake data type"
            )

        snowflake_type = snow_types.pop() if snow_types else ""
        origin_type = type_hint.__origin__
        return {"snowflake_type": snowflake_type, "origin_type": origin_type}

    def _parse_union_type(self, type_hint: Any) -> tuple[object, bool] | None:
        """
        returns None if given type_hint is not UnionType

        UnionType must contain only two types and one of these types must be NoneType.

        Raises exception if UnionType does not include NoneType.
        """
        types = get_args(type_hint)
        nullable = True
        if get_origin(type_hint) not in [Union, UnionType] or len(types) < 2:
            return
        if len(types) > 2:
            raise ValueError("Union type cannot contain more than two types")
        if NoneType not in types:
            raise ValueError("Union type must include NoneType")
        main_type = types[0] if types[0] is not NoneType else types[1]

        return (main_type, nullable)

    def _translate_atomic_type(self, atomic_type: object) -> str:
        snowflake_type = ""
        if atomic_type is str or isinstance(atomic_type, str):
            snowflake_type = "string"
        if atomic_type is int or isinstance(atomic_type, int):
            snowflake_type = "integer"
        if atomic_type is float or isinstance(atomic_type, float):
            snowflake_type = "float"
        if atomic_type is bool or isinstance(atomic_type, bool):
            snowflake_type = "boolean"
        if not snowflake_type:
            raise RuntimeError(
                f"{atomic_type=} is not defined in this method thus can't be translated"
            )
        return snowflake_type


def create_column_definitions():
    parser = ClassParser()
    pprint(parser.parse_class(BacklogActivity), sort_dicts=False)


if __name__ == "__main__":
    create_column_definitions()
