"""Figure 4 v-d (2026-11-09): two-layer decision process, receding-horizon execution and post-training
credit assignment. Layout follows the user's reference images (environment / denoising / post-training bands);
content follows 论文大稿_v3 §3.1, §3.5, 表2 (K = 10 DDIM steps, γ_d = 0.8, γ = 0.99, λ_GAE = 0.95) and
2026-11-09 审视 §9. Corrections relative to the references: r_t enters GAE (not the critic input);
R_{t,j} is the new/old policy ratio, not derived from Â_t; planning window = steps 3–10 (includes the
executed prefix); training steps are Gaussian around the DDIM mean (not DDPM)."""
from pp import Fig

F = 9.33; S = 8
PANEL = ("#F7F7F8", "#A9AEB5"); CREAM = ("#FFFBED", "#CDBB8A")
PAST = ("#E3E3E3", "#B5B8BD"); EXE = ("#95A9CE", "#6F84AB"); PLAN = ("#DBE3EF", "#95A9CE"); UNUSED = ("#FAFAFB", "#C5C9CF")
COND = ("#FBE3D2", "#C9773F"); OBS = ("#E7F3DF", "#8DB580"); RISK = ("#EDD3D3", "#A65D61")
TR = ("#FEF1CB", "#AC9A6A"); OL = "#817153"; TXT = "#5E5236"
DARK = "#2F3E5C"; GREY = "#55607A"; NOTE = "#5A6270"; ORA = "#C9773F"
i = lambda s: f"<i>{s}</i>"
Zs = lambda k: f"<i>Z</i><sup>{k}</sup>"


def build(slide, obs_img, oy=0):
    f = Fig(slide, 0, oy)
    seg = lambda x1, y1, x2, y2, c=GREY, sw=1.0, head=True, dash=None: f.line(x1, y1, x2, y2, c, sw, head, dash)

    def tab(x, y, w, text, fill, color):
        f.card(x, y, w, 15, text, fill, None, fs=F, bold=True, color=color, radius=4)

    def bracket(x0, x1, y, up=False, c=DARK):
        d = -3 if up else 3
        f.poly([(x0, y), (x0, y + d), (x1, y + d), (x1, y)], None, c, 0.8, closed=False)

    # ================= (a) environment layer =================
    f.rect(2, 2, 714, 128, *PANEL, radius=6)
    tab(6, 6, 158, "(a) Environment layer", "#C9DDBE", "#2F4A26")
    f.label(170, 7, 260, i("physical time; one step = 0.3 s"), fs=S, align="left", color=NOTE)
    # observation
    f.rect(8, 28, 112, 74, OBS[0], OBS[1], radius=4)
    f.img(14, 30, 100, 46, obs_img)
    f.label(10, 77, 108, f"{i('o')}<sub>{i('t')}−2</sub>, {i('o')}<sub>{i('t')}−1</sub>, {i('o')}<sub>{i('t')}</sub>", fs=S)
    f.label(10, 90, 108, "point cloud + 9-D state", fs=S, color=NOTE)
    seg(120, 62, 136, 62)
    f.card(137, 51, 30, 22, f"{i('c')}<sub>{i('t')}</sub>", COND[0], COND[1], fs=F, radius=4)
    seg(167, 62, 179, 62)
    # trajectory box
    f.rect(180, 24, 262, 74, "#FFFFFF", "#B9C3D3", radius=4)
    f.label(180, 26, 262, "trajectory of one decision: 16 steps × 11 values", fs=S, color=DARK)
    P, W, X0, Y0 = 16, 14, 184, 54
    pal = [PAST] * 2 + [EXE] * 4 + [PLAN] * 4 + [UNUSED] * 6
    for k in range(16):
        c = pal[k]
        f.card(X0 + P * k, Y0, W, 14, str(k + 1), c[0], c[1], fs=S, radius=1.5,
               dashed=(c is UNUSED), color="#1F2A3D" if c is EXE else INK_(c))
    cx = lambda a, b: (X0 + P * (a - 1) + X0 + P * (b - 1) + W) / 2
    xl = lambda a: X0 + P * (a - 1); xr = lambda b: X0 + P * (b - 1) + W
    bracket(xl(3), xr(10), Y0 - 2, up=True, c=GREY)
    f.label(cx(3, 10) - 60, Y0 - 17, 120, "planning window (steps 3–10)", fs=S, color=GREY)
    for a, b, t in [(1, 2, "past frames,<br>not executed"), (3, 6, "executed prefix<br>(1.2 s)"),
                    (7, 10, "planned,<br>not executed"), (11, 16, "not used")]:
        bracket(xl(a) + 0.5, xr(b) - 0.5, Y0 + 16)
        f.label(cx(a, b) - 30, Y0 + 21, 60, t, fs=S, color=DARK if a == 3 else NOTE)
    seg(442, 62, 456, 62)
    f.card(457, 46, 78, 32, "execute steps 3–6,<br>observe every 0.3 s", "#FFFFFF", "#8A93A3", fs=S, radius=4)
    seg(535, 62, 549, 62)
    f.poly([(550, 62), (582, 42), (614, 62), (582, 82)], "#FFFFFF", "#8A93A3", 0.9)
    f.label(556, 54, 52, "arrival or<br>collision?", fs=S)
    seg(614, 62, 626, 62, head=False)
    seg(626, 40, 626, 84, head=False)
    seg(626, 40, 638, 40); seg(626, 84, 638, 84)
    f.label(607, 64, 18, "yes", fs=S, color=NOTE)
    f.label(642, 54, 70, "episode ends", fs=S, color=NOTE)
    f.card(639, 31, 74, 18, "arrival", "#E9EEF6", "#6F84AB", fs=S, radius=4)
    f.card(639, 75, 74, 18, "collision", RISK[0], RISK[1], fs=S, radius=4)
    # loop back
    seg(582, 82, 582, 116, head=False)
    seg(582, 116, 64, 116, head=False)
    seg(64, 116, 64, 103)
    f.card(190, 110, 220, 12, "no: new decision from the latest three frames", "#FFFFFF", "#B9C3D3", fs=S, radius=3)
    f.label(590, 96, 20, "no", fs=S, color=NOTE)

    # ================= (b) denoising layer =================
    f.rect(2, 136, 714, 112, *PANEL, radius=6)
    tab(6, 140, 158, "(b) Denoising layer", "#DBE3EF", DARK)
    f.label(170, 141, 400, i("inside one decision; no flight time") + "  ·  each arrow " + i("j") +
            ": Gaussian transition π<sub>θ</sub>(" + Zs(i("k") + "−1") + " | " + Zs(i("k")) + ", " + i("c") + "<sub>" + i("t") +
            "</sub>),  " + i("K") + " = 10", fs=S, align="left", color=NOTE)
    # condition strip fed by c_t
    seg(152, 73, 152, 160, ORA, 1.1)
    f.card(36, 161, 380, 11, f"condition {i('c')}<sub>{i('t')}</sub> enters every denoising step", COND[0], COND[1], fs=S, radius=3)
    NX = lambda n: 50 + 38 * n          # node n: Z^(10-n)
    NY, R = 190, 9
    for n in range(10):
        seg(NX(n) + R, NY, NX(n + 1) - R - 1, NY, c=GREY, sw=0.9)
        f.label(NX(n) + 9, NY - 13, 20, f"{i('j')}={n}", fs=S, color=NOTE)
    for n in range(11):
        k = 10 - n
        fill, line = ("#FFFFFF", "#8A93A3") if k == 10 else ((EXE[0], EXE[1]) if k == 0 else (PLAN[0], PLAN[1]))
        f.oval(NX(n), NY, R, fill=fill, line=line, html=Zs(k), fs=S)
    f.label(NX(0) - 24, NY + 10, 48, "𝒩(0, " + i("I") + ")", fs=S, color=NOTE)
    # Z0 back to the trajectory box
    seg(NX(10), NY - R, NX(10), 99, ORA, 1.1)
    f.label(NX(10) + 6, 160, 120, Zs(0) + " = the 16 × 11 trajectory", fs=S, align="left", color=ORA)
    # credit-weight bars under each transition (post-training)
    base = 236
    for j in range(10):
        w = 0.8 ** (9 - j); h = 18 * w; x = NX(j) + 19
        f.rect(x - 5, base - h, 10, h, "#D9C48A", None, radius=0)
    seg(NX(0) + 8, base, NX(10) - 8, base, OL, 0.6, head=False)
    f.label(NX(0) + 4, base + 1, 30, "0.134", fs=S, color=OL)
    f.label(NX(9) + 4, base + 1, 30, "1.000", fs=S, color=OL)
    f.label(468, 178, 244, "Training: Gaussian step around the DDIM mean.<br>Evaluation: deterministic DDIM (10 steps).",
            fs=S, align="left", color=NOTE)
    f.label(468, 214, 244, "post-training credit weight of step " + i("j") + ": γ<sub>" + i("d") + "</sub><sup>" + i("K") +
            "−" + i("j") + "−1</sup>, γ<sub>" + i("d") + "</sub> = 0.8<br>(largest at the last denoising step)",
            fs=S, align="left", color=OL)

    # ================= (c) post-training only =================
    f.rect(2, 254, 714, 148, *CREAM, radius=6)
    tab(6, 258, 250, "(c) Post-training only (not used at deployment)", "#F7E3A8", TXT)
    YC = 312
    f.card(10, YC - 12, 44, 24, f"{i('c')}<sub>{i('t')}</sub>, {i('e')}<sub>{i('t')}</sub>", "#FFFFFF", TR[1], fs=F, radius=4)
    seg(54, YC, 66, YC, OL)
    f.card(67, YC - 15, 80, 30, f"critic {i('V')}<sub>φ</sub>({i('c')}<sub>{i('t')}</sub>, {i('e')}<sub>{i('t')}</sub>)", "#FFFFFF", TR[1], fs=F, radius=4)
    f.label(67, YC + 17, 110, i("e") + "<sub>" + i("t") + "</sub>: task progress; own value loss", fs=S, align="left", color=TXT)
    seg(147, YC, 165, YC, OL)
    f.card(244, 276, 34, 18, f"{i('r')}<sub>{i('t')}</sub>", "#FFFFFF", TR[1], fs=F, radius=4)
    f.label(282, 280, 60, "per decision", fs=S, align="left", color=TXT)
    seg(244, 285, 226, 285, OL, head=False); seg(226, 285, 226, YC - 16, OL)
    f.card(166, YC - 15, 70, 30, "GAE<br>γ = 0.99, λ = 0.95", "#FFFFFF", TR[1], fs=S, radius=4)
    seg(236, YC, 252, YC, OL)
    f.card(253, YC - 15, 70, 30, f"advantage {i('Â')}<sub>{i('t')}</sub><br>batch-normalized", "#FFFFFF", TR[1], fs=S, radius=4)
    seg(323, YC, 339, YC, OL)
    f.card(340, YC - 15, 88, 30, f"{i('Ã')}<sub>{i('t,j')}</sub> = γ<sub>{i('d')}</sub><sup>{i('K')}−{i('j')}−1</sup> {i('Â')}<sub>{i('t')}</sub><br>per denoising step {i('j')}",
           "#FFFFFF", TR[1], fs=S, radius=4)
    seg(428, YC - 6, 450, YC - 6, OL)
    f.card(340, 342, 88, 30, f"ratio {i('R')}<sub>{i('t,j')}</sub> (new / old π<sub>θ</sub>)<br>on steps 3–10", "#FFFFFF", TR[1], fs=S, radius=4)
    seg(428, 357, 440, 357, OL, head=False); seg(440, 357, 440, YC + 8, OL, head=False); seg(440, YC + 8, 450, YC + 8, OL)
    f.card(451, YC - 17, 92, 34, "<b>clipped PPO loss</b><br>" + i("j") + " = 0, …, 9", TR[0], OL, fs=F, radius=4)
    seg(543, YC, 561, YC, OL)
    f.card(562, YC - 17, 146, 34, "<b>update LoRA only</b><br>pretrained weights frozen", "#FFFFFF", OL, fs=F, radius=4)
    f.lock(694, YC - 14)
    f.card(451, 350, 257, 40,
           f"Stage I (iter. 1–128): no regularization<br>Stage II (iter. 129–256): + λ·{i('L')}<sub>reg</sub>, λ = 0.0106<br>"
           f"{i('L')}<sub>reg</sub>: behavior cloning on a fixed success trajectory library",
           "#FFFFFF", TR[1], fs=S, radius=4, color=TXT)
    seg(497, 350, 497, YC + 18, OL)
    return f


def INK_(c):
    return "#8A8F98" if c is UNUSED else "#1F2328"
