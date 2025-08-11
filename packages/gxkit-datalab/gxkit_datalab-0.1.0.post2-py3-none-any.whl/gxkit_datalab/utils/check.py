"""
datalab.utils.check 检测工具包
 - check_dt_and_samp DataFrame中NaT值检测工具
Version 0.1.0
"""
from typing import Literal, Optional, Union, List, Sequence

import pandas as pd

from gxkit_datalab.exception import CheckError


def check_dt_and_samp(df: pd.DataFrame, col_datetime: str, sampling: int, mode: Literal["all", "any"] = "all"):
    """检测DataFrame中是否有NaT值"""
    valid_times = df[col_datetime].dropna()
    if mode == "all":
        if valid_times.empty:
            raise CheckError("datalab.utils.check_col_datetime", "All datetime values are NaT.")
    elif mode == "any":
        if df[col_datetime].isna().any():
            raise CheckError("datalab.utils.check_col_datetime", "Datetime column contains NaT values.")
    if valid_times.min() == valid_times.max():
        raise CheckError("datalab.utils.check_col_datetime", "datetime range is zero.")
    if sampling <= 0:
        raise CheckError("datalab.utils.check_col_datetime", "Sampling must be greater than 0.")


def check_columns(checks: List[str], columns: List[str]):
    missing_cols = set(checks) - set(columns)
    if missing_cols:
        raise CheckError("datalab.utils.convert_columns", f"These columns not exist: {sorted(missing_cols)}")
