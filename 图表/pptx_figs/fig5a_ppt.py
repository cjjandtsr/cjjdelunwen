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
        f.rect(x0, 4, 172, 252, "#FFFFFF", HEAD[c][1], radius=6)
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
        f.label(ax + 70, ay + 141, 70, "20 m", fs=S, color=NOTE)
        f.label(ax + 141, ay + 64, 24, "20 m", fs=S, color=NOTE, align="left")
        f.card(x0 + 4, 200, 164, 50, f"{i('n')} = {n} held-out tasks<br>straight-route success {succ:g}%", HEAD[c][0], None, fs=F, radius=4)
        f.rect(x0 + 22, 238, 128, 5, "#FFFFFF", "#B5B8BD", radius=0, lw=0.5)
        if succ > 0:
            f.rect(x0 + 22, 238, 128 * succ / 100, 5, "#95A9CE", None, radius=0)
    # ---------- definition column ----------
    X = 542
    f.rect(X, 4, 170, 252, "#FFFFFF", "#A9AEB5", radius=6, dashed=True)
    f.label(X, 9, 170, "<b>Route-centred obstacle density</b>", fs=F, color=DARK)
    f.label(X, 26, 170, "ρ = Vol(" + i("O") + " ∩ " + i("R") + ") / Vol(" + i("R") + ")", fs=F)
    f.label(X + 6, 40, 160, i("R") + ": region within 1.0 m on either side of<br>the straight start–goal route; " + i("O") + ": obstacles",
            fs=S, align="left", color=NOTE)
    # oblique sketch of R: length 110 px, 2.0 m wide (depth), height (z_G − z_S) + 2 m; 1 m = 8 px
    bx, by, Lx, H, dx, dy = X + 30, 140, 96, 34, 14, -8
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
    seg(bx - 6, by, bx - 6, sxy[1] - 3, GREY, 0.6, head=False)
    f.label(bx - 30, by - 9, 22, "1.0 m", fs=S, color=NOTE, align="right")
    seg(bx + Lx + dx + 6, by - H + dy, bx + Lx + dx + 6, gxy[1] + 3, GREY, 0.6, head=False)
    f.label(bx + Lx + dx + 8, by - H + dy - 1, 22, "1.0 m", fs=S, color=NOTE, align="left")
    f.label(bx + Lx - 20, by + 2, 50, "2.0 m wide", fs=S, color=NOTE, align="left")
    f.label(X + 6, 152, 160, "lower end 1.0 m below the lower of " + i("S") + ", " + i("G") +
            "<br>(not below 0.2 m); upper end 1.0 m above<br>the higher of " + i("S") + ", " + i("G"), fs=S, align="left", color=NOTE)
    f.label(X + 6, 186, 160, "ρ<sub>med</sub>: median ρ over training-world tasks,<br>fixed before evaluation", fs=S, align="left", color=NOTE)
    # legend
    ly = 214
    f.rect(X + 8, ly, 12, 7, BAND[0], BAND[1], radius=0, lw=0.6, dashed=True)
    f.label(X + 24, ly - 2, 60, i("R"), fs=S, align="left")
    f.rect(X + 50, ly, 10, 7, HIT[0], HIT[1], radius=0, lw=0.8)
    f.label(X + 63, ly - 2, 100, "obstacle overlapping " + i("R"), fs=S, align="left")
    f.rect(X + 8, ly + 13, 10, 7, OBST[0], OBST[1], radius=0, lw=0.8)
    f.oval(X + 26, ly + 16.5, 3.5, fill=OBST[0], line=OBST[1], lw=0.8)
    f.label(X + 33, ly + 11, 130, "other obstacle (box / cylinder)", fs=S, align="left")
    f.oval(X + 12, ly + 30, 3.2, fill=START[0], line=START[1], lw=1.0)
    f.label(X + 18, ly + 25, 40, i("S") + " start", fs=S, align="left")
    f.oval(X + 58, ly + 30, 3.2, fill=GOAL[0], line=GOAL[1], lw=1.2)
    f.label(X + 64, ly + 25, 40, i("G") + " goal", fs=S, align="left")
    seg(X + 100, ly + 30, X + 116, ly + 30, DARK, 0.8, head=False, dash="dash")
    f.label(X + 119, ly + 25, 50, "straight route", fs=S, align="left")
    return f
