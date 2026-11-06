"""Figure 4 (two-layer decision, receding-horizon execution and credit assignment), native PowerPoint shapes.
Three-layer layout after the user's reference; content follows 论文大稿_v3 §3.4–3.5 and the code facts in
2026-11-03 交接 §4.3 (2 aligned steps, H4 = steps 3–6, H8 = steps 3–10, ratio on H8, γ_d = 0.8, K = 10)."""
from pp import Fig

S = 8; F = 9.33
PANEL = ("#F7F9FC", "#A9BEDD"); TPANEL = ("#FBF6EE", "#CDB089")
EXE = ("#8EA7CF", "#6E8DBE"); EVA = ("#C9D8EC", "#8EA7CF"); OUT = ("#F4F7FB", "#C9D8EC"); ALI = ("#E3E6EA", "#AEB4BD")
COND = ("#E7E0F4", "#8E7CC3"); TR = ("#F6EBDA", "#C49E6C"); TR2 = ("#EDD9BC", "#B88A52")
DARK = "#2E4A73"; GREY = "#5A6B85"; AMB = "#B88A52"; NOTE = "#5A6270"; TXT = "#6B5434"
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
    side(6, 138, "1", "Environment<br>layer", "physical time", ("#EAF0F8", None))
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
    note(548, 20, 166, "new observation after every 0.3 s segment")
    note(548, 31, 166, "replan after 4 segments (every 1.2 s)")
    note(548, 42, 166, "arrival or collision ends the episode early")
    # generated sequence at decision t
    f.label(76, 80, 40, "plan at<br>decision " + i("t"), fs=S, italic=True, color=NOTE, align="left")
    CW = 24; X0 = 118; CY = 82; CH = 18
    # zoom: executed steps 3–6 are the four flight segments 0–1.2 s
    f.poly([(152, 58), (312, 58), (X0 + 6 * CW, CY), (X0 + 2 * CW, CY)], "#E6EDF7", None)
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
    note(548, 80, 166, "steps 1–2 align with the two past frames;<br>the unexecuted tail is regenerated<br>at the next decision")

    # ============ layer 2: denoising (inside decision t) ============
    f.rect(2, 152, 714, 110, *PANEL, radius=6)
    side(156, 102, "2", "Denoising<br>layer", "inside decision " + i("t") + ";<br>no flight time", ("#EAF0F8", None))
    note(84, 156, 360, i("K") + " = 10 steps; post-training samples Gaussian transitions " + i("π") + "<sub>" + i("θ") + "</sub>(" + i("Z") + "<sup>" + i("k") + "−1</sup> | " + i("Z") + "<sup>" + i("k") + "</sup>, " + i("c") + "<sub>" + i("t") + "</sub>); evaluation uses deterministic DDIM", align="center", color=DARK)
    NY = 192; R = 10
    nodes = [(150, "10"), (205, "9"), (295, "2"), (350, "1"), (405, "0")]
    f.label(130, 170, 40, "high noise", fs=S, italic=True, color=NOTE)
    f.label(385, 170, 40, "output", fs=S, italic=True, color=DARK)
    for x, k in nodes:
        last = k == "0"
        f.oval(x, NY, R, fill="#C9D8EC" if last else "#FFFFFF", line=DARK if last else "#8EA7CF", lw=1.2 if last else 0.9,
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
    f.card(80, 222, 62, 26, "condition " + i("c") + "<sub>" + i("t") + "</sub><br>(3 frames)", COND[0], COND[1], fs=S, color="#4B3B78")
    seg(142, 235, mids[-1] - 4, 235, color="#8E7CC3", sw=0.9, head=False)
    for m in mids:
        seg(m - 4, 235, m - 4, NY + 3, color="#8E7CC3", sw=0.9)
    # output sequence
    seg(415, NY, 440, NY, color=DARK, sw=1.2)
    f.label(440, 168, 256, "action sequence (16 × 11)", fs=S, color=DARK, bold=True)
    for k in range(16):
        pal = ALI if k < 2 else EXE if k < 6 else EVA if k < 10 else OUT
        f.card(440 + k * 16, NY - 8, 16, 16, str(k + 1), pal[0], pal[1], fs=S, radius=0, lw=0.8)
    note(440, 204, 256, "same sequence as in layer 1", align="center")
    note(452, 230, 250, "credit " + i("γ") + "<sub>" + i("d") + "</sub><sup>" + i("K") + "−" + i("j") + "−1</sup>, " + i("γ") + "<sub>" + i("d") + "</sub> = 0.8: steps closer to the output receive more", color=TXT)

    # ============ layer 3: credit assignment and update (post-training only) ============
    f.rect(2, 266, 714, 120, *TPANEL, radius=6)
    side(270, 112, "3", "Credit<br>assignment", "post-training only", (TR[0], None))
    BY, BH = 312, 30; MY = BY + BH / 2
    # reward terms
    f.rect(77, 274, 76, 104, "#FFFFFF", "#C49E6C", radius=3, dashed=True)
    f.label(77, 276, 76, "<b>reward terms</b>", fs=S, color=TXT)
    for k, t in enumerate(["terminal reward", "progress reward", "risk penalty", "time penalty", "detour cost"]):
        f.card(82, 291 + k * 17, 66, 13, t, "#FBF6EE", "#D8C3A0", fs=S, radius=2, lw=0.8)
    seg(153, MY, 157, MY, color=AMB)
    boxes = [
        (158, 40, "reward<br>" + i("r") + "<sub>" + i("t") + "</sub>"),
        (206, 62, "critic " + i("V") + "<sub>" + i("φ") + "</sub>(" + i("c") + "<sub>" + i("t") + "</sub>, " + i("e") + "<sub>" + i("t") + "</sub>)<br>+ GAE"),
        (276, 46, "normalize<br>" + "Â<sub>" + i("t") + "</sub>"),
        (330, 86, "Ã<sub>" + i("t,j") + "</sub> = " + i("γ") + "<sub>" + i("d") + "</sub><sup>" + i("K") + "−" + i("j") + "−1</sup><br>× Norm(Â<sub>" + i("t") + "</sub>)"),
        (426, 58, "clipped PPO<br>loss " + i("L") + "<sub>π</sub>"),
    ]
    prev = None
    for x, w, t in boxes:
        f.card(x, BY, w, BH, t, TR[0], TR[1], fs=S, color="#3A2F1E")
        if prev:
            seg(prev, MY, x - 1, MY, color=AMB)
        prev = x + w
    # probability ratio of every denoising step, computed over the planning window, enters the PPO loss
    f.card(399, 352, 112, 24, "per-step ratio " + i("R") + "<sub>" + i("t,j") + "</sub><br>over the planning window", TR[0], TR[1], fs=S, color="#3A2F1E")
    seg(455, 352, 455, BY + BH + 1, color=AMB)
    # critic: separate value-loss update
    seg(255, BY + BH, 255, 352, color=AMB, sw=0.8, head=False)
    seg(255, 352, 222, 352, color=AMB, sw=0.8, head=False)
    seg(222, 352, 222, BY + BH + 1, color=AMB, sw=0.8)
    note(206, 354, 120, "value loss: critic " + i("φ") + " updated separately", color=TXT)
    # (+) with the stage-2 regularizer
    seg(484, MY, 494, MY, color=AMB)
    PX_ = 500
    f.plus(PX_, MY, r=6)
    f.rect(444, 271, 150, 25, "#FFFFFF", AMB, radius=3, dashed=True)
    f.label(444, 272, 150, "<b>Stage 2</b>: BC regularization on fixed<br>successful trajectories " + i("λL") + "<sub>reg</sub>", fs=S, color=TXT, h=22, anchor="middle")
    seg(PX_, 296, PX_, MY - 7, color=AMB)
    seg(PX_ + 6, MY, 515, MY, color=AMB)
    f.card(516, BY, 70, BH, "actor loss<br>" + i("L") + "<sub>π</sub> + " + i("λL") + "<sub>reg</sub>", TR[0], TR[1], fs=S, color="#3A2F1E")
    seg(586, MY, 594, MY, color=AMB)
    f.card(595, BY, 114, BH, "<b>update LoRA</b> " + i("θ") + "<br>(pretrained weights frozen)", TR2[0], TR2[1], fs=S, color="#3A2F1E", lw=1.2)
    note(516, 348, 196, "Stage 1: " + i("λ") + " = 0; Stage 2: " + i("λ") + " set once from gradient norms", color=TXT)

    # credit trunk from Ã box up into the denoising layer, fanning out (thin -> thick)
    TX, TY = 400, 252
    seg(TX, BY - 1, TX, TY, color=AMB, sw=1.6, head=False)
    weights = [0.8 ** 9, 0.8 ** 8, 0.8 ** 4, 0.8 ** 1, 1.0]
    for m, wgt in zip(mids, weights):
        tx = m + 4
        f.curve((TX, TY), (TX, 228), (tx, 236), (tx, NY + 4), AMB, 0.5 + 2.0 * wgt, head=True)

    # legend
    LY = 391
    items = [(("#FFFFFF", DARK), "decision (policy inference)"), (EXE, "executed"), (EVA, "evaluated, not executed"), (OUT, "outside window"), (ALI, "aligned with history"),
             (COND, "condition"), (TR, "post-training only")]
    x = 12
    for pal, t in items:
        f.rect(x, LY, 8, 8, pal[0], pal[1], radius=0)
        f.label(x + 11, LY - 1, 140, t, fs=S, align="left")
        x += 11 + len(t) * 3.5 + 12
    return f
