"""Figure 5(a) v2 (2026-11-09): task difficulty classes. Layout after the user's reference images (three top views
+ definition column). Facts: 论文大稿_v3 §4.1.1 与表3 (59/67/64 tasks, straight-route success 100/46.3/9.4 %,
obstacles in a 20 m × 20 m area, 1–40 per world); 研究任务书 D6 (thresholds 0 / ρ_med; the value 0.04623 goes only
to the Table 3 note and the supplement; the word "corridor" is not used); region shape from
Improved-3D-Diffusion-Policy/scripts/routea_paired_support/task_geometry_metrics.py::corridor_density
(project repo commit 36dbc9b): horizontal half width 1.0 m along the start–goal ground projection, vertical
extent from min(z_S, z_G) − 1.0 m (not below 0.2 m) to max(z_S, z_G) + 1.0 m. Obstacle layouts are schematic."""
import math
from pp import Fig

F = 9.33; S = 8
GREY = "#55607A"; NOTE = "#5A6270"; DARK = "#2F3E5C"
BAND = ("#DBE3EF", "#6F84AB"); HIT = ("#EDD3D3", "#A65D61"); OBST = ("#D5D8DD", "#8C9199")
START = ("#E7F3DF", "#5E8A50"); GOAL = ("#FBE3D2", "#C9773F")
HEAD = [("#E9EEF6", "#95A9CE"), ("#FEF6DC", "#CDBB8A"), ("#F6E6E6", "#C99A9C")]
i = lambda s: f"<i>{s}</i>"
SC = 7.0  # px per metre

LAYOUT = {
    "sparse": dict(boxes=[(4, 15, 3, 2), (9, 17, 2, 2), (14, 4, 3, 2), (17, 8, 2, 3), (6, 10.8, 2, 2)],
                   cyls=[(12, 17, 1), (3, 8, .9), (17, 12.5, 1), (10, 4, .9), (18, 3, 1)]),
    "moderate": dict(boxes=[(4, 15, 3, 2), (9, 17, 2, 2), (14, 4, 3, 2), (17, 8, 2, 3), (8, 7.4, 2, 2)],
                     cyls=[(12, 17, 1), (3, 8, .9), (13.6, 12.6, 1), (10, 4, .9), (18, 3, 1)]),
    "dense": dict(boxes=[(4, 15, 3, 2), (5, 5.6, 2, 2), (14, 4, 3, 2), (11, 10.2, 2.5, 2), (16.4, 15.8, 2, 2)],
                  cyls=[(8, 8.6, 1), (3, 9, .9), (13.6, 13, 1), (10, 4, .9), (18, 3, 1)]),
}


def _hits_box(cx, cy, w, h):
    for a in range(11):
        for b in range(11):
            x, y = cx - w / 2 + w * a / 10, cy - h / 2 + h * b / 10
            if abs(x - y) / math.sqrt(2) <= 1.0:
                return True
    return False


def _hits_cyl(cx, cy, r):
    return abs(cx - cy) / math.sqrt(2) <= 1.0 + r


def build(slide, oy=0):
    f = Fig(slide, 0, oy)
    seg = lambda x1, y1, x2, y2, c=GREY, sw=1.0, head=True, dash=None: f.line(x1, y1, x2, y2, c, sw, head, dash)
    classes = [("sparse", "Sparse", "ρ = 0", 59, 100.0), ("moderate", "Moderate", "0 < ρ ≤ ρ<sub>med</sub>", 67, 46.3),
               ("dense", "Dense", "ρ > ρ<sub>med</sub>", 64, 9.4)]
    for c, (key, name, cond, n, succ) in enumerate(classes):
        x0 = 6 + 178 * c
        f.rect(x0, 4, 172, 218, "#FFFFFF", HEAD[c][1], radius=6)
        f.card(x0 + 4, 8, 164, 18, f"<b>{name}</b>,  {cond}", HEAD[c][0], None, fs=F, radius=4)
        ax, ay = x0 + 16, 40                    # obstacle area, 20 m × 20 m = 140 px
        P = lambda x, y: (ax + SC * x, ay + 140 - SC * y)
        f.rect(ax, ay, 140, 140, "#FBFBFC", "#2F3E5C", radius=0, lw=0.9)
        # route region (half width 1.0 m) along the S–G line, S and G outside the area
        h = 1.0 / math.sqrt(2)
        pts = [P(-1.2 - h, -1.2 + h), P(21.2 - h, 21.2 + h), P(21.2 + h, 21.2 - h), P(-1.2 + h, -1.2 - h)]
        f.poly(pts, BAND[0], BAND[1], 0.6, dash="dash")
        L = LAYOUT[key]
        for bx, by, w, hh in L["boxes"]:
            hit = _hits_box(bx, by, w, hh); col = HIT if hit else OBST
            px, py = P(bx - w / 2, by + hh / 2)
            f.rect(px, py, w * SC, hh * SC, col[0], col[1], radius=0, lw=0.9)
        for cx, cy, r in L["cyls"]:
            hit = _hits_cyl(cx, cy, r); col = HIT if hit else OBST
            px, py = P(cx, cy)
            f.oval(px, py, r * SC, fill=col[0], line=col[1], lw=0.9)
        sx, sy = P(-1.2, -1.2); gx, gy = P(21.2, 21.2)
        seg(sx, sy, gx, gy, DARK, 0.8, head=False, dash="dash")
        f.oval(sx, sy, 3.6, fill=START[0], line=START[1], lw=1.0)
        f.oval(gx, gy, 3.6, fill=GOAL[0], line=GOAL[1], lw=1.2)
        f.label(sx - 2, sy + 3, 10, i("S"), fs=S, color=START[1])
        f.label(gx - 15, gy - 4, 10, i("G"), fs=S, color=GOAL[1])
        if c == 0:
            f.label(ax + 35, ay + 141, 70, "20 m × 20 m obstacle area", fs=S, color=NOTE)
        f.label(x0 + 8, 202, 40, f"{i('n')} = {n}", fs=F, align="left")
        f.rect(x0 + 50, 205, 92, 8, "#FFFFFF", "#B5B8BD", radius=0, lw=0.5)
        if succ > 0:
            f.rect(x0 + 50, 205, 92 * succ / 100, 8, "#95A9CE", None, radius=0)
        f.label(x0 + 144, 202, 26, f"{succ:g}%", fs=F, align="left")
    # ---------- definition column ----------
    X = 542
    f.rect(X, 4, 170, 218, "#FFFFFF", "#A9AEB5", radius=6, dashed=True)
    f.label(X, 12, 170, "ρ = Vol(" + i("O") + " ∩ " + i("R") + ") / Vol(" + i("R") + ")", fs=F, bold=True, color=DARK)
    bx, by, Lx, H, dx, dy = X + 30, 104, 96, 34, 14, -8
    A, B = (bx, by), (bx + Lx, by)
    A2, B2 = (bx, by - H), (bx + Lx, by - H)
    C2, D2, D = (bx + dx, by - H + dy), (bx + Lx + dx, by - H + dy), (bx + Lx + dx, by + dy)
    f.poly([A, B, B2, A2], "#E9EEF6", BAND[1], 0.7)
    f.poly([A2, B2, D2, C2], "#DBE3EF", BAND[1], 0.7)
    f.poly([B, D, D2, B2], "#CBD5E6", BAND[1], 0.7)
    sxy = (bx + dx / 2, by + dy / 2 - 8); gxy = (bx + Lx + dx / 2, by - H + dy / 2 + 8)
    seg(*sxy, *gxy, DARK, 0.8, head=False, dash="dash")
    f.oval(*sxy, 3.2, fill=START[0], line=START[1], lw=1.0)
    f.oval(*gxy, 3.2, fill=GOAL[0], line=GOAL[1], lw=1.2)
    f.label(sxy[0] - 3, sxy[1] + 2, 10, i("S"), fs=S, color=START[1])
    f.label(gxy[0] - 12, gxy[1] - 4, 10, i("G"), fs=S, color=GOAL[1])
    seg(bx - 6, by, bx - 6, sxy[1] - 3, GREY, 0.6, head=False)
    f.label(bx - 30, by - 9, 22, "1.0 m", fs=S, color=NOTE, align="right")
    seg(bx + Lx + dx + 6, by - H + dy, bx + Lx + dx + 6, gxy[1] + 3, GREY, 0.6, head=False)
    f.label(bx + Lx + dx + 8, by - H + dy - 1, 22, "1.0 m", fs=S, color=NOTE, align="left")
    f.label(bx + Lx - 6, by - 2, 40, "2.0 m", fs=S, color=NOTE, align="left")
    f.label(X, 118, 170, "region " + i("R") + " around the straight route", fs=S, color=NOTE)
    # legend
    ly = 142
    rows = [("band", "region " + i("R")), ("hit", "obstacle in " + i("R")), ("obst", "other obstacle"),
            ("sg", i("S") + " start,  " + i("G") + " goal"), ("bar", "straight-route success")]
    for k, (kind, t) in enumerate(rows):
        y = ly + 15 * k; x = X + 14
        if kind == "band":
            f.rect(x, y, 16, 8, BAND[0], BAND[1], radius=0, lw=0.6, dashed=True)
        elif kind == "hit":
            f.rect(x + 2, y, 10, 8, HIT[0], HIT[1], radius=0, lw=0.8)
        elif kind == "obst":
            f.rect(x, y, 8, 8, OBST[0], OBST[1], radius=0, lw=0.8); f.oval(x + 13, y + 4, 3.8, fill=OBST[0], line=OBST[1], lw=0.8)
        elif kind == "sg":
            f.oval(x + 3, y + 4, 3.2, fill=START[0], line=START[1], lw=1.0); f.oval(x + 13, y + 4, 3.2, fill=GOAL[0], line=GOAL[1], lw=1.2)
        else:
            f.rect(x, y + 1, 16, 6, "#95A9CE", None, radius=0)
        f.label(x + 24, y - 2, 120, t, fs=S, align="left")
    return f
