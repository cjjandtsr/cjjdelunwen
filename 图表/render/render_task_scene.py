"""图4与图形摘要的三维场景渲染：按评价任务的真实几何（task_meta）用 Blender Cycles 渲染。

模式
  --mode scene : 任务全景（图4(a)—(d)、图形摘要）。障碍、起点无人机、目标球（半径0.5 m，即到达判定球）、
                 起点—目标直线（受阻：酒红虚线；未受阻：灰虚线）、地面2 m比例尺；可叠加一回合执行路径 --path。
  --mode cloud : 机体坐标系局部点云（图4(e)），按论文3.6节相机参数对真实几何射线求交得到。

输出：PNG（白底）+ 同名 .anchors.json（起点、目标、比例尺两端等在图像中的归一化坐标，左上为原点），
供 make_figures_v3.py 加矢量文字。

python render_task_scene.py --mode scene --task 30 --out ../v3/render/fig4_b.png
python render_task_scene.py --mode scene --task 30 --path rl_2f3f9914db78_u32 1 --out ../v3/render/ga.png --aspect 1.25
python render_task_scene.py --mode cloud --task 30 --out ../v3/render/fig4_e.png
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scene_data as sd  # noqa: E402
import render_env_panel_blender as R  # noqa: E402

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

# 论文配图总体方案 v3 §2.3
COL = dict(obstacle=(0.663, 0.702, 0.757), drone=(0.129, 0.200, 0.329), rotor=(0.36, 0.40, 0.46),
           goal=(0.914, 0.702, 0.165), blocked=(0.557, 0.173, 0.227), clear=(0.55, 0.58, 0.62),
           path=(0.878, 0.482, 0.224), bar=(0.15, 0.15, 0.15), axis_x=(0.80, 0.20, 0.18),
           axis_y=(0.20, 0.62, 0.30), axis_z=(0.20, 0.40, 0.80))


def load_meta(task):
    d = json.loads(sd.TREND.read_text(encoding="utf-8"))
    meta = next(t for t in d["task_meta"] if t["task_number"] == task)
    return d, meta


def full_path(d, task, policy, repeat):
    case = next(c for c in d["case_cycles"] if c["task_number"] == task and c["policy"] == policy and c["repeat"] == repeat)
    pts = [case["cycles"][0]["pre"]]
    for c in case["cycles"]:
        pts.extend(c["executed_path"][1:])
    return np.array(pts), case["summary"]["outcome"]


def setup_scene(res_x, res_y, spp):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = spp
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res_x, res_y
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
    world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    return sc


def add_lights(sc, center, span):
    for (dx, dy, dz), e, s in (((-0.5, 0.7, 1.2), 1.0, 0.8), ((0.9, -0.8, 0.8), 0.45, 1.0), ((-1.0, -0.4, 0.5), 0.25, 0.9)):
        ld = bpy.data.lights.new("area", "AREA"); ld.energy = e * 9.0 * span ** 2; ld.size = s * span
        lo = bpy.data.objects.new("area", ld); sc.collection.objects.link(lo)
        lo.location = tuple(np.array(center) + np.array([dx, dy, dz]) * span)
        R.look_at(lo, tuple(center))


def ortho_camera(sc, target, azim_deg, elev_deg, pts, aspect, margin=1.06):
    """正交相机：方位角/仰角给定，ortho_scale 自动包住全部关键点。"""
    az, el = math.radians(azim_deg), math.radians(elev_deg)
    v = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])  # 目标→相机
    fwd = -v
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    P = np.asarray(pts, float) - np.asarray(target, float)
    xs, ys = P @ right, P @ up
    cx, cy = (xs.max() + xs.min()) / 2, (ys.max() + ys.min()) / 2
    w, h = xs.max() - xs.min(), ys.max() - ys.min()
    center = np.asarray(target, float) + right * cx + up * cy
    scale = max(w, h * aspect) * margin
    camd = bpy.data.cameras.new("cam"); camd.type = "ORTHO"; camd.ortho_scale = scale; camd.clip_end = 500
    cam = bpy.data.objects.new("cam", camd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = tuple(center + v * 120); R.look_at(cam, tuple(center))
    camd.sensor_fit = "HORIZONTAL" if aspect >= 1 else "VERTICAL"
    if aspect < 1:
        camd.ortho_scale = max(w / aspect, h) * margin
    return cam, right, up, center, v


def geometry_points(meta):
    pts = []
    for g in meta["geometry"]:
        if g["shape"] == "box":
            hx, hy = g["size_x"] / 2, g["size_y"] / 2
            c, s = math.cos(g["yaw"]), math.sin(g["yaw"])
            for sx in (-1, 1):
                for sy in (-1, 1):
                    x = g["x"] + c * sx * hx - s * sy * hy
                    y = g["y"] + s * sx * hx + c * sy * hy
                    pts += [(x, y, g["z"] - g["size_z"] / 2), (x, y, g["z"] + g["size_z"] / 2)]
        else:
            for k in range(8):
                a = k * math.pi / 4
                x, y = g["x"] + g["radius"] * math.cos(a), g["y"] + g["radius"] * math.sin(a)
                pts += [(x, y, g["z"] - g["height"] / 2), (x, y, g["z"] + g["height"] / 2)]
    return pts


def render_and_save(sc, cam, out, anchors, shadow):
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.view_layer.update()

    def proj(p):
        q = world_to_camera_view(sc, cam, Vector(tuple(float(x) for x in p)))
        return [round(q.x, 4), round(1 - q.y, 4)]
    out.with_suffix(".anchors.json").write_text(json.dumps({k: proj(v) for k, v in anchors.items()}, indent=1))
    sc.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    R.composite_white(str(out), shadow)
    print("saved", out)


def scene_mode(a):
    d, meta = load_meta(a.task)
    start, goal = np.array(meta["start"]), np.array(meta["goal"])
    res_y = int(a.res / a.aspect) if a.aspect >= 1 else a.res
    res_x = a.res if a.aspect >= 1 else int(a.res * a.aspect)
    sc = setup_scene(res_x, res_y, a.spp)
    gp_pts = geometry_points(meta) + [tuple(start), tuple(goal), (start[0], start[1], 0), (goal[0], goal[1], 0)]
    path = None
    if a.path:
        path, outcome = full_path(d, a.task, a.path[0], int(a.path[1]))
        gp_pts += [tuple(p) for p in path]
        print("path outcome:", outcome)
    G = np.array(gp_pts)
    center = (G.min(0) + G.max(0)) / 2; center[2] = 0
    u = (goal - start)[:2]; u /= np.linalg.norm(u)
    base_az = math.degrees(math.atan2(u[1], u[0]))
    cam, right, up, ccenter, v = ortho_camera(sc, center, base_az + a.azim, a.elev, G, a.aspect, margin=a.margin)
    span = float(np.ptp(G[:, :2], axis=0).max())
    add_lights(sc, center, span)

    bpy.ops.mesh.primitive_plane_add(size=span * 6, location=(center[0], center[1], 0))
    bpy.context.object.is_shadow_catcher = True
    m_obs = R.mat_principled("obs", COL["obstacle"], 0.8)
    for g in meta["geometry"]:
        R.add_box(g, m_obs) if g["shape"] == "box" else R.add_cyl(g, m_obs)

    yaw = meta["start_yaw"]
    R.add_drone(tuple(start), yaw, a.drone_scale, R.mat_principled("body", COL["drone"], 0.35),
                R.mat_principled("rotor", COL["rotor"], 0.4, alpha=0.6))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=tuple(goal), segments=48, ring_count=24)
    bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(R.mat_principled("goal", COL["goal"], 0.3, emission=0.15))
    lw = max(0.05, span * 0.0045)
    if a.line:
        blocked = bool(meta["line_blocked"])
        R.add_dashed([start, goal], lw, R.mat_principled("line", COL["blocked" if blocked else "clear"], 0.5, emission=0.2),
                     dash=span * 0.018, gap=span * 0.012)
    if path is not None:
        R.add_tube(R.densify(path, 0.05), lw * 1.3, R.mat_principled("path", COL["path"], 0.4, emission=0.25), "path")

    # 2 m 比例尺：放在画面右下角的地面上，方向取相机 right（水平，无透视缩短）
    cam_d = bpy.data.cameras["cam"]
    half_w = cam_d.ortho_scale / 2 if a.aspect >= 1 else cam_d.ortho_scale * a.aspect / 2
    half_h = half_w / a.aspect
    img_pt = ccenter + right * half_w * 0.62 - up * half_h * 0.86
    t = -img_pt[2] / v[2]
    p0 = img_pt + v * t
    p0 = p0 - right * 1.0
    p1 = p0 + right * 2.0
    R.add_tube([p0 + [0, 0, 0.03], p1 + [0, 0, 0.03]], max(0.05, span * 0.004), R.mat_principled("bar", COL["bar"], 0.5), "bar")
    anchors = dict(start=start, goal=goal, bar0=p0, bar1=p1, center=center)
    render_and_save(sc, cam, a.out, anchors, a.shadow)
    print("task", a.task, meta["family"], "blocked", meta["line_blocked"], "obstacles", len(meta["geometry"]))


def cloud_mode(a):
    d, meta = load_meta(a.task)
    start, yaw = np.array(meta["start"]), meta["start_yaw"]
    pts, observed, o, Rm = sd.synth_point_cloud(meta, start, yaw, seed=a.seed)
    # 世界系 → 机体系（原点在机体，x 朝机头，z 向上）
    c, s = math.cos(-yaw), math.sin(-yaw)
    Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    B = (pts - start) @ Rz.T
    sc = setup_scene(int(a.res), int(a.res / a.aspect), a.spp)
    zl = (B[:, 2].min(), B[:, 2].max())
    R.add_points(B, a.point_radius, R.mat_points(), zl)
    L = 1.6
    for axis, colk in ((np.array([L, 0, 0]), "axis_x"), (np.array([0, L, 0]), "axis_y"), (np.array([0, 0, L]), "axis_z")):
        R.add_tube([np.zeros(3), axis], 0.035, R.mat_principled(colk, COL[colk], 0.4, emission=0.3), colk)
    R.add_drone((0, 0, 0), 0.0, 1.6, R.mat_principled("body", COL["drone"], 0.35),
                R.mat_principled("rotor", COL["rotor"], 0.4, alpha=0.6))
    span = float(np.ptp(B[:, :2], axis=0).max())
    allp = np.vstack([B, np.zeros((1, 3))])
    center = (allp.min(0) + allp.max(0)) / 2
    cam, right, up, ccenter, v = ortho_camera(sc, center, 180 + a.azim, a.elev, allp, a.aspect, margin=1.04)
    add_lights(sc, center, span)
    bpy.ops.mesh.primitive_plane_add(size=span * 6, location=(center[0], center[1], B[:, 2].min() - 0.02))
    bpy.context.object.is_shadow_catcher = True
    anchors = dict(x_tip=[L * 1.1, 0, 0], y_tip=[0, L * 1.1, 0], z_tip=[0, 0, L * 1.1], origin=[0, 0, 0])
    render_and_save(sc, cam, a.out, anchors, a.shadow)
    print("cloud points", len(B), "observed obstacles", len(observed))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["scene", "cloud"], default="scene")
    ap.add_argument("--task", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--path", nargs=2, metavar=("POLICY", "REPEAT"), help="叠加该回合执行路径（需在 case_cycles 中）")
    ap.add_argument("--no-line", dest="line", action="store_false", help="不画起点—目标直线")
    ap.add_argument("--res", type=int, default=1000, help="长边像素")
    ap.add_argument("--aspect", type=float, default=0.85, help="宽/高")
    ap.add_argument("--spp", type=int, default=64)
    ap.add_argument("--elev", type=float, default=55.0, help="相机仰角（度）")
    ap.add_argument("--azim", type=float, default=-115.0, help="相机方位角，相对起点→目标方向（度）")
    ap.add_argument("--drone_scale", type=float, default=5.0)
    ap.add_argument("--point_radius", type=float, default=0.035)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--margin", type=float, default=1.18, help="取景留白系数（包住无人机模型）")
    ap.add_argument("--shadow", type=float, default=0.45)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    if a.mode == "cloud":
        if a.elev == 55.0:
            a.elev = 30.0
        if a.azim == -115.0:
            a.azim = 35.0
        cloud_mode(a)
    else:
        scene_mode(a)


if __name__ == "__main__":
    main()
