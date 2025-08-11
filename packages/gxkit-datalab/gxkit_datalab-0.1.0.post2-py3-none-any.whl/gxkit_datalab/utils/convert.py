"""
datalab.utils.convert 数据类型转换工具包
 - convert_df_datetime DataFrame时间戳转换工具
 - convert_date 日期时区转换工具
 - convert_columns DataFrame-columns获取及转换工具
 - convert_location 经纬度转换工具
Version 0.1.0
"""
from typing import Optional, Union, Tuple, List, Sequence, Dict

import pandas as pd

from gxkit_datalab.exception import ConvertError


def convert_df_datetime(df: pd.DataFrame, col_time: str, col_datetime: str, time_unit: str,
                        timezone: Optional[str] = None) -> pd.DataFrame:
    """将DataFrame的时间戳转换为日期"""
    if df.empty or col_time not in df.columns:
        raise ConvertError("datalab.utils.convert_datetime",
                           f"DataFrame is empty or time column '{col_time}' not found.")

    if not pd.api.types.is_datetime64_any_dtype(df[col_time]):
        try:
            if timezone is not None:
                df[col_datetime] = pd.to_datetime(df[col_time], unit=time_unit, utc=True).dt.tz_convert(timezone)
            else:
                df[col_datetime] = pd.to_datetime(df[col_time], unit=time_unit)
        except Exception as e:
            raise ConvertError("datalab.utils.convert_datetime",
                               f"Failed to convert '{col_time}' to datetime | {e}") from e
    else:
        if timezone is not None:
            try:
                if df[col_time].dt.tz is None:
                    df[col_datetime] = df[col_time].dt.tz_localize("UTC").dt.tz_convert(timezone)
                else:
                    df[col_datetime] = df[col_time].dt.tz_convert(timezone)
            except Exception as e:
                raise ConvertError("datalab.utils.convert_datetime",
                                   f"Failed to convert existing datetime to timezone '{timezone}' | {e}") from e
        else:
            df[col_datetime] = df[col_time]
    return df


def convert_date(date: Union[str, int, pd.Timestamp], time_unit: str, timezone: str = "Asia/Shanghai") -> pd.Timestamp:
    """将时间戳或日期转换为带时区的日期"""
    try:
        if isinstance(date, str):
            date = pd.Timestamp(date)
        elif isinstance(date, int):
            date = pd.Timestamp(date, unit=time_unit)
        elif not isinstance(date, pd.Timestamp):
            raise TypeError(f"Unsupported timestamp type: {type(date)}")
        return date.tz_localize(timezone) if date.tzinfo is None else date.tz_convert(timezone)
    except Exception as e:
        raise ConvertError("datalab.utils.convert_date", str(e)) from e


def convert_columns(df: pd.DataFrame, columns: Optional[Union[Sequence[str], pd.Index, str]]) -> List[str]:
    """统一 DataFrame中的columns"""

    if columns is None:
        cols = list(df.columns)
    elif isinstance(columns, str):
        cols = [columns]
    elif isinstance(columns, pd.Index):
        cols = list(columns)
    else:
        try:
            cols = list(columns)
        except Exception as e:
            raise ConvertError("datalab.utils.convert_columns", str(e)) from e
    missing_cols = set(cols) - set(df.columns)
    if missing_cols:
        raise ConvertError("datalab.utils.convert_columns", f"These columns not exist: {sorted(missing_cols)}")

    return cols


def convert_location(longitude: Union[str, float], latitude: Union[str, float]) -> Tuple[float, float]:
    """转换经纬度为float"""
    try:
        lon = float(longitude)
        lat = float(latitude)
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ConvertError("datalab.utils.convert_location", f"Invalid location: longitude: {lon}, latitude: {lat}")
        return lon, lat
    except Exception as e:
        raise ConvertError("datalab.utils.convert_location", str(e)) from e



