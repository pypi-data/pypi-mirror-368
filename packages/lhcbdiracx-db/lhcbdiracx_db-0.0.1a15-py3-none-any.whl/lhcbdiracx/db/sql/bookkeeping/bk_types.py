from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Double,
    Integer,
    Numeric,
    String,
    types,
)
from sqlalchemy.dialects.oracle import CHAR as CHAR_oracle
from sqlalchemy.dialects.oracle import DOUBLE_PRECISION as DOUBLE_PRECISION_oracle
from sqlalchemy.dialects.oracle import NUMBER as NUMBER_oracle
from sqlalchemy.dialects.oracle import TIMESTAMP as TIMESTAMP_oracle
from sqlalchemy.dialects.oracle import VARCHAR as VARCHAR_oracle

from .functions import boolean_type_default

"""
Deals with sqlite-oracle dialect differences to ensure
the bookkeeping schema can be expressed in both using
the SQLAlchemy models with common types.

TypeDecorator or UserDefinedType becomes necessary as
with_variant(..., "dialect") and the type engine does
not always behave as expected!
"""


class FTypeTypeOracle(types.UserDefinedType):
    def get_col_spec(self, **kw):
        return "FTYPE"

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        connection = dialect.context.connection.connection
        oracle_type = connection.gettype("FTYPE")
        obj = oracle_type.newobject()
        obj.NAME = value.get("name")

        visible = value.get("visible")
        if isinstance(visible, bool):
            obj.VISIBLE = "Y" if value.get("visible") else "N"
        elif isinstance(visible, str) and visible in ["Y", "N"]:
            obj.VISIBLE = visible
        else:
            raise NotImplementedError(
                "Visible is not bool or length-1 str of 'Y' or 'N'."
            )
        return obj

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return {"name": value.NAME, "visible": value.VISIBLE}


class FiletypesArrayTypeOracle(types.UserDefinedType):
    def get_col_spec(self, **kw):
        return "FILETYPESARRAY"

    def process_bind_param(self, value, dialect):
        # Get the FTypeType bind processor
        ftype = FTypeTypeOracle()
        if value is None:
            return None
        connection = dialect.context.connection.connection
        oracle_type = connection.gettype("FILETYPESARRAY")

        new_array = oracle_type.newobject()
        for elem in value:
            processed_elem = ftype.process_bind_param(elem, dialect) if ftype else elem
            new_array.append(processed_elem)
        return new_array

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        ftype = FTypeTypeOracle()
        return [ftype.process_result_value(elem, dialect) for elem in value]


def StringType(N):
    return String(N).with_variant(VARCHAR_oracle(N), "oracle")


FileTypesArrayType = JSON().with_variant(FiletypesArrayTypeOracle(), "oracle")

TimestampType = TIMESTAMP(False).with_variant(TIMESTAMP_oracle(), "oracle")
NumberType = (
    Numeric(asdecimal=False)
    .with_variant(NUMBER_oracle(asdecimal=False), "oracle")
    .with_variant(Integer(), "mysql")
)  # MySQL does not support NUMBER with AUTOINCREMENT
DoubleType: Double = Double().with_variant(DOUBLE_PRECISION_oracle(), "oracle")

BooleanType = String(1).with_variant(CHAR_oracle(1), "oracle")
GotReplicaType = String(3).with_variant(VARCHAR_oracle(3), "oracle")

# Server defaults
GotReplicaYes = "Yes"
GotReplicaNo = "No"


def GotReplicaDefault(value):
    return boolean_type_default(value, yes_value=GotReplicaYes, no_value=GotReplicaNo)
