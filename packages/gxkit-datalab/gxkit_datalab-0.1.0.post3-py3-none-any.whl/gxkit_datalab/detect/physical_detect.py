from typing import Dict, Tuple, Optional, List, Union, Sequence

import pandas as pd

from gxkit_datalab.exception import DetectError
from gxkit_datalab.utils.convert import convert_columns
from gxkit_datalab.utils.normalize import norm_rule
from gxkit_datalab.encode.bitmask import encode_bitmask


def rule_det(df: pd.DataFrame, columns: Optional[Union[str, Sequence[str], pd.Index]], rule: str,
             bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None, merge: bool = False,
             col_mask: str = "rule", prefix: str = "bm", fill: Optional[Union[float, int]] = None,
             split_flag: str = "|") -> pd.DataFrame:
    """pandas规则检测: 输入类query规则进行检测"""
    tgt_cols: List[str] = convert_columns(df, columns)
    bm_cols: List[str] = convert_columns(df, bm_columns) if bm_columns is not None else list(df.columns)

    # 规则标准化与评估：在 df 全列空间下校验
    rule_expr, _ = norm_rule(rule, df.columns)
    try:
        mask = _eval_rule(rule_expr, df)
    except Exception as e:
        raise DetectError("datalab.detect.rule_det", f"Invalid rule: {rule_expr} | {e}") from e

    flags = {c: mask for c in tgt_cols}
    bm_name = _bm_base(prefix, col_mask)
    bm_df = _encode(flags, bm_cols, bm_name, split_flag)

    if not merge and fill is None:
        return bm_df

    out = df.copy()
    _apply_fill(out, flags, fill)
    return pd.concat([out, bm_df], axis=1)


def rules_det(df: pd.DataFrame, rules: Dict[str, Tuple[Union[str, Sequence[str], pd.Index], str]],
              bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None, merge: bool = False,
              col_mask: str = "rule", bm_prefix: str = "bm", fill: Optional[Union[float, int]] = None,
              split_flag: str = "|") -> pd.DataFrame:
    """pandas规则检测: 输入多个规则进行检测"""
    if not rules:
        raise DetectError("datalab.detect.rules_det", "rules cannot be empty")

    bm_cols: List[str] = convert_columns(df, bm_columns) if bm_columns is not None else list(df.columns)
    out = df.copy()
    bm_parts: List[pd.DataFrame] = []

    for rule_name, (cols, rule_str) in rules.items():
        tgt_cols = convert_columns(df, cols)
        expr, _ = norm_rule(rule_str, df.columns)
        try:
            mask = _eval_rule(expr, df)  # 用原 df 评估，避免前一条掩码影响后一条判断
        except Exception as e:
            raise DetectError("datalab.detect.rules_det", f"[{rule_name}] Invalid rule: {expr} | {e}") from e

        flags = {c: mask for c in tgt_cols}
        bm_name = _bm_base(bm_prefix, col_mask, rule_name)
        bm_df = _encode(flags, bm_cols, bm_name, split_flag)
        bm_parts.append(bm_df)

        _apply_fill(out, flags, fill)

    bm_all = pd.concat(bm_parts, axis=1) if bm_parts else pd.DataFrame(index=df.index)
    if not merge and fill is None:
        return bm_all
    return pd.concat([out, bm_all], axis=1)


def threshold_det(df: pd.DataFrame, limits: Dict[str, Tuple[float, float]],
                  bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None,
                  merge: bool = False, col_mask: str = "threshold", bm_prefix: str = "bm",
                  fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    """阈值检测函数: 根据上下限对 df 的多个列进行异常检测"""
    bm_cols: List[str] = convert_columns(df, bm_columns) if bm_columns is not None else list(df.columns)
    out = df.copy()

    flags: Dict[str, pd.Series] = {}
    for col, (low, high) in limits.items():
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        flags[col] = ((s < low) | (s > high)).fillna(False)

    bm_name = _bm_base(bm_prefix, col_mask)
    bm_df = _encode(flags, bm_cols, bm_name, split_flag)

    if not merge and fill is None:
        return bm_df

    _apply_fill(out, flags, fill)
    return pd.concat([out, bm_df], axis=1)


def flatline_det(df: pd.DataFrame, columns: Optional[Union[str, Sequence[str], pd.Index]] = None, window: int = 4,
                 bm_columns: Optional[Union[str, Sequence[str], pd.Index]] = None, drop_special: bool = True,
                 merge: bool = True, col_mask: str = "flatline", bm_prefix: str = "bm",
                 fill: Optional[Union[float, int]] = None, split_flag: str = "|") -> pd.DataFrame:
    """平稳波动检测: 连续window个值完全相同即视为异常"""
    if window <= 1:
        raise ValueError("window must be greater than 1")

    tgt_cols: List[str] = convert_columns(df, columns) if columns is not None else list(df.columns)
    bm_cols: List[str] = convert_columns(df, bm_columns) if bm_columns is not None else list(df.columns)
    out = df.copy()

    flags: Dict[str, pd.Series] = {}
    for col in tgt_cols:
        s = pd.to_numeric(df[col], errors="coerce")
        grp = s.ne(s.shift()).cumsum()
        size = grp.groupby(grp, dropna=False).transform("size")
        first = s.groupby(grp, dropna=False).transform("first")
        m = (size >= window)
        if drop_special:
            m &= ~(first.isna() | (first == 0))
        flags[col] = m.fillna(False)

    bm_name = _bm_base(bm_prefix, col_mask)
    bm_df = _encode(flags, bm_cols, bm_name, split_flag)

    if not merge and fill is None:
        return bm_df

    _apply_fill(out, flags, fill)
    return pd.concat([out, bm_df], axis=1)


def _bm_base(bm_prefix: str, col_mask: str, rule_name: Optional[str] = None) -> str:
    base = f"{bm_prefix}_{col_mask}" if bm_prefix else col_mask
    return f"{base}_{rule_name}" if rule_name else base


def _eval_rule(expr: str, df: pd.DataFrame) -> pd.Series:
    try:
        s = df.eval(expr, engine="numexpr")
    except Exception:
        s = df.eval(expr, engine="python")
    if not isinstance(s, pd.Series):
        raise DetectError("datalab.detect.eval_rule", f"Rule did not return a boolean Series: {type(s)}")
    return s.reindex(df.index).fillna(False).astype(bool)


def _encode(flags: Dict[str, pd.Series], bm_columns: List[str], bm_name: str, sep: str) -> pd.DataFrame:
    """封装字符串位图编码：输出列名为 f"{bm_name}_str"。"""
    return encode_bitmask(flags, columns=bm_columns, col_mask=bm_name, split_flag=sep)


def _apply_fill(df: pd.DataFrame, flags: Dict[str, pd.Series], fill: Optional[Union[float, int]]) -> None:
    """原地掩码：把命中的 (row, col) 置为 fill；flags 中不存在的列自动跳过。"""
    if fill is None:
        return
    for col, m in flags.items():
        if col in df.columns:
            m = m.reindex(df.index).fillna(False).to_numpy()
            if m.any():
                df.loc[m, col] = fill
