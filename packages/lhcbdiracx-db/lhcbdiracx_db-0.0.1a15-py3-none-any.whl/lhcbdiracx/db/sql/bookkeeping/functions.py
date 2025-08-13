from sqlalchemy import func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.types import String


class format_as_char(FunctionElement):
    name = "format_as_char"
    inherit_cache = True


@compiles(format_as_char, "oracle")
def to_char_func_oracle(element, compiler, **kwargs):
    (arg,) = list(element.clauses)
    return compiler.process(func.to_char(arg))


@compiles(format_as_char, "sqlite")
def to_char_func_sqlite(element, compiler, **kwargs):
    (arg,) = list(element.clauses)
    return compiler.process(func.format("%d", arg))


@compiles(format_as_char, "default")
def to_char_func_default(element, compiler, **kwargs):
    (arg,) = list(element.clauses)
    return compiler.process(func.cast(arg, String))


class boolean_type_default(FunctionElement):
    name = "bk_bool_def"
    inherit_cache = True

    def __init__(
        self, value: bool, *args, yes_value="Y", no_value="N", **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._value = value
        self._yes_value = yes_value
        self._no_value = no_value


@compiles(boolean_type_default, "oracle")
def bk_bool_oracle(element, compiler, **kwargs):
    return f"'{element._yes_value}'" if element._value else f"'{element._no_value}'"


@compiles(boolean_type_default, "default")
def bk_bool_default(element, compiler, **kwargs):
    return f"'{element._yes_value}'" if element._value else f"'{element._no_value}'"


class timestamp_now_default(FunctionElement):
    name = "timestamp_now_default"
    inherit_cache = True

    def __init__(
        self, *args, oracle_stmt="sys_extract_utc(systimestamp)", **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._oracle_stmt = oracle_stmt


@compiles(timestamp_now_default, "oracle")
def timestamp_now_default_oracle(element, compiler, **kwargs):
    return element._oracle_stmt


@compiles(timestamp_now_default, "sqlite")
def timestamp_now_default_sqlite(element, compiler, **kwargs):
    return "DATETIME('now')"


@compiles(timestamp_now_default, "default")
def timestamp_now_default_mysql(element, compiler, **kwargs):
    return "NOW()"
