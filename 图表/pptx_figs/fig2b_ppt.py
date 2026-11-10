"""Figure 2 (policy network), simplified layout after the user's reference image (2026-11-06).
Colour semantics: blue = frozen (lock), orange = LoRA (trainable), purple = condition / FiLM, dark-blue outline = output.
Code facts kept: FiLM has its own linear map in every residual block; U-Net = 3 down, 1 mid, 2 up stages + output conv;
skips Down1024->Up512, Down512->Up256; LoRA on denoiser Linear/Conv1d only (r = 8, alpha/r = 1, B init 0)."""
import os
from pp import Fig, measure, pt_of

HERE = os.path.dirname(os.path.abspath(__file__))
CANVAS = os.path.join(HERE, "..", "design_canvas", "assets") + "/"
OWN = os.path.join(HERE, "assets") + "/"
S = 8; F = 9.33; TT = 12
FRZ = ("#E3EBF6", "#7F9CC8"); LORA = ("#F2C49B", "#C98A5E"); COND = ("#E7E0F4", "#8E7CC3"); CONDT = "#4B3B78"
OUT = ("#EEF3FA", "#2E4A73"); NEUT = ("#FFFFFF", "#8A8F98"); PANEL = ("#F7F9FC", "#A9BEDD"); SUBP = ("#FFFFFF", "#B9C3D0")
INK = "#1f2328"; DARK = "#2E4A73"; NOTE = "#5A6270"; AR = "#4A5A75"
i = lambda s: f"<i>{s}</i>"


def use_tol():
    """Paul Tol light scheme (Tol 2021) tints."""
    global FRZ, LORA, COND, CONDT, OUT, PANEL, DARK, AR
    FRZ = ("#E3EEF8", "#5590C8"); LORA = ("#F7C9B6", "#EE8866"); COND = ("#F6ECC0", "#B59A2E"); CONDT = "#6B5A12"
    OUT = ("#E6F6FF", "#2B4A6E"); PANEL = ("#F2F7FC", "#A0C4E8"); DARK = "#2B4A6E"; AR = "#4A5A75"


def use_enhancing():
    """Low-saturation palette sampled from Liu et al. 2026 (Enhancing), Fig. 1."""
    global FRZ, LORA, COND, CONDT, OUT, PANEL, SUBP, DARK, AR, LORABG, LORAT
    FRZ = ("#DBE3EF", "#899DBE"); LORA = ("#F7E3A8", "#817153"); COND = ("#FBE3D2", "#D9925E"); CONDT = "#8A4B22"
    OUT = ("#EEF2F8", "#2F3E5C"); PANEL = ("#F5F5F5", "#A9AEB5"); SUBP = ("#FFFFFF", "#C5C9CF"); DARK = "#2F3E5C"
    AR = "#5C6B85"; LORABG = "#FFFBED"; LORAT = "#5E5236"


LORABG = "#FDF2EE"; LORAT = "#8F3F22"


def build(slide, oy=10):
    f = Fig(slide, 0, oy)
    seg = lambda x1, y1, x2, y2, color=AR, sw=0.9, head=True, dash=None: f.line(x1, y1, x2, y2, color, sw, head, dash)
    box = lambda x, y, w, h, t, pal=NEUT, fs=S, bold=False, color=INK, r=3: f.card(x, y, w, h, t, pal[0], pal[1], fs, bold=bold, color=color, radius=r)
    note = lambda x, y, w, t, align="left", color=NOTE: f.label(x, y, w, t, fs=S, italic=True, color=color, align=align)
    lora = lambda x, y: f.rect(x, y, 5, 6, LORA[0], LORA[1], radius=0, lw=0.6)

    def title(x, y, text, lock=False):
        f.label(x, y, 300, f"<b>{text}</b>", fs=TT, align="left")
        if lock:
            f.lock(x + measure(text, pt_of(TT), bold=True) + 4, y + 3.5)

    def trap(x, w, h0, h1, yc, text, pal=FRZ):
        f.poly([(x, yc - h0 / 2), (x + w, yc - h1 / 2), (x + w, yc + h1 / 2), (x, yc + h0 / 2)], pal[0], pal[1], 0.8)
        f.label(x, yc - 10, w, text, fs=S, color=DARK, h=20, anchor="middle")

    # ================= (a) overall network =================
    f.rect(6, 4, 706, 126, *PANEL, radius=6)
    title(12, 6, "(a) Overall network")
    f.rect(14, 24, 108, 100, *SUBP, radius=4)
    f.label(14, 26, 108, "<b>Three observation frames</b>", fs=S)
    for k, lb in enumerate([i("t") + "−2", i("t") + "−1", i("t")]):
        f.img(18 + 34 * k, 38, 30, 22, CANVAS + "pointcloud.png")
        f.label(18 + 34 * k, 60, 30, lb, fs=S)
    f.label(14, 70, 108, "+", fs=F, bold=True)
    f.label(16, 82, 44, "9-d state", fs=S, align="left")
    for k in range(6):
        f.rect(58 + 9.5 * k, 83, 8, 8, "#C9D8EC", "#7F9CC8", radius=0, lw=0.5)
    f.label(14, 100, 108, "3 × (4096 × 3, 9)", fs=S, italic=True)
    seg(122, 72, 134, 72)
    f.poly([(135, 32), (203, 48), (203, 96), (135, 112)], FRZ[0], FRZ[1], 0.9)
    f.text_lock(135, 52, 68, 40, "Shared<br>observation<br>encoder", fs=S, color=DARK)
    seg(204, 72, 214, 72)
    f.rect(215, 46, 14, 52, COND[0], COND[1], radius=2)
    f.label(207, 32, 30, "<b>" + i("c<sub>t</sub>") + "</b>", fs=F, color=CONDT)
    f.label(207, 99, 30, "576", fs=S)
    # iterative denoising
    f.rect(246, 16, 312, 110, "#FFFFFF", COND[1], radius=5, dashed=True, lw=0.8)
    box(254, 34, 64, 42, "", NEUT)
    f.label(254, 35, 64, "noise " + i("Z<sup>K</sup>"), fs=S)
    f.img(262, 46, 48, 18, OWN + "noise_16x11.png")
    f.label(254, 64, 64, "16 × 11", fs=S, italic=True)
    box(254, 82, 64, 16, "step " + i("k"), COND, color=CONDT)
    seg(319, 55, 330, 55)
    seg(319, 90, 330, 90)
    UX0, UX1, UY0, UY1 = 331, 403, 30, 106
    f.poly([(UX0, UY0), (367 - 6, 48), (367 + 6, 48), (UX1, UY0), (UX1, UY1), (367 + 6, 88), (367 - 6, 88), (UX0, UY1)], FRZ[0], FRZ[1], 0.9)
    f.text_lock(UX0, 56, UX1 - UX0, 24, "Conditional<br>1D U-Net", fs=S, color=DARK)
    for x_, y_ in ((UX0 + 4, 38), (UX0 + 4, 92), (UX1 - 9, 38), (UX1 - 9, 92)):
        lora(x_, y_)
    # condition c_t enters the U-Net from above
    seg(230, 60, 238, 60, color=CONDT, head=False)
    seg(238, 60, 238, 27, color=CONDT, head=False)
    seg(238, 27, 367, 27, color=CONDT, head=False)
    seg(367, 27, 367, 47, color=CONDT)
    seg(404, 68, 414, 68)
    box(415, 34, 62, 66, "", NEUT)
    f.label(415, 35, 62, "predicted " + i("Z<sup>0</sup>"), fs=S)
    f.img(422, 48, 48, 26, OWN + "clean_16x11.png")
    f.label(415, 78, 62, "16 × 11", fs=S, italic=True)
    seg(478, 68, 488, 68)
    box(489, 56, 56, 24, "DDIM<br>update", NEUT)
    # loop: repeat K times
    seg(517, 81, 517, 110, head=False)
    seg(517, 110, 367, 110, head=False)
    seg(367, 110, 367, 89)
    f.label(246, 113, 312, "<b>Iterative denoising: repeat " + i("K") + " = 10 times</b>", fs=S, color=CONDT)
    seg(546, 68, 568, 68)
    box(569, 56, 54, 24, "de-<br>normalize", NEUT)
    seg(624, 68, 636, 68)
    f.rect(637, 24, 68, 100, OUT[0], OUT[1], radius=5)
    f.label(637, 27, 68, "<b>Trajectory<br>sequence</b>", fs=S, color=DARK)
    f.curve((646, 100), (660, 84), (676, 66), (698, 58), "#4F6FA3", 0.7, head=False)
    for k in range(10):
        t = k / 9
        x_ = (1-t)**3*646 + 3*(1-t)**2*t*660 + 3*(1-t)*t**2*676 + t**3*698
        y_ = (1-t)**3*100 + 3*(1-t)**2*t*84 + 3*(1-t)*t**2*66 + t**3*58
        f.oval(x_, y_, 1.8, fill="#4F6FA3", line="#4F6FA3", lw=0.3)
    f.label(637, 106, 68, "16 × 11", fs=S, italic=True)

    # ================= (b) shared observation encoder =================
    f.rect(6, 136, 296, 240, *PANEL, radius=6)
    title(12, 138, "(b) Shared observation encoder", lock=True)
    f.rect(12, 156, 284, 114, *SUBP, radius=4, dashed=True, lw=0.8)
    f.label(16, 158, 200, "<b>Single-frame encoding</b>", fs=S, align="left")
    f.img(18, 172, 36, 24, CANVAS + "pointcloud.png")
    f.label(14, 197, 46, "XYZ points<br>4096 × 3", fs=S)
    seg(56, 184, 66, 184)
    box(67, 172, 44, 24, "point-wise<br>MLP", FRZ, color=DARK)
    seg(112, 184, 122, 184)
    box(123, 172, 50, 24, "PointNet<br>stages × 4", FRZ, color=DARK)
    seg(174, 184, 184, 184)
    box(185, 172, 46, 24, "max-pool<br>over points", FRZ, color=DARK)
    seg(232, 184, 242, 184)
    f.rect(243, 172, 9, 24, "#C9D8EC", "#7F9CC8", radius=1)
    f.label(236, 197, 24, "128", fs=S)
    f.label(16, 222, 50, "9-d state", fs=S, align="left")
    for k in range(5):
        f.rect(18 + 9.5 * k, 234, 8, 8, "#C9D8EC", "#7F9CC8", radius=0, lw=0.5)
    seg(67, 238, 112, 238)
    box(113, 228, 44, 20, "MLP", FRZ, color=DARK)
    seg(158, 238, 242, 238)
    f.rect(243, 232, 9, 12, "#C9D8EC", "#7F9CC8", radius=1)
    f.label(236, 245, 24, "64", fs=S)
    seg(253, 184, 268, 184, head=False); seg(268, 184, 268, 205)
    seg(253, 238, 268, 238, head=False); seg(268, 238, 268, 217)
    f.concat_c(268, 211)
    seg(274, 211, 281, 211)
    f.rect(282, 193, 9, 36, COND[0], COND[1], radius=1)
    f.label(272, 230, 30, "192", fs=S)
    f.rect(12, 276, 284, 94, *SUBP, radius=4, dashed=True, lw=0.8)
    f.label(16, 278, 220, "<b>Three frames, shared weights</b>", fs=S, align="left")
    seg(286, 242, 286, 290, dash="dash", color=NOTE)
    note(240, 256, 44, "each frame", align="right")
    for k, lb in enumerate(["frame " + i("t") + "−2", "frame " + i("t") + "−1", "frame " + i("t")]):
        x_ = 20 + 58 * k
        box(x_, 294, 52, 30, lb + "<br>192", COND, color=CONDT)
        seg(x_ + 26, 325, x_ + 26, 346, head=False)
    seg(46, 346, 196, 346, head=False)
    seg(196, 346, 196, 336)
    f.concat_c(196, 330)
    seg(202, 330, 214, 330)
    f.rect(215, 322, 74, 16, COND[0], COND[1], radius=1)
    for k in range(1, 3):
        seg(215 + 74 * k / 3, 322, 215 + 74 * k / 3, 338, color=COND[1], sw=0.6, head=False)
    f.label(215, 340, 74, "<b>" + i("c<sub>t</sub>") + "</b> 576", fs=S, color=CONDT)

    # ================= (c) one denoising call =================
    f.rect(308, 136, 404, 128, *PANEL, radius=6)
    title(314, 138, "(c) One denoising call: conditional 1D U-Net")
    box(316, 158, 36, 16, "step " + i("k"), COND, color=CONDT)
    seg(353, 166, 363, 166, color=CONDT)
    box(364, 158, 82, 16, "time embedding 128", COND, color=CONDT)
    lora(439, 160)
    box(318, 182, 40, 16, i("c<sub>t</sub>") + " 576", COND, color=CONDT)
    seg(447, 166, 452, 166, color=CONDT, head=False); seg(452, 166, 452, 177, color=CONDT)
    seg(359, 190, 452, 190, color=CONDT, head=False); seg(452, 190, 452, 189, color=CONDT, head=False)
    f.concat_c(452, 183)
    seg(458, 183, 470, 183, color=CONDT)
    box(471, 175, 60, 16, "condition 704", COND, color=CONDT)
    note(535, 158, 176, "→ own linear map + FiLM in every residual block", color=CONDT)
    YC = 228
    spec = [("Down<br>256", 44, 34), ("Down<br>512", 34, 26), ("Down<br>1024", 26, 26), ("Mid<br>1024", 26, 26),
            ("Up<br>512", 26, 34), ("Up<br>256", 34, 44)]
    xs = []
    x = 346
    for k, (lb, h0, h1) in enumerate(spec):
        trap(x, 40, h0, h1, YC, lb)
        lora(x + 32, YC + min(h0, h1) / 2 - 9)
        xs.append((x, h0, h1))
        if k < len(spec) - 1:
            seg(x + 40, YC, x + 50, YC)
        x += 50
    seg(x - 10, YC, x, YC)
    box(x + 1, YC - 22, 30, 44, "output<br>conv", FRZ, color=DARK)
    lora(x + 23, YC + 13)
    seg(x + 32, YC, x + 42, YC)
    f.label(x + 42, YC - 11, 28, "<b>" + i("Z<sup>0</sup>") + "</b><br>16×11", fs=S, color=DARK)
    f.label(312, YC - 11, 28, i("Z<sup>k</sup>") + "<br>16×11", fs=S)
    seg(336, YC, 345, YC)
    # condition bus to every stage
    seg(501, 192, 501, 199, color=CONDT, head=False)
    seg(366, 199, 616, 199, color=CONDT, head=False)
    for (x0, h0, h1) in xs:
        seg(x0 + 20, 199, x0 + 20, YC - max(h0, h1) / 2 + (abs(h0 - h1) / 4) - 1, color=CONDT, sw=0.8)

    def skip(a, b, yb):
        xa = xs[a][0] + 20; xb = xs[b][0] + 20
        seg(xa, YC + 14, xa, yb, color=NOTE, sw=0.7, head=False, dash="dot")
        seg(xa, yb, xb, yb, color=NOTE, sw=0.7, head=False, dash="dot")
        seg(xb, yb, xb, YC + 14, color=NOTE, sw=0.7, dash="dot")
    skip(2, 4, 250); skip(1, 5, 257)
    note(312, 249, 34, "skips")

    # ================= (d) residual block and LoRA =================
    f.rect(308, 270, 404, 106, *PANEL, radius=6)
    title(314, 272, "(d) Residual block and low-rank adaptation")
    f.rect(314, 290, 246, 80, *SUBP, radius=4, dashed=True, lw=0.8)
    f.label(318, 291, 200, "<b>Conditional residual block</b> (× 12)", fs=S, align="left")
    RY = 336
    names = [("Conv–GN–Mish", 64, FRZ, True), ("FiLM", 30, COND, False), ("Conv–GN–Mish", 64, FRZ, True)]
    f.label(318, RY - 6, 8, i("x"), fs=S)
    seg(326, RY, 337, RY)
    x = 338; centers = []
    for k, (nm, w, pal, lo) in enumerate(names):
        box(x, RY - 9, w, 18, nm, pal, color=CONDT if nm == "FiLM" else DARK)
        if lo:
            lora(x + w - 7, RY - 7)
        centers.append(x + w / 2)
        if k < len(names) - 1:
            seg(x + w, RY, x + w + 13, RY)
        x += w + 14
    end = x - 14
    seg(end, RY, end + 10, RY)
    f.plus(end + 16, RY)
    seg(end + 21, RY, end + 30, RY)
    f.label(end + 31, RY - 6, 8, i("y"), fs=S, align="left")
    # residual path
    seg(331, RY, 331, 364, head=False)
    seg(331, 364, end + 16, 364, head=False)
    seg(end + 16, 364, end + 16, RY + 6)
    note(360, 352, 160, "residual: identity or 1×1 conv", align="center")
    # FiLM parameters from the condition
    fx = centers[1]
    f.label(318, 302, 40, "condition<br>704", fs=S, color=CONDT, h=18, anchor="middle")
    seg(359, 311, 369, 311, color=CONDT)
    box(370, 304, 36, 14, "Linear", FRZ, color=DARK)
    lora(400, 306)
    seg(407, 311, fx, 311, color=CONDT, head=False)
    seg(fx, 311, fx, RY - 9, color=CONDT)
    note(fx + 3, 312, 30, i("γ") + ", " + i("β"), color=CONDT)
    # LoRA mechanism
    f.rect(566, 290, 140, 80, LORABG, LORA[1], radius=4, dashed=True, lw=0.8)
    f.label(570, 292, 130, "<b>Low-rank adaptation (LoRA)</b>", fs=S, align="left", color=LORAT)
    LY = 324
    f.label(570, LY - 6, 8, i("x"), fs=S)
    seg(578, LY, 584, LY, head=False)
    seg(584, 312, 584, 336, head=False)
    seg(584, 312, 595, 312)
    box(596, 305, 40, 14, i("W") + "<sub>0</sub>", FRZ, color=DARK)
    f.lock(625, 307)
    seg(584, 336, 595, 336)
    box(596, 329, 16, 14, i("A"), LORA, color=LORAT)
    seg(613, 336, 619, 336)
    box(620, 329, 16, 14, i("B"), LORA, color=LORAT)
    seg(637, 312, 648, 312, head=False); seg(648, 312, 648, 318)
    seg(637, 336, 648, 336, head=False); seg(648, 336, 648, 330)
    f.plus(648, LY)
    seg(653, LY, 662, LY)
    f.label(663, LY - 6, 8, i("y"), fs=S, align="left")
    f.label(570, 348, 134, i("y") + " = " + i("W") + "<sub>0</sub>" + i("x") + " + (" + i("α") + "/" + i("r") + ")" + i("BAx") + ",  " + i("r") + " = 8", fs=S, align="left")
    f.label(570, 358, 134, i("B") + " initialized to 0; only " + i("A") + ", " + i("B") + " trained", fs=S, align="left", color=NOTE)

    # legend
    LGY = 382
    f.rect(170, LGY, 9, 8, FRZ[0], FRZ[1], radius=0); f.lock(182, LGY - 0.5)
    f.label(192, LGY - 1, 120, "frozen in post-training", fs=S, align="left")
    f.rect(290, LGY, 9, 8, LORA[0], LORA[1], radius=0)
    f.label(302, LGY - 1, 120, "LoRA (trainable)", fs=S, align="left")
    f.rect(380, LGY, 9, 8, COND[0], COND[1], radius=0)
    f.label(392, LGY - 1, 160, "condition and FiLM modulation", fs=S, align="left")
    f.rect(520, LGY, 9, 8, OUT[0], OUT[1], radius=0)
    f.label(532, LGY - 1, 60, "output", fs=S, align="left")
    return f
