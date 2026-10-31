"""图1中央Environment面板：基于真实任务几何的三维渲染原型（Blender Cycles，无需GUI）。

运行（Blender 4.2 Python模块或 blender -b -P）：
  python render_env_panel_blender.py --task 30 --policy rl_2f3f9914db78_u32 --repeat 1 --cycle 0 \
         --out ../v2/env_panel_t30.png --res 1600 --spp 96

元素与论文对应：
  障碍几何、起点/目标、本周期H4执行段与H8规划段 —— 原始评价记录（真实数据）
  点云 —— 按论文相机参数对真实几何射线求交（定稿可换仿真器导出的真实观测）
  视锥 —— 60°×46.8°针孔视场，长度仅为示意
  无人机模型 —— 简化几何体，非实机外形
"""
import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scene_data as sd  # noqa: E402

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

# ---------------- 配色（与全文统一，见配图方案文档§2） ----------------
C = dict(
    obstacle=(0.66, 0.70, 0.77),       # #B8BFCC 哑光浅灰（被观测）
    obstacle_faded=(0.88, 0.89, 0.91),  # 未被观测：更浅、不透明
    ground=(0.94, 0.94, 0.935),
    grid=(0.91, 0.91, 0.91),
    drone=(0.13, 0.20, 0.33),          # 深海军蓝 #213354
    rotor=(0.25, 0.30, 0.38),
    frustum=(0.45, 0.62, 0.86),        # #739ED9
    exec_=(0.0, 0.62, 0.45),           # Okabe-Ito 蓝绿 #009E73
    plan=(0.0, 0.45, 0.70),            # Okabe-Ito 蓝 #0072B2
    goal=(0.90, 0.38, 0.0),            # Okabe-Ito 朱橙 #E69F00/#D55E00之间
    route=(0.55, 0.55, 0.55),
)


def srgb_to_lin(c):
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def mat_principled(name, rgb, rough=0.6, alpha=1.0, emission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    lin = srgb_to_lin(rgb) + (1.0,)
    b.inputs["Base Color"].default_value = lin
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    if emission > 0:
        b.inputs["Emission Color"].default_value = lin
        b.inputs["Emission Strength"].default_value = emission
    if alpha < 1:
        m.blend_method = "BLEND"
    return m


def mat_glass_tint(name, rgb, strength=0.15):
    """无噪声半透明着色：透明BSDF与自发光混合，不受光照采样噪声影响。"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = srgb_to_lin(rgb) + (1,)
    em.inputs[1].default_value = 1.0
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = strength
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs[0])
    m.blend_method = "BLEND"
    return m


def mat_ground():
    m = bpy.data.materials.new("ground")
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.9
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Object"], sep.inputs[0])

    def line(axis):
        fr = nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
        links.new(sep.outputs[axis], fr.inputs[0])
        sub = nodes.new("ShaderNodeMath"); sub.operation = "PINGPONG"; sub.inputs[1].default_value = 0.5
        links.new(fr.outputs[0], sub.inputs[0])
        lt = nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.008
        links.new(sub.outputs[0], lt.inputs[0])
        return lt
    mx = nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    links.new(line(0).outputs[0], mx.inputs[0]); links.new(line(1).outputs[0], mx.inputs[1])
    mix = nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs[6].default_value = srgb_to_lin(C["ground"]) + (1,)
    mix.inputs[7].default_value = srgb_to_lin(C["grid"]) + (1,)
    links.new(mx.outputs[0], mix.inputs[0])
    links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    return m


def mat_points():
    """按高度着色：viridis 0.15—0.85 段（感知均匀、色盲友好）。"""
    m = bpy.data.materials.new("points")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.5
    attr = nt.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "col"
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.25
    return m


VIRIDIS = np.array([[0.267, 0.005, 0.329], [0.283, 0.141, 0.458], [0.254, 0.265, 0.530],
                    [0.207, 0.372, 0.553], [0.164, 0.471, 0.558], [0.128, 0.567, 0.551],
                    [0.135, 0.659, 0.518], [0.267, 0.749, 0.441], [0.478, 0.821, 0.318],
                    [0.741, 0.873, 0.150], [0.993, 0.906, 0.144]])


def viridis(t):
    t = np.clip(t, 0, 1) * (len(VIRIDIS) - 1)
    i = np.minimum(t.astype(int), len(VIRIDIS) - 2)
    f = (t - i)[:, None]
    return VIRIDIS[i] * (1 - f) + VIRIDIS[i + 1] * f


def add_box(g, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(g["x"], g["y"], g["z"]))
    o = bpy.context.object
    o.scale = (g["size_x"], g["size_y"], g["size_z"])
    o.rotation_euler[2] = g["yaw"]
    bev = o.modifiers.new("bevel", "BEVEL"); bev.width = 0.02; bev.segments = 2
    o.data.materials.append(mat)
    return o


def add_cyl(g, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=g["radius"], depth=g["height"],
                                        location=(g["x"], g["y"], g["z"]))
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def add_tube(points, radius, mat, name):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"; cu.bevel_depth = radius; cu.bevel_resolution = 6; cu.use_fill_caps = True
    sp = cu.splines.new("POLY"); sp.points.add(len(points) - 1)
    for p, q in zip(sp.points, points):
        p.co = (q[0], q[1], q[2], 1)
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def densify(pts, step):
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.linalg.norm(b - a) / step))
        for k in range(1, n + 1):
            out.append(a + (b - a) * k / n)
    return np.array(out)


def add_dashed(points, radius, mat, dash=0.10, gap=0.07):
    pts = densify(np.asarray(points, float), 0.01)
    seg, acc, on, cur = [], 0.0, True, [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        acc += np.linalg.norm(b - a); cur.append(b)
        if on and acc >= dash:
            seg.append(cur); cur, acc, on = [b], 0.0, False
        elif not on and acc >= gap:
            cur, acc, on = [b], 0.0, True
    if on and len(cur) > 1:
        seg.append(cur)
    for i, s in enumerate(seg):
        add_tube(s, radius, mat, f"dash{i}")


def add_points(pts, radius, mat, zlim=None):
    me = bpy.data.meshes.new("pc"); me.from_pydata([tuple(p) for p in pts], [], [])
    z = pts[:, 2]
    lo, hi = zlim if zlim else (z.min(), z.max())
    col = viridis(0.15 + 0.70 * np.clip((z - lo) / max(1e-6, hi - lo), 0, 1))
    attr = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
    for i, c in enumerate(col):
        attr.data[i].color = tuple(srgb_to_lin(c)) + (1,)
    o = bpy.data.objects.new("pc", me); bpy.context.collection.objects.link(o)
    mod = o.modifiers.new("gn", "NODES")
    ng = bpy.data.node_groups.new("m2p", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi = ng.nodes.new("NodeGroupInput"); go = ng.nodes.new("NodeGroupOutput")
    m2p = ng.nodes.new("GeometryNodeMeshToPoints"); m2p.inputs["Radius"].default_value = radius
    sm = ng.nodes.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = mat
    ng.links.new(gi.outputs[0], m2p.inputs["Mesh"]); ng.links.new(m2p.outputs[0], sm.inputs[0])
    ng.links.new(sm.outputs[0], go.inputs[0])
    mod.node_group = ng
    return o


def add_frustum(o, corners, mat_face, mat_edge):
    verts = [tuple(o)] + [tuple(c) for c in corners]
    faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 2, 3, 4)]
    me = bpy.data.meshes.new("frustum"); me.from_pydata(verts, [], faces)
    ob = bpy.data.objects.new("frustum", me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat_face)
    ob.visible_shadow = False
    for c in corners:
        e = add_tube([o, c], 0.008, mat_edge, "fedge"); e.visible_shadow = False
    ring = list(corners) + [corners[0]]
    e = add_tube(ring, 0.008, mat_edge, "fring"); e.visible_shadow = False


def add_drone(pos, yaw, scale, mat_body, mat_rotor):
    parts = []
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    b = bpy.context.object; b.scale = (0.22 * scale, 0.14 * scale, 0.07 * scale)
    bev = b.modifiers.new("bevel", "BEVEL"); bev.width = 0.02 * scale; bev.segments = 3
    b.data.materials.append(mat_body); parts.append(b)
    arm = 0.19 * scale
    for k in range(4):
        a = yaw + math.pi / 4 + k * math.pi / 2
        tip = Vector(pos) + Vector((math.cos(a) * arm, math.sin(a) * arm, 0.01 * scale))
        mid = (Vector(pos) + tip) / 2
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.012 * scale, depth=arm, location=mid)
        c = bpy.context.object; c.rotation_euler = (0, math.pi / 2, a)
        c.data.materials.append(mat_body); parts.append(c)
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.085 * scale, depth=0.006 * scale,
                                            location=tip + Vector((0, 0, 0.03 * scale)))
        r = bpy.context.object; r.data.materials.append(mat_rotor); parts.append(r)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.018 * scale, depth=0.04 * scale,
                                            location=tip + Vector((0, 0, 0.012 * scale)))
        mtr = bpy.context.object; mtr.data.materials.append(mat_body); parts.append(mtr)
    nose = Vector(pos) + Vector((math.cos(yaw), math.sin(yaw), 0)) * 0.12 * scale
    bpy.ops.mesh.primitive_cube_add(size=1, location=nose)
    cam = bpy.context.object; cam.scale = (0.04 * scale, 0.09 * scale, 0.035 * scale)
    cam.rotation_euler[2] = yaw
    cam.data.materials.append(mat_principled("camblack", (0.05, 0.05, 0.06), 0.3)); parts.append(cam)
    b.rotation_euler[2] = yaw
    return parts


def composite_white(path, shadow=0.6):
    """保留RGBA原图，阴影强度按 shadow 系数减弱后合成到纯白背景。"""
    from PIL import Image
    im = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255
    Image.fromarray((im * 255).astype(np.uint8)).save(str(path).replace(".png", "_rgba.png"))
    rgb, al = im[..., :3], im[..., 3:]
    dark = (rgb.max(-1, keepdims=True) < 0.02) & (al < 0.999)
    al = np.where(dark, al * shadow, al)
    out = rgb * al + (1 - al)
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(path)


def look_at(cam_obj, target):
    d = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", type=int, default=30)
    ap.add_argument("--policy", default="rl_2f3f9914db78_u32")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--cycle", type=int, default=0)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "_preview" / "env_panel.png"))
    ap.add_argument("--res", type=int, default=1400)
    ap.add_argument("--spp", type=int, default=64)
    ap.add_argument("--frustum_len", type=float, default=5.8)
    ap.add_argument("--drone_scale", type=float, default=1.8)
    ap.add_argument("--show_route", action="store_true", help="以浅灰细线显示该回合完整执行路线")
    ap.add_argument("--cam", type=float, nargs=6, default=None, help="相机位置xyz与注视点xyz")
    ap.add_argument("--lens", type=float, default=50)
    ap.add_argument("--faded_alpha", type=float, default=1.0)
    ap.add_argument("--white", action="store_true", help="地面为阴影捕捉器，合成到纯白背景")
    ap.add_argument("--view", default="Standard")
    ap.add_argument("--shadow", type=float, default=0.55, help="阴影强度系数（0—1）")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

    meta, cyc, outcome, full = sd.load_case(a.task, a.policy, a.repeat, a.cycle)
    pos = np.array(cyc["pre"]); yaw = sd.heading(meta, cyc, a.cycle)
    pts, observed, o, R = sd.synth_point_cloud(meta, pos, yaw)
    plan = np.array(cyc["planned_policy_path"])

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.spp
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = a.res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = a.view
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"

    world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.0

    # 柔和主光 + 补光（棚拍风格，阴影柔和）
    for loc, energy, size in (((-6, 8, 14), 900, 10), ((10, -10, 9), 450, 12), ((-12, -6, 6), 250, 10)):
        ld = bpy.data.lights.new("area", "AREA"); ld.energy = energy; ld.size = size
        lo = bpy.data.objects.new("area", ld); sc.collection.objects.link(lo)
        lo.location = loc; look_at(lo, (2, -2, 0))

    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    gp = bpy.context.object
    gp.data.materials.append(mat_ground())
    if a.white:
        gp.is_shadow_catcher = True
        sc.render.film_transparent = True

    m_obs = mat_principled("obs", C["obstacle"], 0.75)
    m_fad = mat_principled("obs_faded", C["obstacle_faded"], 0.85, alpha=a.faded_alpha)
    for i, g in enumerate(meta["geometry"]):
        m = m_obs if i in observed else m_fad
        ob = add_box(g, m) if g["shape"] == "box" else add_cyl(g, m)

    add_points(pts, 0.028, mat_points())
    add_frustum(o, sd.frustum_corners(o, R, a.frustum_len),
                mat_glass_tint("fr", C["frustum"], 0.10),
                mat_principled("fre", C["frustum"], 0.4, alpha=0.8))
    add_drone(tuple(pos), yaw, a.drone_scale, mat_principled("body", C["drone"], 0.35),
              mat_principled("rotor", C["rotor"], 0.4, alpha=0.55))

    add_tube(densify(plan[:5], 0.02), 0.045, mat_principled("exec", C["exec_"], 0.4, emission=0.3), "h4")
    add_dashed(plan[4:], 0.04, mat_principled("plan", C["plan"], 0.4, emission=0.3))
    if a.show_route:
        add_tube(densify(np.array(full), 0.05)[::2], 0.012, mat_principled("route", C["route"], 0.6, alpha=0.6), "route")

    gpos = meta["goal"]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=gpos, segments=48, ring_count=24)
    bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(mat_principled("goal", C["goal"], 0.25, emission=0.2))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=gpos, segments=48, ring_count=24)
    bpy.ops.object.shade_smooth(); gs = bpy.context.object
    gs.data.materials.append(mat_glass_tint("goalball", C["goal"], 0.18)); gs.visible_shadow = False

    camd = bpy.data.cameras.new("cam"); camd.lens = a.lens
    cam = bpy.data.objects.new("cam", camd); sc.collection.objects.link(cam); sc.camera = cam
    if a.cam:
        cam.location = a.cam[:3]; look_at(cam, a.cam[3:])
    else:
        back = np.array([-math.cos(yaw), -math.sin(yaw), 0])
        side = np.array([math.sin(yaw), -math.cos(yaw), 0])
        cam.location = tuple(pos + back * 6.5 + side * 2.5 + np.array([0, 0, 5.0]))
        look_at(cam, tuple(pos + np.array([math.cos(yaw), math.sin(yaw), 0]) * 3.0 + np.array([0, 0, -1.2])))

    # 导出标注锚点（图像归一化坐标，左上为原点），供后期加文字与引线
    from bpy_extras.object_utils import world_to_camera_view
    import json as _json
    bpy.context.view_layer.update()
    def proj(p):
        v = world_to_camera_view(sc, cam, Vector(tuple(float(x) for x in p)))
        return [round(v.x, 4), round(1 - v.y, 4)]
    corners = sd.frustum_corners(o, R, a.frustum_len)
    unobs = [g for i, g in enumerate(meta["geometry"]) if i not in observed]
    anchors = dict(drone=proj(pos), goal=proj(gpos), h4_mid=proj(plan[2]), h8_mid=proj(plan[6]),
                   h8_end=proj(plan[-1]), frustum_corner=proj(corners[1]),
                   points_centroid=proj(pts.mean(0)),
                   unobserved=[proj((g["x"], g["y"], g["z"] + (g["size_z"] or g["height"]) / 2)) for g in unobs])
    Path(a.out).with_suffix(".anchors.json").write_text(_json.dumps(anchors, indent=1))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = a.out
    bpy.ops.render.render(write_still=True)
    if a.white:
        composite_white(a.out, a.shadow)
    print("observed:", [meta["geometry"][i]["name"] for i in observed], "outcome:", outcome)
    print("saved", a.out)


if __name__ == "__main__":
    main()
