"""
datalab.mark.missing
 - mark_missing_columns 标记缺失列
Version 0.1.0
"""
from typing import List

import pandas as pd


def mark_missing_columns(df: pd.DataFrame, threshold: float = 0.9) -> List[str]:
    """检测缺失比例超过给定阈值的列"""
    if not (0 < threshold < 1):
        raise ValueError("threshold must be between 0 and 1")

    null_ratio = df.isna().mean()
    missing_columns = null_ratio[null_ratio > threshold].index.tolist()
    return missing_columns
