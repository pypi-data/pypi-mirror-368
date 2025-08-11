"""
datalab.mark.daytime
 - mark_daytime 标记日夜区间工具
 - get_sun_info 获取日出日落工具
Version 0.1.0
"""
from typing import Union, Literal

import numpy as np
import pandas as pd
from pvlib.location import Location

from gxkit_datalab.exception import MarkError
from gxkit_datalab.utils.convert import convert_df_datetime, convert_date, convert_location
from gxkit_datalab.utils.check import check_dt_and_samp


def mark_daytime(df: pd.DataFrame, longitude: Union[str, float], latitude: Union[str, float], col_time: str,
                 col_daytime: str = "daytime", sampling: int = 300, timezone: str = "Asia/Shanghai",
                 time_unit: Literal["ms", "s", "ns"] = "ms") -> pd.DataFrame:
    """0-夜间 1-日间 2-正午"""
    df = df.copy()
    # step1 时间转换
    df = convert_df_datetime(df, col_time, "datetime", time_unit, timezone)
    # step2 鲁棒性检测
    check_dt_and_samp(df, "datetime", sampling, "any")
    # step3 标记日出日落
    try:
        df["_date"] = df["datetime"].dt.normalize()
        unique_dates = df["_date"].unique()
        sun_info_list = []
        for date in unique_dates:
            info = get_sun_info(date, longitude, latitude, timezone)
            if info and all(info.values()):
                sun_info_list.append({
                    "_date": pd.Timestamp(date),
                    "sunrise": info["sunrise"],
                    "sunset": info["sunset"],
                    "transit": info["transit"]
                })
        sun_df = pd.DataFrame(sun_info_list)
        df = df.merge(sun_df, on="_date", how="left")

        cond_noon = (df["datetime"] - df["transit"]).abs() <= pd.Timedelta(seconds=sampling / 2)
        cond_day = (df["datetime"] >= df["sunrise"]) & (df["datetime"] <= df["sunset"])
        df[col_daytime] = np.select(
            [cond_noon, cond_day], [2, 1], default=0
        )
        return df.drop(columns=["_date", "datetime", "sunrise", "sunset", "transit"])
    except Exception as e:
        raise MarkError("datalab.mark.mark_daytime", str(e)) from e


def get_sun_info(date: Union[pd.Timestamp, str, int], longitude: Union[str, float], latitude: Union[str, float],
                 timezone: str = "Asia/Shanghai", time_unit: Literal["ms", "s", "ns"] = "ms"):
    # step1 日期经纬度转换
    date = convert_date(date, time_unit, timezone)
    longitude, latitude = convert_location(longitude, latitude)
    # step2 获取日出日落正午时间
    noon = date.replace(hour=12, minute=0, second=0, microsecond=0)
    try:
        loc = Location(latitude=latitude, longitude=longitude, tz=timezone)
        times = pd.DatetimeIndex([noon], tz=timezone)
        result = loc.get_sun_rise_set_transit(times)
        return {
            "sunrise": result["sunrise"][0],
            "sunset": result["sunset"][0],
            "transit": result["transit"][0]
        }
    except Exception as e:
        raise MarkError("datalab.mark.get_sun_info", str(e)) from e
