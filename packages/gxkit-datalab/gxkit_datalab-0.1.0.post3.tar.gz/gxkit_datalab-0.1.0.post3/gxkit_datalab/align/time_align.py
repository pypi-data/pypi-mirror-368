"""
datalab.align
 - time_align 时间对齐工具
Version 0.1.0
"""
from typing import Optional, Literal

import pandas as pd

from gxkit_datalab.exception import AlignError
from gxkit_datalab.utils.convert import convert_df_datetime
from gxkit_datalab.utils.check import check_dt_and_samp


def time_align(df: pd.DataFrame, col_time: str, col_mask: str = "time_anomaly", sampling: int = 300,
               anomaly_interval: Optional[int] = None, keep_time_diff: bool = False,
               method: Literal["nearest", "backward"] = "nearest", time_unit: Literal["ms", "s", "ns"] = "ms"):
    """
        异常类型 1-时间缺失 2-重复隐射 3-无数据
    """
    df = df.copy()
    # step1 时间转换
    df = convert_df_datetime(df, col_time, "datetime", time_unit)
    # step2 鲁棒性检测
    check_dt_and_samp(df, "datetime", sampling, "all")
    # step3 采样与对齐
    df = df.sort_values(by="datetime").set_index("datetime")
    df[col_mask] = 0
    if anomaly_interval is None:
        anomaly_interval = sampling * 0.6
    start_time = df.index.min().ceil(f"{sampling}s")
    end_time = df.index.max().floor(f"{sampling}s")
    target_index = pd.date_range(start=start_time, end=end_time, freq=f"{sampling}s")

    try:
        method_pandas = method
        if method == "backward":
            method_pandas = "bfill"

        if method == "nearest":
            df_resampled = df.resample(f"{sampling}s").nearest()
            aligned_index = df_resampled.index
            nearest_idx = df.index.get_indexer(aligned_index, method="nearest")

        elif method == "backward":
            aligned_index = target_index
            nearest_idx = df.index.get_indexer(aligned_index, method="bfill")
            df_resampled = df.iloc[nearest_idx].copy()
            df_resampled.index = aligned_index

        else:
            if not hasattr(df.resample(f"{sampling}s"), method_pandas):
                raise ValueError(f"unsupported resample method: {method}")
            df_resampled = getattr(df.resample(f"{sampling}s"), method_pandas)()
            aligned_index = df_resampled.index
            nearest_idx = df.index.get_indexer(aligned_index, method=method_pandas)

        valid_mask = nearest_idx >= 0
        time_diff = pd.Series(index=aligned_index, dtype="float64")
        aligned_ts = pd.Series(aligned_index, index=aligned_index)
        mapped_ts = pd.Series(index=aligned_index, dtype="datetime64[ns]")
        mapped_ts[valid_mask] = df.index.to_series().iloc[nearest_idx[valid_mask]].values
        time_diff[valid_mask] = (aligned_ts[valid_mask] - mapped_ts[valid_mask]).dt.total_seconds()
        df_resampled["time_diff"] = time_diff.abs()

        df_resampled[col_mask] = 0
        df_resampled.loc[~valid_mask, col_mask] = 3
        df_resampled.loc[(df_resampled["time_diff"] > anomaly_interval) & valid_mask, col_mask] = 1

        if method == "nearest":
            normal_mask = df_resampled[col_mask] == 0
            safe_idx = df_resampled[normal_mask].index
            valid_nearest_idx = pd.Series(nearest_idx[valid_mask], index=aligned_index[valid_mask])
            valid_nearest_idx = valid_nearest_idx[valid_nearest_idx.index.isin(safe_idx)]
            nearest_counts = valid_nearest_idx.value_counts()
            for idx, count in nearest_counts.items():
                if count > 1:
                    mapped_rows = valid_nearest_idx[valid_nearest_idx == idx].index
                    min_idx = df_resampled.loc[mapped_rows, "time_diff"].idxmin()
                    drop_idx = mapped_rows.difference([min_idx])
                    df_resampled.loc[drop_idx, col_mask] = 2

        # step4 清理中间字段
        df_resampled["datetime"] = df_resampled.index
        df_resampled[col_time] = df_resampled["datetime"].astype("int64") // 10 ** 6
        if not keep_time_diff:
            df_resampled.drop(columns=["time_diff"], inplace=True)
        df_resampled.drop(columns=["datetime"], inplace=True)
        return df_resampled.reset_index(drop=True).sort_values(by=col_time).reset_index(drop=True)
    except Exception as e:
        raise AlignError("datalab.align.time_align", str(e)) from e
