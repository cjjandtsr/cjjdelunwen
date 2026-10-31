"""图1中央Environment面板：设计型三维示意（Blender Cycles，非AI生成）。

场景是为说明"局部感知 + 滚动规划"专门设计的示意布局，不对应某个评价任务；
但几何关系由渲染保证正确：点云由相机参数对场景几何射线求交得到（只落在视锥内的可见表面），
被观测/未观测障碍按射线命中自动区分，H4与H8剩余段等弧长，路径与障碍保持间距。

python render_env_schematic.py --style clay --out _preview/env_schematic_clay.png
python render_env_schematic.py --style line --out _preview/env_schematic_line.png
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

# 配色：论文配图总体方案v3 §2.3
P = dict(
    obs=(0.663, 0.702, 0.757),        # #A9B3C1 被观测障碍
    unobs=(0.882, 0.894, 0.914),      # #E1E4E9 未观测障碍
    drone=(0.129, 0.200, 0.329),      # #213354
    rotor=(0.36, 0.40, 0.46),
    frustum=(0.357, 0.553, 0.839),    # #5B8DD6
    traj=(0.102, 0.498, 0.447),       # #1A7F72 深青
    goal=(0.914, 0.702, 0.165),       # #E9B32A 金黄
    goal_edge=(0.62, 0.44, 0.05),
    grid=(0.80, 0.82, 0.85),
    line=(0.33, 0.36, 0.41),
)

# ---------------- 设计场景（单位m，无人机朝+x） ----------------
WALL_H = 2.8
SCENE = [
    dict(name="u_left", shape="box", x=4.425, y=-1.6, z=WALL_H / 2, size_x=2.85, size_y=0.3, size_z=WALL_H, yaw=0.0),
    dict(name="u_right", shape="box", x=4.425, y=1.6, z=WALL_H / 2, size_x=2.85, size_y=0.3, size_z=WALL_H, yaw=0.0),
    dict(name="u_back", shape="box", x=6.0, y=0.0, z=WALL_H / 2, size_x=0.3, size_y=3.5, size_z=WALL_H, yaw=0.0),
    dict(name="c1", shape="cylinder", x=1.0, y=-5.3, z=1.5, radius=0.38, height=3.0),
    dict(name="c2", shape="cylinder", x=5.3, y=4.1, z=1.3, radius=0.34, height=2.6),
    dict(name="c3", shape="cylinder", x=8.6, y=2.4, z=1.6, radius=0.40, height=3.2),
    dict(name="c4", shape="cylinder", x=7.9, y=-3.1, z=1.2, radius=0.30, height=2.4),
    dict(name="c5", shape="cylinder", x=-0.6, y=3.2, z=1.4, radius=0.32, height=2.8),
]
for g in SCENE:
    g.setdefault("radius", 0.0); g.setdefault("height", 0.0)
    g.setdefault("size_x", 0.0); g.setdefault("size_y", 0.0); g.setdefault("size_z", 0.0); g.setdefault("yaw", 0.0)

DRONE = np.array([0.0, 0.0, 1.6])
YAW = 0.0
GOAL = np.array([8.0, 0.0, 1.6])


def planned_path():
    """二次Bezier从U形开口前转向左臂（朝向观察者一侧）外侧，与墙最小水平间距约0.85 m，按等弧长重采样为9点（H8：前4段执行、后4段仅规划）。"""
    p0, c, p2 = DRONE[:2] + [0.3, 0], np.array([1.6, -0.5]), np.array([2.7, -3.2])
    t = np.linspace(0, 1, 400)[:, None]
    xy = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t ** 2 * p2
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]
    pts = np.array([xy[np.searchsorted(s, v)] for v in np.linspace(0, s[-1], 9)])
    z = np.linspace(DRONE[2], DRONE[2] + 0.05, 9)[:, None]
    return np.hstack([pts, z])


def add_grid(mat_cache, half=11, step=1.0, cx=3.5, cy=0.3):
    """地面淡网格：透明度随到场景中心距离衰减，避免出现地板边界。"""
    for k in np.arange(-half, half + 1e-6, step):
        for a, b in (((cx + k, cy - half), (cx + k, cy + half)), ((cx - half, cy + k), (cx + half, cy + k))):
            n = 40
            xs = np.linspace(a[0], b[0], n); ys = np.linspace(a[1], b[1], n)
            for i in range(n - 1):
                mx, my = (xs[i] + xs[i + 1]) / 2, (ys[i] + ys[i + 1]) / 2
                d = math.hypot(mx - cx, my - cy) / half
                alpha = max(0.0, 1 - d) ** 1.8 * 0.30
                if alpha < 0.03:
                    continue
                key = round(alpha, 2)
                if key not in mat_cache:
                    mat_cache[key] = R.mat_glass_tint(f"grid{key}", P["grid"], key)
                o = R.add_tube([(xs[i], ys[i], 0.002), (xs[i + 1], ys[i + 1], 0.002)], 0.004, mat_cache[key], "grid")
                o.visible_shadow = False


def add_drone_nice(pos, yaw, s, coll):
    def link(o):
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
        return o
    body_m = R.mat_principled("d_body", P["drone"], 0.35)
    rotor_m = R.mat_glass_tint("d_rotor", P["rotor"], 0.35)
    ring_m = R.mat_principled("d_ring", P["rotor"], 0.4)
    cam_m = R.mat_principled("d_cam", (0.06, 0.06, 0.07), 0.25)
    pos = Vector(tuple(pos))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=pos, segments=48, ring_count=24)
    b = link(bpy.context.object); b.scale = (0.17 * s, 0.11 * s, 0.05 * s); b.rotation_euler[2] = yaw
    bpy.ops.object.shade_smooth(); b.data.materials.append(body_m)
    arm = 0.22 * s
    for k in range(4):
        a = yaw + math.pi / 4 + k * math.pi / 2
        tip = pos + Vector((math.cos(a) * arm, math.sin(a) * arm, 0.0))
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.014 * s, depth=arm, location=(pos + tip) / 2)
        c = link(bpy.context.object); c.rotation_euler = (0, math.pi / 2, a); c.data.materials.append(body_m)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.10 * s, minor_radius=0.007 * s,
                                         location=tip + Vector((0, 0, 0.025 * s)), major_segments=64, minor_segments=8)
        r = link(bpy.context.object); r.data.materials.append(ring_m)
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.095 * s, depth=0.002 * s,
                                            location=tip + Vector((0, 0, 0.025 * s)))
        d = link(bpy.context.object); d.data.materials.append(rotor_m); d.visible_shadow = False
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.02 * s, depth=0.035 * s,
                                            location=tip + Vector((0, 0, 0.008 * s)))
        m = link(bpy.context.object); m.data.materials.append(body_m)
    nose = pos + Vector((math.cos(yaw), math.sin(yaw), -0.005)) * 0.16 * s
    bpy.ops.mesh.primitive_cube_add(size=1, location=nose)
    cm = link(bpy.context.object); cm.scale = (0.03 * s, 0.07 * s, 0.03 * s); cm.rotation_euler[2] = yaw
    bev = cm.modifiers.new("b", "BEVEL"); bev.width = 0.006 * s; bev.segments = 2
    cm.data.materials.append(cam_m)


def composite(path, shadow, bg_center=0.955):
    """阴影强度缩放后合成到径向渐变底（中心浅灰→四周纯白）。"""
    from PIL import Image
    im = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255
    Image.fromarray((im * 255).astype(np.uint8)).save(str(path).replace(".png", "_rgba.png"))
    h, w = im.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w * 0.52) / (w * 0.62), (yy - h * 0.58) / (h * 0.50))
    bgv = bg_center + (1 - bg_center) * np.clip(r, 0, 1) ** 1.5
    bg = np.repeat(bgv[..., None], 3, -1)
    rgb, al = im[..., :3], im[..., 3:]
    dark = (rgb.max(-1, keepdims=True) < 0.02) & (al < 0.999)
    al = np.where(dark, al * shadow, al)
    out = rgb * al + bg * (1 - al)
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", choices=["clay", "line"], default="clay")
    ap.add_argument("--out", default=str(HERE / "_preview" / "env_schematic.png"))
    ap.add_argument("--res", type=int, default=1600)
    ap.add_argument("--spp", type=int, default=128)
    ap.add_argument("--ortho", type=float, default=12.0)
    ap.add_argument("--view", type=float, nargs=3, default=(-1.0, -0.42, 0.85), help="相机方向（由目标指向相机）")
    ap.add_argument("--target", type=float, nargs=3, default=(3.6, -0.4, 1.3))
    ap.add_argument("--frustum_len", type=float, default=2.6)
    ap.add_argument("--drone_scale", type=float, default=3.0)
    ap.add_argument("--shadow", type=float, default=0.45)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

    meta = dict(geometry=SCENE)
    pts, observed, o, Rm = sd.synth_point_cloud(meta, DRONE, YAW, seed=3)
    plan = planned_path()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.spp
    sc.cycles.use_denoising = True
    sc.render.resolution_x = a.res; sc.render.resolution_y = int(a.res * 0.92)
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
    world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.55

    for loc, energy, size in (((-4, -6, 12), 650, 9), ((10, -8, 8), 220, 12), ((-8, 6, 7), 140, 10)):
        ld = bpy.data.lights.new("area", "AREA"); ld.energy = energy; ld.size = size
        lo = bpy.data.objects.new("area", ld); sc.collection.objects.link(lo); lo.location = loc
        R.look_at(lo, (3.5, 0, 0))

    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    gp = bpy.context.object; gp.is_shadow_catcher = True
    add_grid({})

    obs_coll = bpy.data.collections.new("outlined"); sc.collection.children.link(obs_coll)
    m_obs = R.mat_principled("obs", P["obs"], 0.8)
    m_un = R.mat_principled("unobs", P["unobs"], 0.85)
    for i, g in enumerate(SCENE):
        ob = R.add_box(g, m_obs if i in observed else m_un) if g["shape"] == "box" else R.add_cyl(g, m_obs if i in observed else m_un)
        for c in ob.users_collection:
            c.objects.unlink(ob)
        obs_coll.objects.link(ob)

    gmask = pts[:, 2] < 0.05
    zl = (pts[:, 2].min(), pts[:, 2].max())
    R.add_points(pts[~gmask], 0.022, R.mat_points(), zl)
    gp_pts = pts[gmask][np.random.default_rng(0).random(gmask.sum()) < 0.45]
    R.add_points(gp_pts, 0.013, R.mat_points(), zl)  # 地面点抽稀并缩小，只作示意
    R.add_frustum(o, sd.frustum_corners(o, Rm, a.frustum_len),
                  R.mat_glass_tint("fr", P["frustum"], 0.05), R.mat_principled("fre", P["frustum"], 0.4, alpha=0.8))
    add_drone_nice(DRONE, YAW, a.drone_scale, obs_coll)

    m_tr = R.mat_principled("traj", P["traj"], 0.4, emission=0.25)
    R.add_tube(R.densify(plan[:5], 0.02), 0.055, m_tr, "h4")
    R.add_dashed(plan[4:], 0.045, m_tr, dash=0.16, gap=0.11)
    # 航点（等弧长，k=1..8）：H4执行段为深青实心球，H8剩余段为浅色球
    m_wp = R.mat_principled("wp", P["traj"], 0.35, emission=0.2)
    m_wp8 = R.mat_principled("wp8", (0.93, 0.97, 0.96), 0.35)
    for k, q in enumerate(plan[1:], start=1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075 if k <= 4 else 0.065, location=tuple(q), segments=32, ring_count=16)
        bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(m_wp if k <= 4 else m_wp8)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=tuple(GOAL), segments=48, ring_count=24)
    bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(R.mat_principled("goal", P["goal"], 0.3, emission=0.15))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=tuple(GOAL), segments=48, ring_count=24)
    bpy.ops.object.shade_smooth(); gs = bpy.context.object
    gs.data.materials.append(R.mat_glass_tint("goal_ball", P["goal"], 0.16)); gs.visible_shadow = False

    camd = bpy.data.cameras.new("cam"); camd.type = "ORTHO"; camd.ortho_scale = a.ortho
    cam = bpy.data.objects.new("cam", camd); sc.collection.objects.link(cam); sc.camera = cam
    v = np.array(a.view) / np.linalg.norm(a.view)
    cam.location = tuple(np.array(a.target) + v * 40); R.look_at(cam, a.target)
    camd.clip_end = 200

    if a.style == "line":
        sc.render.use_freestyle = True
        sc.render.line_thickness_mode = "ABSOLUTE"; sc.render.line_thickness = 2.0 * a.res / 1600
        vl = sc.view_layers[0]; vl.use_freestyle = True; fs = vl.freestyle_settings
        ls = fs.linesets[0] if fs.linesets else fs.linesets.new("ls")
        ls.select_by_collection = True; ls.collection = obs_coll
        ls.select_silhouette = True; ls.select_border = True; ls.select_crease = True
        if ls.linestyle is None:
            ls.linestyle = bpy.data.linestyles.new("ls")
        ls.linestyle.color = P["line"]; ls.linestyle.thickness = 1.0; ls.linestyle.alpha = 0.85

    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    composite(str(out), a.shadow)

    bpy.context.view_layer.update()

    def proj(p):
        q = world_to_camera_view(sc, cam, Vector(tuple(float(x) for x in p)))
        return [round(q.x, 4), round(1 - q.y, 4)]
    corners = sd.frustum_corners(o, Rm, a.frustum_len)
    un = [g for i, g in enumerate(SCENE) if i not in observed]
    anchors = dict(drone=proj(DRONE), goal=proj(GOAL), h4_mid=proj(plan[2]), h8_mid=proj(plan[6]),
                   h8_end=proj(plan[-1]), frustum_corner=proj(corners[1]), points_centroid=proj(pts.mean(0)),
                   unobserved=[proj((g["x"], g["y"], g["z"] + (g["size_z"] or g["height"]) / 2)) for g in un])
    out.with_suffix(".anchors.json").write_text(json.dumps(anchors, indent=1))
    print("observed:", [SCENE[i]["name"] for i in observed])
    print("saved", out)


if __name__ == "__main__":
    main()
