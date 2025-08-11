"""
datalab.encode.bitmask
 - encode_bitmask bitmask编码工具
 - decode_bitmask bitmask解码工具
Version 0.1.0
"""
import re
from typing import Dict, List, Optional, Union, Sequence, Any, Mapping, Literal
from collections import defaultdict

import numpy as np
import pandas as pd

_SEG_BITS = 64


def encode_bitmask(flags: Union[Dict[str, pd.Series], pd.DataFrame], columns: Sequence[str],
                   col_mask: str = "bitmask", split_flag: str = "|") -> pd.DataFrame:
    """bitmask 单规则编码器"""
    # 统一为 DataFrame，并按 columns 对齐
    if isinstance(flags, dict):
        idx = next(iter(flags.values())).index
        flags = pd.DataFrame(flags, index=idx)
    elif not isinstance(flags, pd.DataFrame):
        raise TypeError("flags must be a dict or DataFrame")

    columns = list(columns)
    n_groups = (len(columns) + _SEG_BITS - 1) // _SEG_BITS
    idx = flags.index

    # 取列与填充
    bool_mat = (
        flags.reindex(columns=columns, fill_value=False)
        .astype(np.uint8, copy=False)
        .to_numpy(copy=False)
    )

    # 预先准备 64 位权重，分组时切片即可
    _W64 = (1 << np.arange(_SEG_BITS, dtype=np.uint64))

    seg_list = []
    for g in range(n_groups):
        block = bool_mat[:, g * _SEG_BITS: (g + 1) * _SEG_BITS]
        if block.size == 0:
            seg = np.zeros((len(idx),), dtype=np.uint64)
        else:
            w = _W64[:block.shape[1]]
            seg = (block.astype(np.uint64) * w).sum(axis=1, dtype=np.uint64)
        seg_list.append(seg)

    if seg_list:
        seg_arr = np.column_stack(seg_list)
        bm_str = pd.DataFrame(seg_arr, index=idx, dtype="uint64").astype(str).agg(split_flag.join, axis=1)
    else:
        bm_str = pd.Series("", index=idx)

    return pd.DataFrame({f"{col_mask}_str": bm_str}, index=idx)


def decode_bitmask(bitmask_df: Union[pd.Series, pd.DataFrame], columns: Sequence[str],
                   df: Optional[pd.DataFrame] = None, col_mask: Optional[str] = None,
                   split_flag: str = "|", fill: Union[float, int, None] = np.nan,
                   inplace: bool = False) -> pd.DataFrame:
    """bitmask 单规则解码器"""
    columns = list(columns)
    n_groups = (len(columns) + _SEG_BITS - 1) // _SEG_BITS

    # 取得字符串列
    if isinstance(bitmask_df, pd.Series):
        s = bitmask_df.astype(str)
        idx = s.index
    else:
        if col_mask is None:
            # 自动识别：如果只有唯一一个 *_str，就用它
            str_cols = [c for c in bitmask_df.columns if c.endswith("_str")]
            if len(str_cols) != 1:
                raise ValueError("Please specify col_mask or ensure there is exactly one '*_str' column.")
            col_name = str_cols[0]
        else:
            col_name = f"{col_mask}_str"
            if col_name not in bitmask_df.columns:
                raise ValueError(f"bitmask DataFrame must contain column '{col_name}'")
        s = bitmask_df[col_name].astype(str)
        idx = bitmask_df.index

    # 限制分割次数，避免多余列；转 uint64（缺失填 0）
    parts = s.str.split(split_flag, n=n_groups - 1, expand=True)
    for c in parts.columns:
        parts[c] = pd.to_numeric(parts[c], errors="coerce").fillna(0).astype("uint64")

    # 组装 (N, K) 段数组
    seg_cols = [(parts[i].to_numpy("uint64") if i in parts.columns else np.zeros(len(s), dtype="uint64"))
                for i in range(n_groups)]
    seg_arr = np.vstack(seg_cols).T  # (N, K)

    # 解码 -> flags
    frames = []
    for g in range(n_groups):
        sub_cols = columns[g * _SEG_BITS: (g + 1) * _SEG_BITS]
        if not sub_cols:
            continue
        seg = seg_arr[:, g].astype(np.uint64)
        W = len(sub_cols)
        bits = ((seg[:, None] >> np.arange(W, dtype=np.uint64)) & 1).astype(bool)  # (N, W)
        frames.append(pd.DataFrame(bits, columns=sub_cols, index=idx))
    flags_df = pd.concat(frames, axis=1) if frames else pd.DataFrame(index=idx)

    if df is None:
        return flags_df

    # 掩码
    target = df if inplace else df.copy()
    if not flags_df.index.equals(target.index):
        flags_df = flags_df.reindex(target.index).fillna(False)

    # 逐列向量化赋值
    for col in columns:
        if col in target.columns and col in flags_df.columns:
            m = flags_df[col].to_numpy()
            if m.any():
                target.loc[m, col] = fill
    return target
