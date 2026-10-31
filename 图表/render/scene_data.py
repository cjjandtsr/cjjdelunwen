"""从原始评价数据准备三维场景渲染所需的几何、轨迹与合成点云。

数据来源：2026-10-15_v3_全策略原轨迹分析/2026-10-15_v3_fresh趋势数据.json
  - task_meta[*].geometry：障碍真实几何（box/cylinder），start/goal/start_yaw
  - case_cycles[*].cycles[k]：该周期真实执行路径 executed_path（H4）与规划路径 planned_policy_path（H8）

点云：按论文3.6节相机参数（320x240、HFOV 60°、0.05—10 m、机头前0.12 m、下俯8°、
0.5%乘性深度噪声、5%点缺失、随机抽4096点）对真实几何做射线求交复现。
定稿时建议改用仿真器在该周期导出的真实观测点云（见配图方案文档），本函数结构不变。
"""
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TREND = ROOT / "2026-10-15_v3_全策略原轨迹分析" / "2026-10-15_v3_fresh趋势数据.json"

CAM = dict(w=320, h=240, hfov_deg=60.0, near=0.05, far=10.0, offset=0.12,
           pitch_down_deg=8.0, noise=0.005, dropout=0.05, n_points=4096)


def load_case(task_number, policy, repeat, cycle):
    d = json.loads(TREND.read_text(encoding="utf-8"))
    meta = next(t for t in d["task_meta"] if t["task_number"] == task_number)
    case = next(c for c in d["case_cycles"] if c["task_number"] == task_number
                and c["policy"] == policy and c["repeat"] == repeat)
    cyc = case["cycles"][cycle]
    full_path = [case["cycles"][0]["pre"]]
    for c in case["cycles"]:
        full_path.extend(c["executed_path"][1:])
    return meta, cyc, case["summary"]["outcome"], full_path


def heading(meta, cyc, cycle):
    if cycle == 0:
        return meta["start_yaw"]
    p = np.array(cyc["planned_policy_path"])
    v = p[min(4, len(p) - 1)] - p[0]
    return math.atan2(v[1], v[0])


def _rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def _rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def camera_rays(pos, yaw):
    w, h = CAM["w"], CAM["h"]
    f = (w / 2) / math.tan(math.radians(CAM["hfov_deg"]) / 2)
    u, v = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    d_cam = np.stack([np.ones_like(u), -(u - w / 2) / f, -(v - h / 2) / f], -1).reshape(-1, 3)
    d_cam /= np.linalg.norm(d_cam, axis=1, keepdims=True)
    R = _rot_z(yaw) @ _rot_y(math.radians(CAM["pitch_down_deg"]))
    origin = np.asarray(pos, float) + _rot_z(yaw) @ np.array([CAM["offset"], 0, 0])
    return origin, d_cam @ R.T, R


def _hit_box(o, d, g):
    a = -g["yaw"]
    Rl = _rot_z(a)
    oc = Rl @ (o - np.array([g["x"], g["y"], g["z"]]))
    dl = d @ Rl.T
    half = np.array([g["size_x"], g["size_y"], g["size_z"]]) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = (-half - oc) / dl
        t2 = (half - oc) / dl
    tmin = np.nanmax(np.minimum(t1, t2), axis=1)
    tmax = np.nanmin(np.maximum(t1, t2), axis=1)
    ok = (tmax >= tmin) & (tmax > 0)
    t = np.where(tmin > 0, tmin, tmax)
    return np.where(ok, t, np.inf)


def _hit_cyl(o, d, g):
    cx, cy, r = g["x"], g["y"], g["radius"]
    z0, z1 = g["z"] - g["height"] / 2, g["z"] + g["height"] / 2
    ox, oy = o[0] - cx, o[1] - cy
    a = d[:, 0] ** 2 + d[:, 1] ** 2
    b = 2 * (ox * d[:, 0] + oy * d[:, 1])
    c = ox ** 2 + oy ** 2 - r ** 2
    disc = b ** 2 - 4 * a * c
    t = np.full(len(d), np.inf)
    with np.errstate(invalid="ignore", divide="ignore"):
        sq = np.sqrt(np.maximum(disc, 0))
        for tt in ((-b - sq) / (2 * a), (-b + sq) / (2 * a)):
            z = o[2] + tt * d[:, 2]
            ok = (disc >= 0) & (tt > 0) & (z >= z0) & (z <= z1)
            t = np.where(ok & (tt < t), tt, t)
        tc = (z1 - o[2]) / d[:, 2]
        px, py = ox + tc * d[:, 0], oy + tc * d[:, 1]
        ok = (tc > 0) & (px ** 2 + py ** 2 <= r ** 2)
        t = np.where(ok & (tc < t), tc, t)
    return t


def synth_point_cloud(meta, pos, yaw, seed=0):
    o, d, R = camera_rays(pos, yaw)
    best = np.full(len(d), np.inf)
    hit_id = np.full(len(d), -1)
    with np.errstate(divide="ignore", invalid="ignore"):
        tg = np.where(d[:, 2] < 0, -o[2] / d[:, 2], np.inf)
    best = np.minimum(best, tg)
    for i, g in enumerate(meta["geometry"]):
        t = _hit_box(o, d, g) if g["shape"] == "box" else _hit_cyl(o, d, g)
        closer = t < best
        best = np.where(closer, t, best)
        hit_id = np.where(closer, i, hit_id)
    valid = (best >= CAM["near"]) & (best <= CAM["far"])
    rng = np.random.default_rng(seed)
    valid &= rng.random(len(d)) > CAM["dropout"]
    depth = best * (1 + CAM["noise"] * rng.standard_normal(len(d)))
    idx = np.flatnonzero(valid)
    pick = rng.choice(idx, size=min(CAM["n_points"], len(idx)), replace=False)
    pts = o + d[pick] * depth[pick, None]
    observed = sorted(set(int(i) for i in hit_id[idx] if i >= 0))
    return pts, observed, o, R


def frustum_corners(o, R, length):
    w, h = CAM["w"], CAM["h"]
    f = (w / 2) / math.tan(math.radians(CAM["hfov_deg"]) / 2)
    cs = []
    for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        dc = np.array([1.0, -su * (w / 2) / f, -sv * (h / 2) / f])
        cs.append(o + R @ dc * length)
    return np.array(cs)
