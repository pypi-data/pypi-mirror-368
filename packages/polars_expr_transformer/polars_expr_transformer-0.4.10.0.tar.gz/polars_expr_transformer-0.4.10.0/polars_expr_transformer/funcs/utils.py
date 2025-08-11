import polars as pl
from typing import Any
import os
from polars.datatypes.group import NUMERIC_DTYPES


PlStringType = pl.Expr | str
PlIntType = pl.Expr | int
PlNumericType = NUMERIC_DTYPES


def is_polars_expr(v: Any) -> bool:
    return isinstance(v, pl.Expr)


def create_fix_col(val: Any) -> pl.Expr:
    return pl.lit(val)


def create_fix_date_col(s: Any) -> pl.Expr:
    return pl.lit(s).str.to_datetime()
