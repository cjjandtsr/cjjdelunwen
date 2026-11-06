"""Figure 2 (policy network) as native PowerPoint shapes; port of 图表/design_canvas/src/body_fig2v2.py.
Changes vs canvas: all 7 px text raised to 8 px (6 pt) with the affected boxes widened."""
from pp import Fig, measure, pt_of

import os
ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "design_canvas", "assets") + "/"
S = 8; F = 9.33; TT = 12
FROZ = ("#FFFFFF", "#7F9CC8"); CORE = ("#EEF3FA", "#B7C9E5"); COND = ("#DCE6F3", "#6E8DBE")
LORA = ("#F6EBDA", "#B88A52"); FILM = ("#F2C3A0", "#C98A5E"); OUTC = ("#EAF0F8", "#4F6FA3")
NEUT = ("#FFFFFF", "#8A8F98"); PANEL = ("#F7F9FC", "#A9BEDD"); NOTE = "#5A6270"; LR = "#B88A52"
BL = ("#B9CCE8", "#DCE6F3", "#93AED6", "#6F8BBA"); OR = ("#F2C3A0", "#F8DCC7", "#E0A77E", "#C98A5E")
i = lambda s: f"<i>{s}</i>"
Zt = lambda k: i("Z") + "<sub>" + i("t") + "</sub><sup>" + k + "</sup>"


def build(slide, oy=16):
    f = Fig(slide, 0, oy)
    seg = lambda x1, y1, x2, y2, color="#5A6B85", sw=1.2, head=True, dash=None: f.line(x1, y1, x2, y2, color, sw, head, dash)
    band = lambda x, y, w, h, fill, border, radius=6, dashed=False: f.rect(x, y, w, h, fill, border, radius, dashed)
    bx = lambda x, y, w, h, html, pal, fs=F, dashed=False, bold=False: f.card(x, y, w, h, html, pal[0], pal[1], fs, dashed=dashed, bold=bold)
    note = lambda x, y, w, t, align="left": f.label(x, y, w, t, fs=S, italic=True, color=NOTE, align=align)
    dims = lambda x, y, w, t: f.label(x, y, w, t, fs=S, italic=True, color="#3A4452")
    vbar = lambda x, y, w, h, pal: f.rect(x, y, w, h, pal[0], pal[1], radius=2)

    def ttl(x, y, w, text, lock=False):
        f.label(x, y, w, f"<b>{text}</b>", fs=TT)
        if lock:
            tw = measure(text, pt_of(TT), bold=True)
            f.lock(x + w / 2 + tw / 2 + 3, y + 3.5)

    def ring(x, y, w, h, pad=2.5, r=4):
        f.rect(x - pad, y - pad, w + 2 * pad, h + 2 * pad, None, LR, radius=r, dashed=True, lw=0.9, line_dash="dash")

    def ring_poly(x, w, h0, h1, yc, pad=2.5):
        a, b = h0 + 2 * pad, h1 + 2 * pad
        x0 = x - pad; W_ = w + 2 * pad
        f.poly([(x0, yc - a / 2), (x0 + W_, yc - b / 2), (x0 + W_, yc + b / 2), (x0, yc + a / 2)], None, LR, 0.9, dash="dash")

    def stage(x, w, h0, h1, yc, html):
        f.poly([(x, yc - h0 / 2), (x + w, yc - h1 / 2), (x + w, yc + h1 / 2), (x, yc + h0 / 2)], "#FFFFFF", "#7F9CC8", 0.9)
        f.label(x, yc - max(h0, h1) / 2, w, html, fs=S, color="#1F3A63", h=max(h0, h1), anchor="middle")

    def cube(x, y, w, h, d, front, top, side, stroke):
        f.rect(x, y + d, w, h, front, stroke, radius=0, lw=0.6)
        f.poly([(x, y + d), (x + d, y), (x + w + d, y), (x + w, y + d)], top, stroke, 0.6)
        f.poly([(x + w, y + d), (x + w + d, y), (x + w + d, y + h), (x + w, y + h + d)], side, stroke, 0.6)

    # ======================= (a) overall flow =======================
    band(8, 8, 702, 116, *PANEL, radius=8)
    ttl(8, 11, 702, "(a) Overall Network Flow")
    f.label(10, 30, 92, "<b>Observations (3 frames)</b>", fs=S)
    f.img(20, 42, 70, 45, ASSET + "threeframe.png")
    dims(14, 92, 82, "3 × (4096×3, 9)")
    seg(91, 66, 103, 66)
    f.poly([(104, 38), (170, 49), (170, 83), (104, 94)], line="#7F9CC8", lw=0.7, grad=("#E3EBF6", "#C9D8EC"))
    f.text_lock(104, 38, 66, 56, "Shared<br>observation<br>encoder", fs=F, color="#1F3A63")
    seg(171, 66, 179, 66)
    vbar(180, 40, 12, 52, COND)
    f.label(174, 27, 24, i("c<sub>t</sub>"), bold=True, color="#2E4A73")
    f.label(189, 94, 24, "576", fs=S, italic=True, color="#3A4452", align="left")
    band(206, 27, 360, 93, *CORE, radius=6)
    f.label(414, 106, 148, "<b>Iterative denoising</b>", fs=S, color="#2E4A73", align="right")
    bx(214, 44, 64, 28, "", NEUT)
    f.img(218, 47, 56, 12, ASSET + "noisytraj.png")
    f.label(214, 59, 64, "noise " + Zt(i("K")), fs=S)
    dims(214, 73, 64, "16×11")
    bx(214, 87, 64, 16, "step " + i("k"), COND, fs=S)
    seg(279, 58, 297, 58)
    seg(279, 95, 285, 95, color="#6E8DBE", head=False)
    seg(285, 95, 285, 68, color="#6E8DBE", head=False)
    seg(285, 68, 297, 68, color="#6E8DBE")
    band(298, 40, 112, 66, "#FFFFFF", "#4C72B0", radius=4)
    # mini U-Net cubes, centred at x=354, top=44
    hs = [36, 27, 19, 12]; base, dpt = 44, 3
    xx = 3; parts = []
    for hh in hs:
        parts.append(("b", xx, base - hh - dpt, 5, hh, dpt)); parts.append(("o", xx + 8, base - hh * 0.8 - 2, 1.5, hh * 0.8, 1.5)); xx += 10
    parts.append(("m", xx, base - 7 - dpt, 8, 5, dpt)); xx += 12
    for hh in reversed(hs):
        parts.append(("o", xx, base - hh * 0.8 - 2, 1.5, hh * 0.8, 1.5)); parts.append(("b", xx + 3, base - hh - dpt, 5, hh, dpt)); xx += 10
    UW = xx + 2; X0 = 354 - UW / 2; Y0 = 44
    for k, x_, y_, w_, h_, d_ in parts:
        pal = BL if k == "b" else OR if k == "o" else ("#C9D8EC", "#E3EBF6", "#A7BEDF", "#6F8BBA")
        cube(X0 + x_, Y0 + y_, w_, h_, d_, *pal)
    # 'U-Net [lock] + LoRA'
    s1 = "U-Net"; s2 = " + LoRA"
    w1 = measure(s1, 6, bold=True); w2 = measure(s2, 6, bold=True)
    tot = w1 + 10 + w2; x0 = 354 - tot / 2
    f.label(x0 - 1, 93, w1 + 2, "<b>U-Net</b>", fs=S)
    f.lock(x0 + w1 + 1.5, 94.5)
    f.label(x0 + w1 + 9, 93, w2 + 4, "<b>+ <span style=\"color: #9C7A4C\">LoRA</span></b>", fs=S, align="left")
    seg(186, 93, 186, 116, color="#6E8DBE", head=False)
    seg(186, 116, 354, 116, color="#6E8DBE", head=False)
    seg(354, 116, 354, 107, color="#6E8DBE")
    note(250, 103, 70, "condition " + i("c<sub>t</sub>"))
    seg(411, 70, 461, 70)
    f.label(410, 55, 54, "predict " + Zt("0"), fs=S)
    bx(462, 58, 64, 24, "DDIM<br>update", NEUT, fs=S)
    seg(494, 58, 494, 31, head=False)
    seg(494, 31, 354, 31, head=False)
    seg(354, 31, 354, 39)
    f.label(420, 32, 60, "× 10", fs=S, bold=True, color="#2E4A73")
    seg(527, 70, 577, 70)
    bx(578, 58, 50, 24, "De-<br>normalize", NEUT, fs=S)
    seg(629, 70, 637, 70)
    band(638, 30, 66, 86, *OUTC, radius=5)
    f.label(638, 33, 66, "<b>Action seq.</b>", fs=S, color="#2E4A73")
    pts = []
    for j in range(12):
        cx, cy = 642 + 4 + j * 4.6, 48 + 30 - 22 * (j / 11) + 8 * (j / 11) ** 2
        pts.append((cx, cy))
    f.curve((646, 78), (662, 62), (678, 54), (697, 56), "#4F6FA3", 0.7, head=False)
    for cx, cy in pts:
        f.oval(cx, cy, 1.6, fill="#4F6FA3", line="#4F6FA3", lw=0.3)
    dims(638, 86, 66, "16 steps × 11")

    # ======================= (b) shared observation encoder =======================
    band(8, 132, 292, 220, *PANEL, radius=8)
    ttl(8, 135, 292, "(b) Shared Observation Encoder", lock=True)
    band(14, 153, 228, 120, "#FFFFFF", "#B9C3D0", radius=4, dashed=True)
    f.label(18, 155, 100, "<b>Point-cloud branch</b>", fs=S, align="left")
    f.img(18, 170, 36, 28, ASSET + "pointcloud.png")
    dims(16, 202, 44, "4096 × 3")
    seg(55, 186, 62, 186)
    bx(63, 174, 44, 24, "point-wise<br>Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
    seg(108, 186, 113, 186)
    band(114, 168, 124, 52, "#F2F6FB", "#8EA7CF", radius=4, dashed=True)
    f.label(118, 169, 80, "PointNet stage", fs=S, align="left", color="#3D5A80", bold=True)
    f.label(208, 169, 28, "×4", fs=S, align="right", color="#3D5A80", bold=True)
    bx(118, 181, 40, 16, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
    seg(159, 189, 179, 189)
    seg(138, 197, 138, 202, head=False)
    bx(116, 203, 64, 13, "global max-pool", NEUT, fs=S)
    seg(181, 209, 186, 209, head=False)
    seg(186, 209, 186, 196)
    f.concat_c(186, 189)
    seg(192, 189, 201, 189)
    bx(202, 181, 34, 16, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
    bx(18, 238, 58, 26, "concat 4 stages<br>(4 × 128)", NEUT, fs=S)
    seg(77, 251, 87, 251)
    bx(88, 241, 38, 20, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
    seg(127, 251, 137, 251)
    bx(138, 241, 50, 20, "max-pool<br>over points", NEUT, fs=S)
    seg(189, 251, 205, 251)
    vbar(206, 240, 10, 22, ("#C9D8EC", "#8EA7CF"))
    dims(216, 245, 26, "128")
    seg(176, 220, 176, 228, head=False)
    seg(176, 228, 47, 228, head=False)
    seg(47, 228, 47, 237)
    band(14, 279, 228, 44, "#FFFFFF", "#B9C3D0", radius=4, dashed=True)
    f.label(18, 281, 100, "<b>State branch</b>", fs=S, align="left")
    bx(20, 296, 42, 20, "9-d state", ("#FFFFFF", "#5A6B85"), fs=S)
    seg(63, 306, 75, 306)
    bx(76, 296, 84, 20, "MLP 9→64→64", ("#DCE6F3", "#7F9CC8"), fs=S)
    seg(161, 306, 205, 306)
    vbar(206, 299, 10, 14, ("#DCE6F3", "#7F9CC8"))
    dims(216, 302, 26, "64")
    seg(241, 251, 245, 251, head=False)
    seg(241, 306, 245, 306, head=False)
    seg(245, 251, 245, 306, head=False)
    seg(245, 278, 255, 278)
    bx(256, 262, 38, 32, "concat<br>192 per<br>frame", NEUT, fs=S)
    seg(275, 294, 275, 309)
    note(250, 296, 22, "×3")
    vbar(266, 310, 18, 30, COND)
    f.label(250, 340, 50, i("c<sub>t</sub>") + " 576", fs=S, bold=True, color="#2E4A73")

    # ======================= (c) one denoising call =======================
    band(308, 132, 402, 136, *PANEL, radius=8)
    ttl(308, 132, 402, "(c) One Denoising Call: Conditional 1D U-Net")
    bx(316, 151, 40, 14, "step " + i("k"), COND, fs=S)
    seg(357, 158, 367, 158, color="#6E8DBE")
    bx(366, 150, 70, 16, "time embedding", COND, fs=S)
    ring(366, 150, 70, 16, pad=2)
    bx(316, 170, 40, 14, i("c<sub>t</sub>"), COND, fs=S)
    seg(437, 158, 446, 158, color="#6E8DBE", head=False)
    seg(446, 158, 446, 162, color="#6E8DBE")
    seg(357, 177, 446, 177, color="#6E8DBE", head=False)
    seg(446, 177, 446, 174, color="#6E8DBE")
    dims(372, 177, 30, "576")
    f.concat_c(446, 168)
    seg(452, 168, 471, 168, color="#6E8DBE")
    bx(472, 159, 62, 18, "condition 704", COND, fs=S)
    seg(535, 168, 612, 168, color="#6E8DBE", head=False, dash="dash")
    seg(612, 168, 612, 199, color="#6E8DBE", head=False, dash="dash")
    note(538, 156, 160, "to the FiLM of every residual block")
    band(334, 186, 346, 76, "#FFFFFF", "#8EA7CF", radius=4, dashed=True)
    f.label(334, 188, 250, "<b>1D U-Net</b>: 6 stages × 2 residual blocks", fs=S, color="#2E4A73")
    YC = 226; L = {16: 44, 8: 32, 4: 22}; G = 16
    spec = [("Down<br>256", 36, 16, 8), ("Down<br>512", 36, 8, 4), ("Down<br>1024", 36, 4, 4), ("Mid<br>1024", 36, 4, 4),
            ("Up<br>512", 36, 4, 8), ("Up<br>256", 36, 8, 16)]
    x = 340; geo = {}; bars = []
    for k_, (lb, w, a_, b_) in enumerate(spec):
        stage(x, w, L[a_], L[b_], YC, lb)
        ring_poly(x, w, L[a_], L[b_], YC)
        geo[k_] = (x, w, (L[a_] + L[b_]) / 2)
        if k_ < len(spec) - 1:
            bh = min(L[b_], L[spec[k_ + 1][2]]); bx_ = x + w + 4
            f.rect(bx_, YC - bh / 2, 8, bh, FILM[0], FILM[1], radius=1)
            seg(x + w, YC, bx_, YC, head=False)
            seg(bx_ + 8, YC, x + w + G, YC, head=False)
            bars.append((bx_ + 4, YC - bh / 2)); x += w + G
        else:
            seg(x + w + 1, YC, x + w + 9, YC); x += w + 10
    seg(int(bars[0][0]), 199, int(bars[-1][0]), 199, color="#6E8DBE", head=False)
    for bxc, top in bars:
        seg(int(bxc), 199, int(bxc), int(top) - 1, color="#6E8DBE", sw=0.9)
    f.card(x, YC - 22, 26, 44, "final<br>conv", "#FFFFFF", "#7F9CC8", fs=S)
    ring(x, YC - 22, 26, 44)
    seg(x + 27, YC, 685, YC)
    f.label(684, YC - 11, 26, "<b>" + Zt("0") + "<br>16×11</b>", fs=S, color="#2E4A73")
    f.label(308, YC - 11, 26, Zt(i("k")) + "<br>16×11", fs=S)
    seg(331, YC, 339, YC)

    def skip(src, dst, yb):
        xs_, ws_, hs_ = geo[src]; xd, wd, hd = geo[dst]
        cs, cd = int(xs_ + ws_ / 2), int(xd + wd / 2)
        seg(cs, int(YC + hs_ / 2) + 1, cs, yb, color="#4A5563", sw=0.8, head=False, dash="dot")
        seg(cs, yb, cd, yb, color="#4A5563", sw=0.8, head=False, dash="dot")
        seg(cd, yb, cd, int(YC + hd / 2) + 2, color="#4A5563", sw=0.8, dash="dot")
    skip(2, 4, 247); skip(1, 5, 254)
    note(344, 250, 56, "skip (concat)")

    # ======================= (d) residual block with LoRA =======================
    band(308, 276, 402, 76, *PANEL, radius=8)
    ttl(308, 277, 402, "(d) Conditional Residual Block with LoRA")
    RY = 324
    f.label(310, RY - 7, 10, i("x"), fs=S)
    names = ["Conv1d", "GN", "Mish", "FiLM", "Conv1d", "GN", "Mish"]
    ws_ = [32, 20, 24, 26, 32, 20, 24]
    xs_ = []; xc = 330
    for ww in ws_:
        xs_.append(xc); xc += ww + 9
    for xx_, nm, ww in zip(xs_, names, ws_):
        if nm == "FiLM":
            bx(xx_, RY - 8, ww, 16, nm, FILM, fs=S)
        else:
            bx(xx_, RY - 8, ww, 16, nm, FROZ, fs=S)
            if nm == "Conv1d":
                ring(xx_, RY - 8, ww, 16, pad=2)
    for xx_, ww, nx in zip(xs_[:-1], ws_[:-1], xs_[1:]):
        seg(xx_ + ww, RY, nx - 1, RY, sw=1)
    fx = xs_[3] + 13; CYD = 303
    f.label(312, CYD - 9, 36, "condition<br>704", fs=S, color="#2E4A73")
    seg(349, CYD, 355, CYD, color="#6E8DBE", sw=1)
    bx(356, CYD - 7, 26, 14, "Mish", FROZ, fs=S)
    seg(383, CYD, 389, CYD, color="#6E8DBE", sw=1)
    bx(390, CYD - 7, 36, 14, "Linear", FROZ, fs=S)
    ring(390, CYD - 7, 36, 14, pad=2)
    seg(428, CYD, fx, CYD, color="#6E8DBE", sw=1, head=False)
    seg(fx, CYD, fx, RY - 9, color="#6E8DBE", sw=1)
    note(fx + 3, CYD, 24, i("γ") + ", " + i("β"))
    end = xs_[-1] + ws_[-1]
    seg(end, RY, end + 9, RY)
    f.plus(end + 15, RY)
    seg(end + 20, RY, end + 28, RY)
    f.label(end + 29, RY - 6, 10, i("y"), fs=S, align="left")
    seg(320, RY, 329, RY)
    seg(320, RY, 320, 343, head=False)
    seg(320, 343, end + 15, 343, head=False)
    seg(end + 15, 343, end + 15, RY + 6)
    bx(412, 336, 130, 14, "residual: Identity / 1×1 Conv1d", FROZ, fs=S)
    ring(412, 336, 130, 14, pad=2)
    band(596, 296, 108, 52, "#FBF6EE", "#B88A52", radius=4, dashed=True)
    f.label(600, 297, 100, "<b>LoRA-adapted layer</b>", fs=S, color="#6B5434", align="left")
    seg(600, 324, 604, 324, head=False)
    seg(604, 313, 604, 337, head=False)
    seg(604, 313, 613, 313)
    bx(614, 307, 36, 13, i("W") + "<sub>0</sub>", FROZ, fs=S)
    f.lock(640, 309)
    seg(604, 337, 613, 337)
    bx(614, 331, 15, 13, i("A"), LORA, fs=S)
    seg(630, 337, 638, 337)
    bx(639, 331, 15, 13, i("B"), LORA, fs=S)
    seg(651, 313, 658, 313, head=False)
    seg(655, 337, 658, 337, head=False)
    seg(658, 313, 658, 337, head=False)
    note(661, 316, 46, i("y") + " = " + i("W") + "<sub>0</sub>" + i("x") + "<br>+ (" + i("α") + "/" + i("r") + ")" + i("BAx"))
    seg(137, 118, 137, 131, color="#7A8496", sw=0.9, head=False, dash="dash")
    seg(354, 121, 354, 131, color="#7A8496", sw=0.9, head=False, dash="dash")

    # legend
    f.lock(316, 356)
    f.label(326, 355, 100, "frozen in post-training", fs=S, align="left")
    f.rect(414, 357, 7, 7, FILM[0], FILM[1], radius=0)
    f.label(424, 355, 40, "FiLM", fs=S, align="left")
    f.rect(453, 358, 8, 5, "#FFFFFF", "#7F9CC8", radius=0)
    ring(453, 358, 8, 5, pad=1.8, r=2)
    f.label(465, 355, 150, "LoRA-adapted layer", fs=S, align="left")
    f.rect(616, 357, 7, 7, COND[0], COND[1], radius=0)
    f.label(626, 355, 50, "condition", fs=S, align="left")
    f.rect(668, 357, 7, 7, OUTC[0], OUTC[1], radius=0)
    f.label(678, 355, 40, "output", fs=S, align="left")
    return f
