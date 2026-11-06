"""论文数据图的数据读取、分组与区间估计（make_figures_v3.py 使用）。

已有数据（仓库内）：
  REC    v3全策略原轨迹分析数据.json  —— 原任务84×5回合逐回合记录（BC、后训练等14组）
  TREND  v3 fresh趋势数据.json        —— task_meta 几何、case_cycles 205个案例回合的逐周期路径
  P3     图表/P3_data_tables.md        —— 新任务24项逐任务结局计数；中间状态24项
  P2     图表/P2_results.json          —— 配对终点矩阵
  CURVE  fresh203_training_curve_384.csv —— 训练曲线
  B1     图表/data/b1_lora_scale.json  —— LoRA缩放评价

待回传数据（放到 图表/data/ 后自动启用，格式见 图表/data/待回传数据格式说明.md）：
  EGO    b3_ego_records.json           —— EGO-Planner逐回合记录（图5、图6、表4/5）
  P3S    p3_first_step_by_state.json   —— 24个中间状态逐状态首段推进（图8(a)）
  PATHS  v3_executed_paths.json        —— 全部回合执行路径（占据密度图）
"""
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "图表" / "data"
REC = ROOT / "2026-10-15_v3_全策略原轨迹分析" / "2026-10-15_v3_全策略原轨迹分析数据.json"
TREND = ROOT / "2026-10-15_v3_全策略原轨迹分析" / "2026-10-15_v3_fresh趋势数据.json"
CURVE = ROOT / "2026-10-15_v3_全策略原轨迹分析" / "fresh203_training_curve_384.csv"
P2 = ROOT / "图表" / "P2_results.json"
P3 = ROOT / "图表" / "P3_data_tables.md"
B1 = DATA / "b1_lora_scale.json"
EGO = DATA / "b3_ego_records.json"
P3S = DATA / "p3_first_step_by_state.json"
PATHS = DATA / "v3_executed_paths.json"

BC, RL, EG = "bc", "rl_2f3f9914db78_u32", "ego"
DENSE = ["cul_de_sac_trap", "bottleneck_corridor", "s_turn_multi_obstacle"]
FAM_EN = {"cul_de_sac_trap": "U-trap", "bottleneck_corridor": "Bottleneck", "s_turn_multi_obstacle": "S-turn"}
OUTCOMES = ["reached", "collision", "time_limit"]

# 中间状态汇总值（研究报告/2026-10-21_论文P3与有限任务评价独立验收数据.json 及验收报告；论文4.4节）
SAME_STATE = dict(mean_progress={"bc": 0.355, "rl": 0.593},
                  positive={"bc": (851, 1200), "rl": (1000, 1200)},
                  rl_cont={"positive": (36, 12, 52), "non_positive": (5, 0, 15)})

_cache = {}


def _json(p):
    if p not in _cache:
        _cache[p] = json.loads(Path(p).read_text(encoding="utf-8"))
    return _cache[p]


def available():
    return {"EGO": EGO.exists(), "P3S": P3S.exists(), "PATHS": PATHS.exists()}


# ---------------- 原任务逐回合记录 ----------------
def records(policies=(BC, RL)):
    R = [r for r in _json(REC)["records"] if r["policy"] in policies]
    if EG in policies and EGO.exists():
        R += [dict(r, policy=EG) for r in ego_records(set_="original")]
    return R


def ego_records(set_=None):
    """EGO 记录：字段与 v3 records 一致；用 world 中的 __rl_train__/__rl_test__ 区分原任务/新任务。"""
    if not EGO.exists():
        return []
    d = _json(EGO)
    R = d["records"] if isinstance(d, dict) else d
    out = []
    for r in R:
        s = r.get("task_set") or ("new" if "__rl_test__" in r.get("world", r.get("task_id", "")) else "original")
        if set_ is None or s == set_:
            out.append(dict(r, task_set=s))
    return out


def original_group_keys(r):
    dense = r["family"] in DENSE
    keys = ["all"]
    if dense:
        keys += ["dense", "dense_blocked" if r["blocked"] else "dense_unblocked"]
        if r["family"] == "cul_de_sac_trap" and r["blocked"]:
            keys.append("utrap_blocked")
    else:
        keys.append("low_density")
    return keys


def original_groups(R):
    g = defaultdict(lambda: defaultdict(list))
    for r in R:
        for k in original_group_keys(r):
            g[k][r["policy"]].append(r)
    return g


# ---------------- 新任务（逐任务计数） ----------------
def new_tasks():
    """返回24项：dict(n, world, blocked, dense, family, counts={'bc':[a,c,t],'rl':[...],'ego':[...]?})。"""
    t = P3.read_text(encoding="utf-8")
    rows = re.findall(r"\| (\d+) \| (\w+) \| (\S+) \| (True|False) \| (True|False) \| (\d)/(\d)/(\d) \| (\d)/(\d)/(\d) \|", t)
    assert len(rows) == 24, len(rows)
    out = []
    ego = defaultdict(lambda: [0, 0, 0])
    for r in ego_records(set_="new"):
        key = str(r["new_task_index"]) if "new_task_index" in r else r["task_id"]
        ego[key][OUTCOMES.index(r["outcome"])] += 1
    for r in rows:
        world = r[2]
        fam = next((f for f in DENSE if f in world), world.split("__")[-2] if "__" in world else world)
        item = dict(n=int(r[0]), task_id=r[1], world=world, blocked=r[3] == "True", family=fam,
                    dense=fam in DENSE, counts={"bc": [int(x) for x in r[5:8]], "rl": [int(x) for x in r[8:11]]})
        for key in (r[1], r[0]):
            if key in ego:
                item["counts"]["ego"] = ego[key]
        out.append(item)
    return out


def new_group_keys(t):
    keys = ["all"]
    if t["dense"]:
        keys += ["dense", "dense_blocked" if t["blocked"] else "dense_unblocked"]
    else:
        keys.append("low_density")
    return keys


# ---------------- 统计 ----------------
def rate(xs, outcome="reached"):
    return 100.0 * sum(x["outcome"] == outcome for x in xs) / len(xs) if xs else float("nan")


def cluster_bootstrap(per_task, n_boot=4000, seed=20261031):
    """以任务为重采样单位的bootstrap 95%区间。per_task: [(成功数, 回合数), ...]。返回 (lo, hi)，单位%。"""
    a = np.asarray(per_task, float)
    if len(a) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    s = a[idx, 0].sum(1) / a[idx, 1].sum(1) * 100
    return float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def per_task_counts(xs, outcome="reached"):
    d = defaultdict(lambda: [0, 0])
    for x in xs:
        d[x["task"]][0] += x["outcome"] == outcome
        d[x["task"]][1] += 1
    return list(d.values())


# ---------------- 其他数据 ----------------
def task_meta(task):
    return next(t for t in _json(TREND)["task_meta"] if t["task_number"] == task)


def case(task, policy, repeat):
    return next(c for c in _json(TREND)["case_cycles"]
                if c["task_number"] == task and c["policy"] == policy and c["repeat"] == repeat)


def case_paths():
    """205 个案例回合（预览用）：[(policy, task, repeat, path ndarray)]。"""
    out = []
    for c in _json(TREND)["case_cycles"]:
        pts = [c["cycles"][0]["pre"]]
        for cy in c["cycles"]:
            pts.extend(cy["executed_path"][1:])
        out.append((c["policy"], c["task_number"], c["repeat"], np.array(pts)))
    return out


def all_paths():
    """全部回合执行路径（待回传）。返回与 case_paths 相同格式。"""
    d = _json(PATHS)
    return [(p["policy"], p["task"], p["repeat"], np.array(p["path"])) for p in d["paths"]]


def training_curve():
    rows = list(csv.DictReader(CURVE.open(encoding="utf-8")))
    keys = ["reached", "collision", "time_limit", "collection_boundary", "altitude_exceed", "ground_crash", "out_of_bounds"]
    u = np.array([int(r["update"]) for r in rows])
    tot = np.array([sum(int(r["done_reason_" + k] or 0) for k in keys) for r in rows], float)
    arr = np.array([int(r["done_reason_reached"] or 0) for r in rows], float)
    col = np.array([int(r["done_reason_collision"] or 0) for r in rows], float)
    ret = np.array([float(r["return_mean"]) if r["return_mean"] else math.nan for r in rows])
    return u, tot, arr, col, ret


def paired_matrix():
    M = _json(P2)["paired_terminal_matrix"]
    assert M["rows_bc"] == M["columns_rl"] == OUTCOMES
    return np.array(M["counts"])


def lora_scale():
    return _json(B1)


def first_step_by_state():
    """待回传：[{state, bc_mean_progress_m, rl_mean_progress_m, bc_positive, rl_positive, n_samples}]。校验与汇总值一致。"""
    d = _json(P3S)
    S = d["states"]
    assert len(S) == 24, f"应为24个状态，实际{len(S)}"
    n = sum(s["n_samples"] for s in S)
    for p, key in (("bc", "bc"), ("rl", "rl")):
        m = sum(s[f"{key}_mean_progress_m"] * s["n_samples"] for s in S) / n
        pos = sum(s[f"{key}_positive"] for s in S)
        exp_m, (exp_pos, exp_n) = SAME_STATE["mean_progress"][p], SAME_STATE["positive"][p]
        if abs(m - exp_m) > 0.0015 or pos != exp_pos or n != exp_n:
            print(f"[警告] 逐状态数据与验收汇总不一致：{p} 均值 {m:.3f}/{exp_m}，正推进 {pos}/{exp_pos}，样本 {n}/{exp_n}")
    return S
