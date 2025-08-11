"""
datalab.utils.normalize 数据/字符标准化工具包
 - norm_rule 用于规则检测的规则转换工具
Version 0.1.0
"""
from typing import Iterable, Tuple, List
import re

import re
from typing import Iterable, Tuple, List


def norm_rule(rule_str: str, columns: Iterable[str]) -> Tuple[str, List[str]]:
    if not isinstance(rule_str, str) or not rule_str.strip():
        raise ValueError("rule must be a non-empty string")

    s = rule_str.strip()

    # 比较与逻辑
    s = re.sub(r"<>", "!=", s)
    s = re.sub(r'(?<![!<>=])=(?![=])', '==', s)
    s = re.sub(r"\bAND\b", "&", s, flags=re.IGNORECASE)
    s = re.sub(r"\bOR\b", "|", s, flags=re.IGNORECASE)
    s = re.sub(r"\bNOT\b", "~", s, flags=re.IGNORECASE)

    # IS [NOT] NULL
    s = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+is\s+not\s+null\b", r"\1.notna()", s, flags=re.IGNORECASE)
    s = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+is\s+null\b", r"\1.isna()", s, flags=re.IGNORECASE)

    # [NOT] IN
    s = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+not\s+in\s*\(([^()]*)\)",
               lambda m: f"~{m.group(1)}.isin([{m.group(2)}])", s, flags=re.IGNORECASE)
    s = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+in\s*\(([^()]*)\)",
               lambda m: f"{m.group(1)}.isin([{m.group(2)}])", s, flags=re.IGNORECASE)

    # BETWEEN / NOT BETWEEN
    s = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+between\s+([^ ]+)\s+and\s+([^ )]+)",
               r"(\1 >= \2) & (\1 <= \3)", s, flags=re.IGNORECASE)
    s = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+not\s+between\s+([^ ]+)\s+and\s+([^ )]+)",
               r"(\1 < \2) | (\1 > \3)", s, flags=re.IGNORECASE)

    # 收集并校验列名
    tokens = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", s))
    keywords = {"and", "or", "not", "True", "False", "None", "isna", "notna", "isin"}
    used_cols: List[str] = []
    col_set = set(columns)
    for tok in tokens:
        if tok in keywords:
            continue
        if tok in col_set:
            used_cols.append(tok)

    return s, used_cols
