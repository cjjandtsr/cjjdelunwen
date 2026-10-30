"""在渲染图上按锚点添加英文标注（矢量文字），输出PDF+PNG，模拟图1中央面板的印刷效果。

python annotate_panel.py _preview/env_panel_proto.png --width_mm 62 --out _preview/env_panel_annotated
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6.5, "pdf.fonttype": 42})

LABELS = [  # (锚点, 文字, 文字偏移dx, dy, 颜色)
    ("goal", "Goal", -0.14, -0.10, "#B85A0E"),
    ("frustum_corner", "Camera FOV\n60°×47°", -0.02, 0.16, "#3D66A8"),
    ("points_centroid", "Local point cloud", -0.36, -0.30, "#2F5E57"),
    ("h4_mid", "H4 executed", -0.24, 0.12, "#00795A"),
    ("h8_end", "H8 planned", 0.02, 0.13, "#005C91"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("img")
    ap.add_argument("--width_mm", type=float, default=62)
    ap.add_argument("--out", required=True)
    ap.add_argument("--crop", type=float, nargs=4, default=(0.0, 0.18, 1.0, 1.0), help="x0 y0 x1 y1（归一化）")
    a = ap.parse_args()
    im = Image.open(a.img)
    anchors = json.loads(Path(a.img).with_suffix(".anchors.json").read_text())
    W, H = im.size
    x0, y0, x1, y1 = a.crop
    im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    w_in = a.width_mm / 25.4
    h_in = w_in * im.size[1] / im.size[0]
    fig = plt.figure(figsize=(w_in, h_in))
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(im); ax.axis("off")

    def to_px(u, v):
        return ((u - x0) / (x1 - x0) * im.size[0], (v - y0) / (y1 - y0) * im.size[1])

    for key, text, dx, dy, col in LABELS:
        u, v = anchors[key]
        px, py = to_px(u, v)
        tx, ty = to_px(u + dx, v + dy)
        ax.annotate(text, (px, py), (tx, ty), color=col, fontsize=6.5, ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.5, color=col, shrinkA=1, shrinkB=1))
    if anchors["unobserved"]:
        cand = [p for p in anchors["unobserved"] if 0.75 < p[0] < 0.92 and 0.3 < p[1] < 0.6] or anchors["unobserved"]
        u, v = cand[0]
        px, py = to_px(u, v)
        ax.annotate("Unobserved\nobstacles", (px, py), to_px(0.86, 0.22),
                    color="#6B6B6B", fontsize=6.5, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.5, color="#8A8A8A"))
    fig.savefig(a.out + ".pdf", dpi=600)
    fig.savefig(a.out + ".png", dpi=600)
    print("saved", a.out)


if __name__ == "__main__":
    main()
