"""
datalab.interp.stat_interpolate
 - pandas_interp pandas插值器
 - scipy_interp scipy插值器
Version 0.1.0
"""

from typing import Optional, Sequence, Union, Literal, Dict, Tuple

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d, PchipInterpolator, Akima1DInterpolator, CubicSpline

from gxkit_datalab.exception import InterpolateError
from gxkit_datalab.utils.convert import convert_columns

PANDAS_METHOD = Literal["linear", "polynomial", "spline", "time", "pad", "nearest", "barycentric", "akima", "cubic"]
DIRECTION = Literal["forward", "backward", "both"]
SCIPY_METHOD = Literal["linear", "cubic", "pchip", "akima", "spline"]
DEFAULT_INTERP_RULE = {
    1: "linear",
    2: "linear",
    3: "pchip",
    4: "pchip",
    5: "akima",
    6: "spline"
}


def pandas_interp(data: Union[pd.DataFrame, pd.Series], columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                  method: PANDAS_METHOD = "linear", limit_direction: DIRECTION = "both",
                  **kwargs) -> Union[pd.DataFrame, pd.Series]:
    """使用 pandas 插值方法对指定列（或单个 Series）中的缺失或异常值进行插值填补"""
    if isinstance(data, pd.Series):
        series = pd.to_numeric(data, errors="coerce")
        try:
            return series.interpolate(method=method, limit_direction=limit_direction, **kwargs)
        except Exception as e:
            raise InterpolateError("datalab.interp.pandas_interp", str(e)) from e
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
        columns = convert_columns(df, columns)
        for col in columns:
            series = pd.to_numeric(df[col], errors="coerce")
            try:
                df[col] = series.interpolate(method=method, limit_direction=limit_direction, **kwargs)
            except Exception as e:
                raise InterpolateError("datalab.interp.pandas_interp", str(e)) from e
        return df
    else:
        raise TypeError("Only Series or DataFrame are supported for pandas_interp.")


def scipy_interp(x: np.ndarray, y: np.ndarray, method: SCIPY_METHOD = "linear",
                 target_index: Optional[np.ndarray] = None) -> np.ndarray:
    """使用 scipy 插值方法对指定 x/y 序列进行插值填补"""
    if len(x) != len(y):
        raise ValueError("[scipy_interp] x and y must be the same length")
    if len(x) < 2:
        raise ValueError("[scipy_interp] Need at least 2 points for interpolation")
    if target_index is None:
        target_index = np.arange(len(y))

    try:
        methods = {
            "linear": lambda x, y: interp1d(x, y, kind="linear", bounds_error=False, fill_value=np.nan),
            "cubic": lambda x, y: interp1d(x, y, kind="cubic", bounds_error=False, fill_value=np.nan),
            "pchip": lambda x, y: PchipInterpolator(x, y, extrapolate=False),
            "akima": lambda x, y: Akima1DInterpolator(x, y),
            "spline": lambda x, y: CubicSpline(x, y, extrapolate=False)
        }
        f = methods[method](x, y)
        return f(target_index)
    except Exception as e:
        raise InterpolateError("datalab.interp.scipy_interp", str(e)) from e


def dynamic_interp(series: pd.Series,
                   strategy: Optional[Dict[int, SCIPY_METHOD]] = None,
                   max_missing: int = 6) -> Tuple[pd.Series, pd.Series]:
    """动态插值法 """
    series = series.copy()
    bad_mask = pd.Series(False, index=series.index)

    strategy = strategy or DEFAULT_INTERP_RULE
    is_na = series.isna()
    group_id = (is_na != is_na.shift()).cumsum()
    for _, group in series[is_na].groupby(group_id):
        start, end = group.index[0], group.index[-1]
        idx_start = series.index.get_loc(start)
        idx_end = series.index.get_loc(end)
        n_missing = idx_end - idx_start + 1

        # 判断是否超长
        if n_missing > max_missing:
            bad_mask[start:end] = True
            continue

        # 构造局部窗口（前后各取2个点）
        left = max(0, idx_start - 2)
        right = min(len(series), idx_end + 3)
        window = series.iloc[left:right]
        window_index = window.index.to_numpy()

        valid = window.notna()
        x = window_index[valid.to_numpy()]
        y = window[valid].to_numpy()
        target_index = window_index[~valid.to_numpy()]

        if len(x) < 2:
            bad_mask[start:end] = True
            continue

        method = strategy.get(n_missing, "linear")
        try:
            filled = scipy_interp(x=x, y=y, method=method, target_index=target_index)
            series.loc[target_index] = filled
        except Exception:
            bad_mask[start:end] = True

    return series, bad_mask
