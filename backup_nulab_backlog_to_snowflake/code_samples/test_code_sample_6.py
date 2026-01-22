from typing import Annotated, Any, Literal, Optional
import pytest

from .code_sample_6 import ClassParser


@pytest.fixture(scope="module")
def class_parser():
    return ClassParser()


class ClassWithNoTypeHints:
    a = 0
    b = 1


def test_ClassWithNoTypeHints(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithNoTypeHints)
    assert res.get("fields") == []


class ClassWithAtomicTypeHints:
    a: int
    b: str
    c: bool
    d: float


def test_ClassWithAtomicTypeHints(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithAtomicTypeHints)
    assert res.get("fields") == [
        {"name": "a", "type": "integer", "nullable": False},
        {"name": "b", "type": "string", "nullable": False},
        {"name": "c", "type": "boolean", "nullable": False},
        {"name": "d", "type": "float", "nullable": False},
    ]


class ClassWithAtomicTypeHintsAndDefaultValues:
    a: int = 0
    b: str = "some value"


def test_ClassWithAtomicTypeHintsAndDefaultValues(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithAtomicTypeHintsAndDefaultValues)
    assert res.get("fields") == [
        {"name": "a", "type": "integer", "nullable": False},
        {"name": "b", "type": "string", "nullable": False},
    ]


class ClassWithOptionalField:
    a: Optional[int]
    b: str


def test_ClassWithOptionalField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithOptionalField)
    assert res.get("fields") == [
        {"name": "a", "type": "integer", "nullable": True},
        {"name": "b", "type": "string", "nullable": False},
    ]


class ClassWithLiteralField:
    a: Literal[0, 1]
    b: str


def test_ClassWithLiteralField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithLiteralField)
    assert res.get("fields") == [
        {"name": "a", "type": "integer", "nullable": False},
        {"name": "b", "type": "string", "nullable": False},
    ]


class ClassWithDictionaryField:
    a: dict[str, int]
    b: str


def test_ClassWithDictionaryField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithDictionaryField)
    assert res.get("fields") == [
        {"name": "a", "type": "variant", "nullable": False},
        {"name": "b", "type": "string", "nullable": False},
    ]


class ClassWithListField:
    a: list[str]
    b: str
    c: list[int] | None


def test_ClassWithListField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithListField)
    assert res.get("fields") == [
        {"name": "a", "type": "variant", "nullable": False},
        {"name": "b", "type": "string", "nullable": False},
        {"name": "c", "type": "variant", "nullable": True},
    ]


class ClassWithTupleField:
    a: tuple[str, int]
    b: str
    c: tuple[int, int] | None


def test_ClassWithTupleField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithTupleField)
    assert res.get("fields") == [
        {"name": "a", "type": "variant", "nullable": False},
        {"name": "b", "type": "string", "nullable": False},
        {"name": "c", "type": "variant", "nullable": True},
    ]


class ClassWithNullableAtomicField:
    a: str | None
    b: int


def test_ClassWithNullableAtomicField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithNullableAtomicField)
    assert res.get("fields") == [
        {"name": "a", "type": "string", "nullable": True},
        {"name": "b", "type": "integer", "nullable": False},
    ]


class ClassWithNullableDictionaryField:
    a: dict[str, Any] | None
    b: int


def test_ClassWithNullableDictionaryField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithNullableDictionaryField)
    assert res.get("fields") == [
        {"name": "a", "type": "variant", "nullable": True},
        {"name": "b", "type": "integer", "nullable": False},
    ]


class ClassWithNullableLiteralField:
    a: Literal["approved", "pending"] | None
    b: int


def test_ClassWithNullableLiteralField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithNullableLiteralField)
    assert res.get("fields") == [
        {"name": "a", "type": "string", "nullable": True},
        {"name": "b", "type": "integer", "nullable": False},
    ]


class ClassWithUnionField:
    a: str | int
    b: int


def test_ClassWithUnionField(class_parser: ClassParser):
    with pytest.raises(ValueError):
        class_parser.parse_class(ClassWithUnionField)


class ClassWithAnnotatedField:
    a: Annotated[str, "some_metadata"]
    b: str


def test_ClassWithAnnotatedField(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithAnnotatedField)
    assert res.get("fields") == [
        {"name": "a", "type": "string", "nullable": False},
        {"name": "b", "type": "string", "nullable": False},
    ]


class ClassWithAnnotatedFieldWithSnowflakeDatatype:
    a: Annotated[str, "timestamp_ntz"]
    b: str


def test_ClassWithAnnotatedFieldWithSnowflakeDatatype(class_parser: ClassParser):
    res = class_parser.parse_class(ClassWithAnnotatedFieldWithSnowflakeDatatype)
    assert res.get("fields") == [
        {"name": "a", "type": "timestamp_ntz", "nullable": False},
        {"name": "b", "type": "string", "nullable": False},
    ]


class ClassWithAnnotatedFieldWithSnowflakeDatatypeWithUnionType:
    a: Annotated[str | int, "timestamp_ntz"]
    b: str


def test_ClassWithAnnotatedFieldWithSnowflakeDatatypeWithUnionType(
    class_parser: ClassParser,
):
    with pytest.raises(ValueError):
        class_parser.parse_class(
            ClassWithAnnotatedFieldWithSnowflakeDatatypeWithUnionType
        )


class ClassWithAnnotatedFieldWithSnowflakeDatatypeNullable:
    a: Annotated[str | None, "timestamp_ntz"]
    b: str


def test_ClassWithAnnotatedFieldWithSnowflakeDatatypeNullable(
    class_parser: ClassParser,
):
    res = class_parser.parse_class(ClassWithAnnotatedFieldWithSnowflakeDatatypeNullable)
    assert res.get("fields") == [
        {"name": "a", "type": "timestamp_ntz", "nullable": True},
        {"name": "b", "type": "string", "nullable": False},
    ]


class ClassWithAnnotatedFieldWithSnowflakeDatatypeNullableWithLiteralType:
    a: Annotated[Literal["2025-12-29 17:34:09"] | None, "timestamp_ntz"]
    b: str


def test_ClassWithAnnotatedFieldWithSnowflakeDatatypeNullableWithLiteralType(
    class_parser: ClassParser,
):
    res = class_parser.parse_class(
        ClassWithAnnotatedFieldWithSnowflakeDatatypeNullableWithLiteralType
    )
    assert res.get("fields") == [
        {"name": "a", "type": "timestamp_ntz", "nullable": True},
        {"name": "b", "type": "string", "nullable": False},
    ]


class ClassWithAnnotatedFieldWithTWOSnowflakeDatatype:
    a: Annotated[str, "timestamp_ntz", "variant"]
    b: str


def test_ClassWithAnnotatedFieldWithTWOSnowflakeDatatype(class_parser: ClassParser):
    with pytest.raises(ValueError):
        class_parser.parse_class(ClassWithAnnotatedFieldWithTWOSnowflakeDatatype)
