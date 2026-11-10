"""Figure 4 (two-layer decision, receding-horizon execution and credit assignment), native PowerPoint shapes.
Three-layer layout after the user's reference; content follows 论文大稿_v3 §3.4–3.5 and the code facts in
2026-11-03 交接 §4.3 (2 aligned steps, H4 = steps 3–6, H8 = steps 3–10, ratio on H8, γ_d = 0.8, K = 10)."""
from pp import Fig

S = 8; F = 9.33
PANEL = ("#F5F5F5", "#A9AEB5"); TPANEL = ("#FFFBED", "#CDBB8A")
EXE = ("#95A9CE", "#899DBE"); EVA = ("#DBE3EF", "#95A9CE"); OUT = ("#FAFAFB", "#C5C9CF"); ALI = ("#E3E3E3", "#B5B8BD")
COND = ("#FBE3D2", "#D9925E"); TR = ("#FEF1CB", "#AC9A6A"); TR2 = ("#F7E3A8", "#817153")
DARK = "#2F3E5C"; GREY = "#5C6B85"; AMB = "#817153"; NOTE = "#5A6270"; TXT = "#5E5236"
i = lambda s: f"<i>{s}</i>"


def build(slide, oy=0):
    f = Fig(slide, 0, oy)
    seg = lambda x1, y1, x2, y2, color=GREY, sw=1.0, head=True, dash=None: f.line(x1, y1, x2, y2, color, sw, head, dash)
    note = lambda x, y, w, t, align="left", color=NOTE: f.label(x, y, w, t, fs=S, italic=True, color=color, align=align)

    def bracket(x0, x1, y, color=DARK):
        f.poly([(x0, y), (x0, y + 3), (x1, y + 3), (x1, y)], None, color, 0.8, closed=False)

    def side(y, h, n, title, sub, pal):
        f.rect(6, y, 66, h, pal[0], None, radius=4)
        f.label(8, y + h / 2 - 17, 62, f"<b>{n} {title}</b>", fs=F, color=DARK if pal[0] != TR[0] else TXT, h=22, anchor="middle")
        f.label(8, y + h / 2 + 5, 62, sub, fs=S, italic=True, color=NOTE, h=20, anchor="top")

    # ============ layer 1: environment (physical time) ============
    f.rect(2, 2, 714, 146, *PANEL, radius=6)
    side(6, 138, "1", "Environment<br>layer", "physical time", ("#EEF2F8", None))
    # time axis
    seg(116, 26, 538, 26, color="#4A5563", sw=0.9)
    f.label(84, 19, 30, i("t") + " (s)", fs=S, align="right")
    X = {"D0": (118, 152), "D1": (312, 346)}
    ex = [(152 + 40 * k, 192 + 40 * k) for k in range(4)] + [(346 + 40 * k, 386 + 40 * k) for k in range(4)]
    ticks = [(152, "0"), (192, "0.3"), (232, "0.6"), (272, "0.9"), (312, "1.2"), (386, "1.5"), (426, "1.8"), (466, "2.1"), (506, "2.4")]
    for x, t in ticks:
        seg(x, 23, x, 29, color="#4A5563", sw=0.8, head=False)
        f.label(x - 12, 12, 24, t, fs=S)
    for x in [152, 192, 232, 272, 312, 346, 386, 426, 466, 506]:
        f.oval(x, 26, 2.6, fill="#4F6FA3", line="#2E4A73", lw=0.6)
    # decision t+1 sits at 1.2 s: no flight time
    seg(312, 26, 346, 26, color="#FFFFFF", sw=2.2, head=False)
    seg(312, 26, 346, 26, color="#4A5563", sw=0.6, head=False, dash="dot")
    # row label
    f.label(76, 40, 40, "flight", fs=S, italic=True, color=NOTE, align="left")
    f.card(118, 36, 34, 22, "<b>decision</b><br>" + i("t"), "#FFFFFF", DARK, fs=S, color=DARK)
    f.card(312, 36, 34, 22, "<b>decision</b><br>" + i("t") + "+1", "#FFFFFF", DARK, fs=S, color=DARK)
    times = ["0–0.3 s", "0.3–0.6 s", "0.6–0.9 s", "0.9–1.2 s", "1.2–1.5 s", "1.5–1.8 s", "1.8–2.1 s", "2.1–2.4 s"]
    for k, ((a, b), t) in enumerate(zip(ex, times)):
        f.card(a, 36, b - a, 22, f"step {k % 4 + 3}<br>{t}", EXE[0], EXE[1], fs=S, radius=0)
    f.card(506, 36, 30, 22, i("t") + "+2 …", "#FFFFFF", DARK, fs=S, color=DARK)
    # latest observation -> next decision
    f.label(260, 2, 150, "latest observation feeds the next decision", fs=S, italic=True, color=DARK)
    seg(329, 11, 329, 35, color=DARK, sw=0.9)
    # notes
    # generated sequence at decision t
    f.label(76, 80, 40, "plan at<br>decision " + i("t"), fs=S, italic=True, color=NOTE, align="left")
    CW = 24; X0 = 118; CY = 82; CH = 18
    # zoom: executed steps 3–6 are the four flight segments 0–1.2 s
    f.poly([(152, 58), (312, 58), (X0 + 6 * CW, CY), (X0 + 2 * CW, CY)], "#E8ECF4", None)
    seg(152, 58, X0 + 2 * CW, CY, color="#7A8496", sw=0.7, head=False, dash="dash")
    seg(312, 58, X0 + 6 * CW, CY, color="#7A8496", sw=0.7, head=False, dash="dash")
    for k in range(16):
        pal = ALI if k < 2 else EXE if k < 6 else EVA if k < 10 else OUT
        f.card(X0 + k * CW, CY, CW, CH, str(k + 1), pal[0], pal[1], fs=S, radius=0, lw=0.8)
    bracket(X0 + 2 * CW, X0 + 6 * CW, 103)
    f.label(X0 + 6 * CW + 3, 100, 120, "<b>executed prefix</b> (steps 3–6)", fs=S, align="left", color=DARK)
    bracket(X0 + 2 * CW, X0 + 10 * CW, 113)
    f.label(X0 + 10 * CW + 3, 110, 140, "<b>planning window</b> (steps 3–10)", fs=S, align="left", color=DARK)
    bracket(X0, X0 + 16 * CW, 123)
    f.label(X0 + 16 * CW + 3, 120, 160, "<b>generated sequence</b> (16 steps × 0.3 s)", fs=S, align="left", color=DARK)

    # ============ layer 2: denoising (inside decision t) ============
    f.rect(2, 152, 714, 150, *PANEL, radius=6)
    side(156, 142, "2", "Denoising<br>layer", "inside decision " + i("t") + ";<br>no flight time", ("#EEF2F8", None))
    note(84, 156, 360, i("K") + " = 10 steps; post-training samples Gaussian transitions " + i("π") + "<sub>" + i("θ") + "</sub>(" + i("Z") + "<sup>" + i("k") + "−1</sup> | " + i("Z") + "<sup>" + i("k") + "</sup>, " + i("c") + "<sub>" + i("t") + "</sub>); evaluation uses deterministic DDIM", align="center", color=DARK)
    NY = 192; R = 10
    nodes = [(150, "10"), (205, "9"), (295, "2"), (350, "1"), (405, "0")]
    f.label(130, 170, 40, "high noise", fs=S, italic=True, color=NOTE)
    f.label(385, 170, 40, "output", fs=S, italic=True, color=DARK)
    for x, k in nodes:
        last = k == "0"
        f.oval(x, NY, R, fill="#DBE3EF" if last else "#FFFFFF", line=DARK if last else "#95A9CE", lw=1.2 if last else 0.9,
               html=i("Z") + "<sup>" + k + "</sup>", fs=F, color=DARK)
    f.label(238, NY - 7, 24, "…", fs=F, color=DARK)
    mids = []
    for (xa, _), (xb, _) in zip(nodes[:-1], nodes[1:]):
        if xb - xa > 60:
            seg(xa + R, NY, 236, NY, sw=1.0); seg(264, NY, xb - R, NY, sw=1.0)
            mids.append(250)
        else:
            seg(xa + R, NY, xb - R, NY, sw=1.0)
            mids.append((xa + xb) / 2)
    # condition bus into every transition
    f.card(80, 222, 62, 26, "condition " + i("c") + "<sub>" + i("t") + "</sub><br>(3 frames)", COND[0], COND[1], fs=S, color="#8A4B22")
    seg(142, 235, mids[-1] - 4, 235, color="#D9925E", sw=0.9, head=False)
    for m in mids:
        seg(m - 4, 235, m - 4, NY + 3, color="#D9925E", sw=0.9)
    # output sequence
    seg(415, NY, 440, NY, color=DARK, sw=1.2)
    f.label(440, 168, 256, "action sequence (16 × 11)", fs=S, color=DARK, bold=True)
    for k in range(16):
        pal = ALI if k < 2 else EXE if k < 6 else EVA if k < 10 else OUT
        f.card(440 + k * 16, NY - 8, 16, 16, str(k + 1), pal[0], pal[1], fs=S, radius=0, lw=0.8)
    note(440, 204, 256, "same sequence as in layer 1", align="center")

    # ---- post-training only: advantage credit and ratio (DPPO, ref. [13]) ----
    f.rect(76, 262, 634, 36, TPANEL[0], TPANEL[1], radius=4, dashed=True, lw=0.8)
    f.label(82, 264, 120, "<i>post-training only</i>", fs=S, color=TXT, align="left")
    f.card(340, 271, 110, 20, "advantage Â<sub><i>t</i></sub> (GAE)", TR[0], TR[1], fs=S, color="#3A2F1E")
    note(456, 266, 250, "credit to step <i>j</i>: Ã<sub><i>t,j</i></sub> = <i>γ</i><sub><i>d</i></sub><sup><i>K</i>−<i>j</i>−1</sup>Â<sub><i>t</i></sub>, <i>γ</i><sub><i>d</i></sub> = 0.8 (closer to output, larger)", color=TXT)
    note(456, 279, 250, "per-step ratio <i>R</i><sub><i>t,j</i></sub> on the planning window → clipped PPO", color=TXT)
    BY = 270
    # credit trunk from Ã box up into the denoising layer, fanning out (thin -> thick)
    TX, TY = 400, 248
    seg(TX, BY - 1, TX, TY, color=AMB, sw=1.6, head=False)
    weights = [0.8 ** 9, 0.8 ** 8, 0.8 ** 4, 0.8 ** 1, 1.0]
    for m, wgt in zip(mids, weights):
        tx = m + 4
        f.curve((TX, TY), (TX, 226), (tx, 232), (tx, NY + 4), AMB, 0.5 + 2.0 * wgt, head=True)

    # legend
    LY = 308
    items = [(("#FFFFFF", DARK), "decision (policy inference)"), (EXE, "executed"), (EVA, "evaluated, not executed"), (OUT, "outside window"), (ALI, "aligned with history"),
             (COND, "condition"), (TR, "post-training only")]
    x = 12
    for pal, t in items:
        f.rect(x, LY, 8, 8, pal[0], pal[1], radius=0)
        f.label(x + 11, LY - 1, 140, t, fs=S, align="left")
        x += 11 + len(t) * 3.5 + 12
    return f
