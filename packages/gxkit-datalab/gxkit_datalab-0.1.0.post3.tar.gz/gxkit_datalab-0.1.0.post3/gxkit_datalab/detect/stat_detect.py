from typing import Optional, List, Union, Sequence, Dict

import numpy as np
import pandas as pd
from statistics import NormalDist

from gxkit_datalab.utils.convert import convert_columns
from gxkit_datalab.encode.bitmask import encode_bitmask


# ---------------- 1) 全局 Z-score ----------------

def zscore_det(df: pd.DataFrame, threshold: float = 3.0,
               columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
               bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
               merge: bool = False, col_mask: str = "zscore", bm_prefix: str = "bm",
               fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        sd = s.std(skipna=True)
        if not np.isfinite(sd) or sd == 0:
            m = pd.Series(False, index=df.index)
        else:
            mu = s.mean(skipna=True)
            m = (s - mu).abs() > threshold * sd
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 2) 全局 MAD ----------------

def mad_det(df: pd.DataFrame, threshold: float = 3.5,
            columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
            bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
            merge: bool = False, col_mask: str = "mad", bm_prefix: str = "bm",
            fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    scale = 1.4826
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        med = s.median(skipna=True)
        mad = (s - med).abs().median(skipna=True)
        if not np.isfinite(mad) or mad == 0:
            m = pd.Series(False, index=df.index)
        else:
            m = (s - med).abs() > threshold * scale * mad
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 3) 全局 IQR ----------------

def iqr_det(df: pd.DataFrame, factor: float = 1.5,
            columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
            bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
            merge: bool = False, col_mask: str = "iqr", bm_prefix: str = "bm",
            fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        if not np.isfinite(iqr) or iqr == 0:
            m = pd.Series(False, index=df.index)
        else:
            lower, upper = q1 - factor * iqr, q3 + factor * iqr
            m = (s < lower) | (s > upper)
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 4) 滚动 Z-score ----------------

def rolling_zscore_det(df: pd.DataFrame, window: int = 10, threshold: float = 3.0,
                       columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                       bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                       merge: bool = False, col_mask: str = "roll_zscore", bm_prefix: str = "bm",
                       fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    minp = max(3, min(window, len(df)))
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        mu = s.rolling(window, min_periods=minp).mean()
        sd = s.rolling(window, min_periods=minp).std()
        z = (s - mu).abs() / sd
        m = (sd > 0) & (z > threshold)
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 5) 滚动 MAD ----------------

def rolling_mad_det(df: pd.DataFrame, window: int = 10, threshold: float = 3.5,
                    columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                    bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                    merge: bool = False, col_mask: str = "roll_mad", bm_prefix: str = "bm",
                    fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    minp = max(3, min(window, len(df)))
    scale = 1.4826
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        med = s.rolling(window, min_periods=minp).median()
        mad = (s - med).abs().rolling(window, min_periods=minp).median()
        thr = threshold * scale * mad
        m = (mad > 0) & ((s - med).abs() > thr)
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 6) 滚动 IQR ----------------

def rolling_iqr_det(df: pd.DataFrame, window: int = 10, factor: float = 1.5,
                    columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                    bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                    merge: bool = False, col_mask: str = "roll_iqr", bm_prefix: str = "bm",
                    fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    minp = max(3, min(window, len(df)))
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        q1 = s.rolling(window, min_periods=minp).quantile(0.25)
        q3 = s.rolling(window, min_periods=minp).quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - factor * iqr, q3 + factor * iqr
        m = (iqr > 0) & ((s < lower) | (s > upper))
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 7) 趋势漂移（短长均线差） ----------------

def trend_shift_det(df: pd.DataFrame, short_window: int = 5, long_window: int = 20, threshold: float = 2.0,
                    columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                    bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                    merge: bool = False, col_mask: str = "trend", bm_prefix: str = "bm",
                    fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    if long_window <= short_window:
        long_window = short_window * 2
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    minp_s = max(3, min(short_window, len(df)))
    minp_l = max(3, min(long_window, len(df)))
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        s_mean = s.rolling(short_window, min_periods=minp_s).mean()
        l_mean = s.rolling(long_window, min_periods=minp_l).mean()
        l_std = s.rolling(long_window, min_periods=minp_l).std()
        diff = (s_mean - l_mean).abs()
        m = (l_std > 0) & (diff > threshold * l_std)
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 8) Hampel 滤波 ----------------

def hampel_filter_det(df: pd.DataFrame, window: int = 7, n_sigma: float = 3.0,
                      columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                      bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                      merge: bool = False, col_mask: str = "hampel", bm_prefix: str = "bm",
                      fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    minp = max(3, min(window, len(df)))
    scale = 1.4826
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        med = s.rolling(window, center=True, min_periods=minp).median()
        mad = (s - med).abs().rolling(window, center=True, min_periods=minp).median()
        thr = n_sigma * scale * mad
        m = (mad > 0) & ((s - med).abs() > thr)
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 9) Grubbs（正态近似临界值） ----------------

def grubbs_det(df: pd.DataFrame, alpha: float = 0.05,
               columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
               bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
               merge: bool = False, col_mask: str = "grubbs", bm_prefix: str = "bm",
               fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    norm = NormalDist()
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        v = s.dropna()
        n = len(v)
        if n < 3:
            flags[c] = pd.Series(False, index=df.index)
            continue
        sd = v.std(ddof=1)
        if not np.isfinite(sd) or sd == 0:
            flags[c] = pd.Series(False, index=df.index)
            continue
        mu = v.mean()
        # 正态近似：用 z 近似 t
        z = norm.inv_cdf(1 - alpha / (2 * n))
        g_crit = (n - 1) / np.sqrt(n) * np.sqrt(z * z / (n - 2 + z * z))
        m = ((s - mu).abs() / sd) > g_crit
        flags[c] = m.fillna(False)
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


# ---------------- 10) Generalized ESD（正态近似） ----------------

def esd_test_det(df: pd.DataFrame, max_outliers: int = 5, alpha: float = 0.05,
                 columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                 bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                 merge: bool = False, col_mask: str = "esd", bm_prefix: str = "bm",
                 fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    cols = convert_columns(df, columns)
    bm_cols = _bm_cols(df, bm_columns)
    norm = NormalDist()
    flags: Dict[str, pd.Series] = {}
    for c in cols:
        s = _to_num(df[c])
        v = s.dropna()
        out_idx: List[int] = []
        for i in range(min(max_outliers, len(v))):
            n = len(v)
            if n < 3:
                break
            sd = v.std(ddof=1)
            if not np.isfinite(sd) or sd == 0:
                break
            mu = v.mean()
            dev = (v - mu).abs()
            idx = dev.idxmax()
            Ri = dev.loc[idx] / sd
            # 正态近似：用 z 近似 t
            z = norm.inv_cdf(1 - alpha / (2 * (n - i)))
            lam = (n - i - 1) / np.sqrt(n - i) * np.sqrt(z * z / (n - i - 2 + z * z))
            if Ri > lam:
                out_idx.append(idx)
                v = v.drop(idx)
            else:
                break
        m = pd.Series(False, index=df.index)
        if out_idx:
            m.loc[out_idx] = True
        flags[c] = m
    return _finish(df, flags, bm_cols, bm_prefix, col_mask, merge, fill, split_flag)


def _bm_name(prefix: str, col_mask: str) -> str:
    return f"{prefix}_{col_mask}" if prefix else col_mask


def _bm_cols(df: pd.DataFrame, bm_columns) -> List[str]:
    return convert_columns(df, bm_columns) if bm_columns is not None else list(df.columns)


def _to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _apply_fill_inplace(df: pd.DataFrame, flags: Dict[str, pd.Series], fill: Optional[Union[float, int]]) -> None:
    if fill is None:
        return
    for col, m in flags.items():
        if col in df.columns:
            mm = m.reindex(df.index).fillna(False).to_numpy()
            if mm.any():
                df.loc[mm, col] = fill


def _finish(df: pd.DataFrame, flags: Dict[str, pd.Series],
            bm_cols: List[str], bm_prefix: str, col_mask: str,
            merge: bool, fill: Optional[Union[float, int]], split_flag: str) -> pd.DataFrame:
    bm = encode_bitmask(flags, columns=bm_cols, col_mask=_bm_name(bm_prefix, col_mask), split_flag=split_flag)
    if not merge and fill is None:
        return bm
    out = df.copy()
    _apply_fill_inplace(out, flags, fill)
    return pd.concat([out, bm], axis=1)
