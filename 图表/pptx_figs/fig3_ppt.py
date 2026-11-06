"""Figure 3 (progress reward and planned-risk evaluation), native PowerPoint shapes, 190 x 70 mm (718 x 265 px).
variant 'curve': (a) distance-vs-decision plot; variant 'rings': (a) top-down best-distance rings.
(b) is identical in both. All risk values in (b) are computed from Eq. (8) of 论文大稿_v3 for the drawn geometry;
the trajectory in (a) is schematic."""
import math
from pp import Fig

S = 8; F = 9.33; TT = 12
PANEL = ("#F7F9FC", "#A9BEDD")
DARK = "#2E4A73"; NOTE = "#5A6270"; AMB = "#B88A52"; AMBF = "#EDD9BC"; GREY = "#8A8F98"
EXE = "#6E8DBE"; EVA = "#A9BEDD"
RISK1, RISK2 = "#F8ECEE", "#EDCBD0"   # low-saturation collision family: outer / inner band
i = lambda s: f"<i>{s}</i>"
sub = lambda a, b: i(a) + "<sub>" + b + "</sub>"

# ---- schematic episode used by (a) ----
D = [10, 9.2, 8.3, 7.6, 7.1, 7.0, 7.4, 8.1, 8.6, 8.4, 7.6, 6.9, 6.3, 5.4, 4.6, 3.7, 2.9, 2.1, 1.4, 0.9, 0.5]
B = []
for d in D:
    B.append(min(d, B[-1]) if B else d)
D0 = D[0]
R = [10 * (B[t] - B[t + 1]) / D0 for t in range(len(D) - 1)]

# ---- (b) geometry: obstacle clearance of the 8 planned segments (m) ----
DO = [1.6, 1.4, 1.2, 1.0, 0.75, 0.40, 0.25, 0.08]
ALT = 1.5   # flight height (m): ground term is zero


def Bf(d, dw, dc):
    return min(1.0, max(0.0, (dw - d) / (dw - dc))) ** 2


W_ = [1, 1, 1, 1] + [2 ** (-(m - 4) / 4) for m in range(5, 9)]
Q = [W_[m] / 2 * (Bf(DO[m], 0.45, 0.10) + Bf(ALT, 1.0, 0.20)) for m in range(8)]
RHO = max(max(Q[:4]), max(Q[4:]))


def build(slide, variant="curve", oy=0):
    f = Fig(slide, 0, oy)
    seg = lambda x1, y1, x2, y2, color="#5A6B85", sw=1.0, head=True, dash=None: f.line(x1, y1, x2, y2, color, sw, head, dash)
    note = lambda x, y, w, t, align="left", color=NOTE: f.label(x, y, w, t, fs=S, italic=True, color=color, align=align)

    # ===================== (a) =====================
    f.rect(4, 4, 318, 257, *PANEL, radius=8)
    f.label(4, 7, 318, "<b>(a) Progress reward: paid only for a new best</b>", fs=TT)
    if variant == "curve":
        X0, X1, YT, YB = 44, 306, 44, 150
        sx = (X1 - X0) / (len(D) - 1); sy = (YB - YT) / 10
        px = lambda t: X0 + t * sx
        py = lambda d: YB - d * sy
        # detour shading
        f.rect(px(5), YT - 6, px(11) - px(5), YB - YT + 6, "#ECEFF3", None, radius=0)
        note(px(5), YT - 6, px(11) - px(5), "detour: no penalty", align="center")
        # axes
        seg(X0, YB, X1 + 6, YB, color="#4A5563", sw=0.8)
        seg(X0, YB, X0, YT - 10, color="#4A5563", sw=0.8)
        for v in (0, 5, 10):
            seg(X0 - 3, py(v), X0, py(v), color="#4A5563", sw=0.8, head=False)
            f.label(X0 - 22, py(v) - 5, 18, str(v), fs=S, align="right")
        f.label(8, 26, 80, "goal distance (m)", fs=S, align="left")
        # current distance (thin grey) and best-so-far (thick blue step)
        f.poly([(px(t), py(d)) for t, d in enumerate(D)], None, GREY, 0.9, closed=False)
        for t, d in enumerate(D):
            f.oval(px(t), py(d), 1.5, fill="#FFFFFF", line=GREY, lw=0.7)
        step = []
        for t, b in enumerate(B):
            if t:
                step.append((px(t), py(B[t - 1])))
            step.append((px(t), py(b)))
        f.poly(step, None, DARK, 1.8, closed=False)
        # legend for the two lines
        seg(200, 52, 214, 52, color=GREY, sw=0.9, head=False)
        f.label(217, 47, 100, "current distance", fs=S, align="left")
        seg(200, 63, 214, 63, color=DARK, sw=1.8, head=False)
        f.label(217, 58, 100, "best so far " + sub("b", "t"), fs=S, align="left")
        # reward bars
        BY0 = 228; sc = 34
        f.label(8, 172, 200, "progress reward 10(" + sub("b", "t") + " − " + sub("b", "t+1") + ")/" + sub("D", "0"), fs=S, align="left")
        seg(X0, BY0, X1 + 6, BY0, color="#4A5563", sw=0.8, head=False)
        for t, r in enumerate(R):
            if r > 1e-9:
                h = r * sc
                f.rect(px(t) + 2, BY0 - h, sx - 4, h, AMBF, AMB, radius=0, lw=0.7)
        f.label(X1 - 70, BY0 + 3, 76, "decision cycle " + i("t"), fs=S, align="right")
        # annotations
        note(px(5) - 4, BY0 - 30, 110, "back below the old best:<br>only the new part is paid", color="#6B5434")
        seg(px(9) + 6, BY0 - 12, px(10) + sx / 2 - 1, BY0 - 5, color=AMB, sw=0.7)
    else:
        GX, GY, SC = 252, 140, 13.5
        clip = (8, 24, 318, 257)
        th = [180, 180, 181, 182, 184, 190, 205, 220, 232, 240, 245, 247, 246, 243, 238, 232, 225, 218, 210, 200, 190]
        P = [(GX + d * SC * math.cos(math.radians(a)), GY + d * SC * math.sin(math.radians(a))) for d, a in zip(D, th)]
        # obstacle
        f.rect(176, 80, 28, 116, "#D5D9DF", GREY, radius=1)
        note(165, 198, 50, "obstacle", align="center")
        # best-distance rings (clipped to the panel)
        rings = sorted(set(round(b, 1) for b in B if b > 1.0), reverse=True)
        rings = [r for r in rings if r in (10.0, 8.3, 7.0, 5.4, 3.7, 2.1)]
        for r in rings:
            pts, cur = [], []
            for k in range(361):
                a = math.radians(k)
                x, y = GX + r * SC * math.cos(a), GY + r * SC * math.sin(a)
                if clip[0] <= x <= clip[2] and clip[1] <= y <= clip[3]:
                    cur.append((x, y))
                elif cur:
                    pts.append(cur); cur = []
            if cur:
                pts.append(cur)
            if len(pts) > 1 and pts[0][0] == (GX + r * SC, GY) and pts[-1][-1][1] < GY:
                pts[0] = pts[-1] + pts[0]; pts.pop()
            for c in pts:
                if len(c) > 1:
                    f.poly(c, None, "#9FB4D6", 0.7, closed=False, dash="dash")
        # path: amber when the step sets a new best, grey otherwise
        for t in range(len(P) - 1):
            new = B[t + 1] < B[t] - 1e-9
            seg(P[t][0], P[t][1], P[t + 1][0], P[t + 1][1], color=AMB if new else GREY, sw=1.8 if new else 1.0, head=False)
        for t, p in enumerate(P[:-1]):
            f.oval(p[0], p[1], 1.6, fill="#FFFFFF", line="#4A5563", lw=0.6)
        f.oval(P[0][0], P[0][1], 3, fill=DARK, line=DARK)
        note(P[0][0] - 30, P[0][1] + 5, 40, "start", align="center")
        f.oval(GX, GY, 0.5 * SC, fill="#FFFFFF", line=DARK, lw=1.0)
        f.oval(GX, GY, 1.4, fill=DARK, line=DARK)
        note(GX + 8, GY + 2, 40, "goal")
        # labels
        note(268, 32, 52, "rings: best<br>distance " + sub("b", "t"), color=DARK)
        seg(12, 236, 26, 236, color=AMB, sw=1.8, head=False)
        f.label(29, 231, 150, "new best → reward", fs=S, align="left")
        seg(118, 236, 132, 236, color=GREY, sw=1.0, head=False)
        f.label(135, 231, 180, "detour or revisit → no reward, no penalty", fs=S, align="left")

    # ===================== (b) =====================
    f.rect(328, 4, 386, 257, *PANEL, radius=8)
    f.label(328, 7, 386, "<b>(b) Risk: executed prefix and unexecuted plan</b>", fs=TT)
    M = 60.0                           # px per metre (side view, x–z)
    GYb = 226                          # ground line
    XO = 488                           # obstacle face
    ZY = GYb - ALT * M                 # flight height
    # ground bands
    f.rect(334, GYb - 1.0 * M, 240, 1.0 * M, RISK1, None, radius=0)
    f.rect(334, GYb - 0.2 * M, 240, 0.2 * M, RISK2, None, radius=0)
    seg(334, GYb, 574, GYb, color="#4A5563", sw=1.0, head=False)
    note(338, GYb - 1.0 * M + 1, 120, "ground: " + sub("d", "w") + " = 1.0 m", color="#8E2C3A")
    note(338, GYb - 0.2 * M - 10, 120, sub("d", "c") + " = 0.20 m", color="#8E2C3A")
    # obstacle bands and obstacle
    top = 66
    f.rect(XO - 0.45 * M, top - 0.45 * M, 30 + 0.9 * M, GYb - top + 0.45 * M, RISK1, None, radius=4)
    f.rect(XO - 0.10 * M, top - 0.10 * M, 30 + 0.2 * M, GYb - top + 0.10 * M, RISK2, None, radius=2)
    f.rect(XO, top, 30, GYb - top, "#D5D9DF", GREY, radius=1)
    note(XO - 0.45 * M - 2, 38, 120, "obstacle: " + sub("d", "w") + " = 0.45 m, " + sub("d", "c") + " = 0.10 m", color="#8E2C3A")
    # H8 window: segments 1–4 executed, 5–8 planned
    xs = [XO - 1.85 * M] + [XO - d * M for d in DO]
    zs = [ZY] * 9
    for m in range(8):
        ex = m < 4
        seg(xs[m], zs[m], xs[m + 1], zs[m + 1], color=EXE if ex else EVA, sw=2.0 if ex else 1.4, head=False,
            dash=None if ex else "dot")
    for m in range(8):
        f.oval(xs[m + 1], zs[m + 1], 2.0, fill=EXE if m < 4 else "#FFFFFF", line=EXE, lw=0.8)
        f.label(xs[m + 1] - 5, zs[m + 1] - 13, 10, str(m + 1), fs=S, color=DARK)
    f.oval(xs[0], zs[0], 3.2, fill=DARK, line=DARK)
    note(xs[0] - 40, zs[0] + 5, 60, "UAV at decision " + i("t"), align="left", color=DARK)
    f.label(xs[1] - 6, zs[0] + 16, 70, "executed prefix 1–4", fs=S, color=DARK, align="left")
    f.label(xs[5] - 2, zs[0] + 26, 80, "unexecuted plan 5–8", fs=S, color="#6E8DBE", align="left")

    # bar chart of q_m
    BX0, BYB, BW, GAP, HS = 604, 180, 10, 3, 0.3
    HPX = 110
    f.label(592, 30, 120, "segment risk " + sub("q", i("m")), fs=S, bold=True, color=DARK)
    seg(BX0 - 3, BYB, BX0 + 8 * (BW + GAP) + 2, BYB, color="#4A5563", sw=0.8, head=False)
    seg(BX0 - 3, BYB, BX0 - 3, BYB - HPX - 6, color="#4A5563", sw=0.8, head=False)
    for v in (0.0, 0.1, 0.2, 0.3):
        y = BYB - v / HS * HPX
        seg(BX0 - 6, y, BX0 - 3, y, color="#4A5563", sw=0.8, head=False)
        f.label(BX0 - 26, y - 5, 20, f"{v:.1f}", fs=S, align="right")
    for m in range(8):
        x = BX0 + m * (BW + GAP)
        h = Q[m] / HS * HPX
        if h > 0.3:
            f.rect(x, BYB - h, BW, h, "#E2AEB6" if m >= 4 else "#C9D8EC", "#8E2C3A" if m >= 4 else EXE, radius=0, lw=0.7)
        f.label(x - 2, BYB + 1, BW + 4, str(m + 1), fs=S)
    f.label(BX0 - 22, BYB + 11, 140, sub("w", i("m")) + " = 1, 1, 1, 1, " + ", ".join(f"{W_[m]:.2f}" for m in range(4, 8)), fs=S, align="left", color=NOTE, italic=True)
    # maxima
    xa0, xa1 = BX0, BX0 + 4 * (BW + GAP) - GAP
    xb0, xb1 = BX0 + 4 * (BW + GAP), BX0 + 8 * (BW + GAP) - GAP
    for a, b in ((xa0, xa1), (xb0, xb1)):
        f.poly([(a, BYB + 24), (a, BYB + 27), (b, BYB + 27), (b, BYB + 24)], None, DARK, 0.8, closed=False)
    f.label(xa0 - 6, BYB + 28, 60, f"prefix max<br>{max(Q[:4]):.2f}", fs=S, color=DARK)
    f.label(xb0 - 6, BYB + 28, 60, f"plan max<br>{max(Q[4:]):.2f}", fs=S, color="#8E2C3A")
    f.label(578, 242, 136, i("ρ") + "<sub>" + i("t") + f"</sub> = max({max(Q[:4]):.2f}, {max(Q[4:]):.2f}) = {RHO:.2f}", fs=S, bold=True, color=DARK)
    return f, Q, RHO
