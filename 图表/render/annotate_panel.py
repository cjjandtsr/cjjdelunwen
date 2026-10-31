"""在渲染图上按锚点添加英文矢量标注，按成品宽度输出PDF+PNG（检查印刷字号与版面）。

python annotate_panel.py _preview/env_schematic_line.png --layout schematic --width_mm 62 \
       --crop 0 0.02 1 0.86 --out _preview/env_schematic_line_annotated
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

import glob  # noqa: E402
import os  # noqa: E402
from matplotlib import font_manager  # noqa: E402

# Arial 不在沙箱里时，用字宽与之一致的 Liberation Sans（目录可用 PAPER_FONT_DIR 指定）
for f in glob.glob(os.path.join(os.environ.get("PAPER_FONT_DIR", "/projects/sandbox/work/fonts"), "**", "*.ttf"), recursive=True):
    font_manager.fontManager.addfont(f)
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans", "DejaVu Sans"], "pdf.fonttype": 42})

# 配色与 论文配图总体方案v3 §2.3 一致
INK = dict(goal="#8A6410", fov="#3D66A8", pc="#2F5E57", traj="#1A7F72", grey="#6B6B6B")

# 每项：(锚点键, 文字, 文字位置[归一化x,y]或相对偏移, 颜色, 对齐)
LAYOUTS = {
    "real": [
        ("goal", "Goal", ("rel", -0.14, -0.10), INK["goal"], "left"),
        ("frustum_corner", "Camera FOV\n60°×47°", ("rel", -0.02, 0.16), INK["fov"], "left"),
        ("points_centroid", "Local point cloud", ("rel", -0.36, -0.30), INK["pc"], "left"),
        ("h4_mid", "H4 executed", ("rel", -0.24, 0.12), INK["traj"], "left"),
        ("h8_end", "H8 planned", ("rel", 0.02, 0.13), INK["traj"], "left"),
        ("unobserved:0", "Unobserved\nobstacles", ("abs", 0.86, 0.22), INK["grey"], "center"),
    ],
    # 坐标均为原图归一化坐标；"pt:u,v" 表示直接指向原图上的一点（用于指向点云区域这类无单一锚点的对象）
    "schematic": [
        ("goal", "Goal", ("abs", 0.710, 0.206), INK["goal"], "center"),
        ("unobserved:3", "Unobserved\nobstacle", ("abs", 0.854, 0.102), INK["grey"], "center"),
        ("pt:0.369,0.347", "Local point cloud", ("abs", 0.304, 0.113), INK["pc"], "center"),
        ("frustum_corner", "Camera FOV\n60°×47°", ("abs", 0.799, 0.503), INK["fov"], "center"),
        ("h8_end", "Planned\n(H8)", ("abs", 0.669, 0.752), INK["traj"], "center"),
        ("h4_mid", "Executed\n(H4)", ("abs", 0.205, 0.560), INK["traj"], "center"),
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("img")
    ap.add_argument("--layout", default="real", choices=list(LAYOUTS))
    ap.add_argument("--width_mm", type=float, default=62)
    ap.add_argument("--fontsize", type=float, default=7.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--crop", type=float, nargs=4, default=(0.0, 0.0, 1.0, 1.0), help="x0 y0 x1 y1（归一化）")
    a = ap.parse_args()
    im = Image.open(a.img)
    anchors = json.loads(Path(a.img).with_suffix(".anchors.json").read_text())
    W, H = im.size
    x0, y0, x1, y1 = a.crop
    im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    w_in = a.width_mm / 25.4
    fig = plt.figure(figsize=(w_in, w_in * im.size[1] / im.size[0]))
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(im); ax.axis("off")

    def px(u, v):
        return ((u - x0) / (x1 - x0) * im.size[0], (v - y0) / (y1 - y0) * im.size[1])

    for key, text, pos, col, ha in LAYOUTS[a.layout]:
        if key.startswith("pt:"):
            u, v = (float(t) for t in key[3:].split(","))
        elif ":" in key:
            k, i = key.split(":"); u, v = anchors[k][int(i)]
        else:
            u, v = anchors[key]
        tu, tv = (u + pos[1], v + pos[2]) if pos[0] == "rel" else pos[1:]
        ax.annotate(text, px(u, v), px(tu, tv), color=col, fontsize=a.fontsize, ha=ha, va="center",
                    linespacing=1.05,
                    arrowprops=dict(arrowstyle="-", lw=0.45, color=col, shrinkA=2, shrinkB=1.5))
    fig.savefig(a.out + ".pdf", dpi=600)
    fig.savefig(a.out + ".png", dpi=600)
    print("saved", a.out)


if __name__ == "__main__":
    main()
