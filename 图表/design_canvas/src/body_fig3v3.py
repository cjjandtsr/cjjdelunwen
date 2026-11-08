# Figure 3 v3: three layers (environment, denoising, credit assignment)
W, H = 718, 426
FN, TITLE = "Fig3.dc.html", "Figure 3 Two-layer decision process, receding execution and credit assignment"
COND = ("#DCE6F3", "#6E8DBE")
FROZ = ("#FFFFFF", "#7F9CC8")
LORA = ("#F8DCC7", "#C98A5E")
OUTC = ("#EAF0F8", "#4F6FA3")
PANEL = ("#F7F9FC", "#A9BEDD")
TPANEL = ("#FBF6EE", "#CDB089")        # training panel (amber family, as Fig. 1)
TB1 = ("#F6EBDA", "#C49E6C")           # training block, light
TB2 = ("#EDD9BC", "#B88A52")           # training block, darker (key quantity)
NOTE = "#5A6270"
AINK = "#6B5434"                       # amber text
LINE = "#5A6B85"
ALINE = "#9C7A4C"
# cell shades: executed / risk window / rest of plan
C_EX = ("#8EA7CF", "#6E8DBE")
C_H8 = ("#C9D8EC", "#8EA7CF")
C_RS = ("#EEF3FA", "#B7C9E5")
lk = ('<svg width="7" height="9" viewBox="0 0 7 9" role="img" aria-label="frozen" style="display: inline-block; vertical-align: -1px; margin-left: 2px; width: 7px; height: 9px">'
      '<path d="M1.6 4 V2.6 A1.9 1.9 0 0 1 5.4 2.6 V4" stroke="#2E3B4E" stroke-width="0.9" fill="none"/><rect x="0.5" y="4" width="6" height="4.6" rx="0.8" fill="#2E3B4E"/></svg>')


def note(x, y, w, text, align="left", color=NOTE):
    label(x, y, w, text, fs=S, italic=True, color=color, align=align)


def cell(x, y, w, h, pal, op=1.0):
    raw(f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; box-sizing: border-box; '
        f'background: {pal[0]}; border: 0.8px solid {pal[1]}; opacity: {op}"></div>')


C_PA = ("#E3E6EA", "#A7AEB6")   # cells 0-1: overlap the observed history


def shade(n):
    return C_PA if n < 2 else C_EX if n < 6 else (C_H8 if n < 10 else C_RS)


def bracket(x1, x2, y, color="#4A5563"):
    raw(f'<svg width="{x2 - x1}" height="6" viewBox="0 0 {x2 - x1} 6" aria-hidden="true" style="position: absolute; left: {x1}px; top: {y}px; width: {x2 - x1}px; height: 6px; overflow: visible">'
        f'<path d="M0.5 5 V1 H{x2 - x1 - 0.5} V5" stroke="{color}" stroke-width="0.8" fill="none"/></svg>')


def diamond(x, y, s=5, fill="#4F6FA3"):
    raw(f'<svg width="{2*s}" height="{2*s}" viewBox="0 0 {2*s} {2*s}" aria-hidden="true" style="position: absolute; left: {x - s}px; top: {y - s}px; width: {2*s}px; height: {2*s}px; overflow: visible">'
        f'<path d="M{s} 0 L{2*s} {s} L{s} {2*s} L0 {s} Z" fill="{fill}" stroke="#ffffff" stroke-width="0.6"/></svg>')


def circ(cx, cy, r, html, pal, bold=False):
    fw = " font-weight: 700;" if bold else ""
    raw(f'<div style="position: absolute; left: {cx - r}px; top: {cy - r}px; width: {2*r}px; height: {2*r}px; box-sizing: border-box; border-radius: 50%; '
        f'background: {pal[0]}; border: 1px solid {pal[1]}; display: flex; align-items: center; justify-content: center; font-size: {S}; color: #1F3A63;{fw}"><span>{html}</span></div>')


def svgpath(d, color, sw, head=True, dash=None, op=1.0):
    _mid[0] += 1
    mid = f"f3arc{_mid[0]}"
    mk = (f'<defs><marker id="{mid}" orient="auto" markerWidth="5" markerHeight="5" refX="2" refY="2" markerUnits="userSpaceOnUse" overflow="visible">'
          f'<path d="M0 0 L4 2 L0 4 Z" fill="{color}"/></marker></defs>') if head else ""
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    me = f' marker-end="url(#{mid})"' if head else ""
    raw(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true" style="position: absolute; left: 0px; top: 0px; width: {W}px; height: {H}px; overflow: visible; pointer-events: none">'
        f'{mk}<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="none" stroke-linecap="round" opacity="{op}"{ds}{me}/></svg>')



Zs = lambda k: i("Z") + "<sup>" + k + "</sup>"
def ccell(x, y, w, h, pal, html, fs="7px", op=1.0, color="#1F3A63"):
    raw(f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; box-sizing: border-box; background: {pal[0]}; border: 0.8px solid {pal[1]}; opacity: {op}; '
        f'display: flex; align-items: center; justify-content: center; text-align: center; font-size: {fs}; line-height: 1.05; color: {color}"><span>{html}</span></div>')
KIND = lambda n: ("aligned", C_PA) if n <= 2 else ("exec", C_EX) if n <= 6 else ("eval", C_H8) if n <= 10 else ("outside", C_RS)

# ======================= (a) environment layer =======================
band(8, 8, 702, 132, *PANEL, radius=8)
label(16, 11, 600, "<b>(a) Environment Layer</b>: physical time, training rollouts", fs=TT, align="left")
X0, CWD = 170, 34                       # t = 0 and width of one 0.3 s segment
seg(140, 40, 706, 40, color="#4A5563", sw=0.9)
label(110, 33, 26, i("t") + " (s)", fs=S)
ticks = [(X0 + k * CWD, f"{0.3 * k:.1f}".rstrip("0").rstrip(".") if k else "0") for k in range(5)]
ticks += [(340 + k * CWD, f"{1.2 + 0.3 * k:.1f}") for k in range(1, 5)]
for x, t in ticks:
    label(x - 12, 27, 24, t, fs="7px")
    raw(f'<div style="position: absolute; left: {x - 2.5}px; top: 37.5px; width: 5px; height: 5px; border-radius: 50%; background: #4F6FA3"></div>')
label(14, 52, 84, "environment", fs=S, align="left", bold=True, color="#2E4A73")
ccell(136, 48, 34, 22, OUTC, "<b>decide</b><br>" + i("t"), fs="7px")
for k in range(4):
    ccell(X0 + k * CWD, 48, CWD, 22, C_EX, f"exec {k + 1}<br>{0.3 * k:.1f}–{0.3 * (k + 1):.1f} s".replace("0.0", "0"), fs="7px")
ccell(306, 48, 34, 22, OUTC, "<b>decide</b><br>" + i("t") + "+1", fs="7px")
for k in range(4):
    ccell(340 + k * CWD, 48, CWD, 22, C_EX, f"exec {k + 1}", fs="7px")
ccell(476, 48, 30, 22, ("#FFFFFF", "#B7C9E5"), i("t") + "+2 …", fs="7px")
note(516, 47, 190, "observation updated every 0.3 s (dots);<br>replan after 4 segments (1.2 s)")
note(516, 66, 190, "episode ends early on arrival or collision")
# generated sequence of decision t
label(14, 86, 84, "generated sequence<br>of decision " + i("t"), fs=S, align="left", bold=True, color="#2E4A73")
C1 = X0 - 2 * CWD
for n in range(1, 17):
    kind, pal = KIND(n)
    ccell(C1 + (n - 1) * CWD, 84, CWD, 22, pal, f"<b>{n}</b><br>{kind}", fs="7px")
SX = lambda n: C1 + (n - 1) * CWD
EX = lambda n: C1 + n * CWD
bracket(SX(3), EX(6), 109)
label(EX(6) + 3, 106, 70, "<b>H4</b> executed", fs="7px", align="left", color="#2E4A73")
bracket(SX(3), EX(10), 118)
label(EX(10) + 3, 115, 120, "<b>H8</b> planning window (3–10)", fs="7px", align="left")
bracket(SX(1), EX(16), 127)
label(SX(1), 129, EX(16) - SX(1), "<b>H16</b> generated (1–16)", fs="7px")
note(EX(16) + 4, 84, 58, "unexecuted tail is regenerated at " + i("t") + "+1", color=NOTE)

# ======================= (b) denoising layer =======================
band(8, 148, 702, 122, *PANEL, radius=8)
label(16, 151, 680, "<b>(b) Denoising Layer</b>: internal computation of decision " + i("t") + ", no flight time", fs=TT, align="left")
band(14, 168, 408, 96, "#FFFFFF", "#B9C3D0", radius=4, dashed=True)
note(110, 170, 300, i("K") + " = 10; stochastic denoising transitions during post-training", align="center")
CY, R = 204, 11
zx = [120, 176, 228, 280, 334, 390]
circ(zx[0], CY, R, Zs("10"), ("#FFFFFF", "#8EA7CF"))
circ(zx[1], CY, R, Zs("9"), ("#F2F6FB", "#8EA7CF"))
label(zx[2] - 12, CY - 7, 24, "⋯", fs=F)
circ(zx[3], CY, R, Zs("2"), ("#E3EBF6", "#8EA7CF"))
circ(zx[4], CY, R, Zs("1"), ("#DCE6F3", "#7F9CC8"))
circ(zx[5], CY, R, Zs("0"), OUTC, bold=True)
label(zx[0] - 30, 182, 60, "high noise", fs="7px", color=NOTE)
label(zx[5] - 34, 182, 68, "near clean", fs="7px", color="#2E4A73")
mids = []
for a, b in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5)):
    x1 = zx[a] + (R if a != 2 else 9) + 1
    x2 = zx[b] - (R if b != 2 else 9) - 1
    seg(x1, CY, x2, CY, color=LINE)
    mids.append((x1 + x2) // 2)
# condition into every transition
bx(22, 236, 70, 24, "condition " + i("c<sub>t</sub>") + "<br>(3 frames, 576)", COND, fs="7px")
seg(93, 248, mids[-1] - 5, 248, color="#6E8DBE", head=False)
for m in mids:
    seg(m - 5, 248, m - 5, CY + 3, color="#6E8DBE", sw=0.9)
# output sequence
seg(zx[5] + R + 1, CY, 446, CY, color="#4F6FA3")
label(446, 172, 256, "generated action sequence <b>H16</b>", fs=S, color="#2E4A73")
for n in range(1, 17):
    kind, pal = KIND(n)
    ccell(447 + (n - 1) * 16, CY - 8, 16, 16, pal, str(n), fs="7px")
note(447, 224, 256, "evaluation uses deterministic DDIM with the same 10 steps", align="center")
note(447, 248, 256, "closer to the output → larger credit (" + i("γ<sub>d</sub>") + " = 0.8)", align="center", color=AINK)

# ======================= (c) credit assignment =======================
band(8, 278, 702, 128, *TPANEL, radius=8)
label(16, 281, 320, "<b>(c) Credit Assignment</b>: post-training only", fs=TT, align="left")
band(16, 300, 90, 98, "#FFFFFF", "#CDB089", radius=4, dashed=True)
label(16, 302, 90, "<b>reward terms</b>", fs="7px", color=AINK)
for k_, t_ in enumerate(["terminal (arrival / failure)", "progress (H4)", "risk (H4 + H8 tail)", "time", "space (H4 path)"]):
    card(21, 314 + k_ * 16.5, 80, 13, t_, fill="#FBF6EE", border="#D8C6A6", fs="7px", color=AINK)
YB, HB = 336, 32
def tb(x, w, html, pal=TB1, bold=False):
    card(x, YB, w, HB, html, fill=pal[0], border=pal[1], fs="7px", color=AINK, bold=bold)
seg(107, YB + 16, 113, YB + 16, color=ALINE)
tb(114, 40, "reward<br>" + i("r<sub>t</sub>"))
seg(155, YB + 16, 161, YB + 16, color=ALINE)
tb(162, 70, "value " + i("V<sub>φ</sub>") + "(" + i("c<sub>t</sub>") + ", " + i("e<sub>t</sub>") + ")<br>+ GAE")
seg(233, YB + 16, 239, YB + 16, color=ALINE)
tb(240, 46, "normalize<br>" + i("Â<sub>t</sub>"))
seg(287, YB + 16, 293, YB + 16, color=ALINE)
tb(294, 98, i("Ã<sub>t,j</sub>") + " = " + i("γ<sub>d</sub>") + "<sup><i>K</i>−<i>j</i>−1</sup><br>· Norm(" + i("Â<sub>t</sub>") + ")", TB2)
seg(393, YB + 16, 399, YB + 16, color=ALINE)
tb(400, 52, "per-step ratio<br>" + i("R<sub>t,j</sub>"))
seg(453, YB + 16, 459, YB + 16, color=ALINE)
tb(460, 50, "clipped PPO<br>" + i("L") + "<sub>PPO</sub>")
seg(511, YB + 16, 516, YB + 16, color=ALINE)
raw(f'<svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true" style="position: absolute; left: 517px; top: {YB + 10}px; width: 12px; height: 12px; overflow: visible">'
    '<circle cx="6" cy="6" r="5.5" fill="#ffffff" stroke="#8E6A3E" stroke-width="0.9"/><path d="M6 2.2 V9.8 M2.2 6 H9.8" stroke="#8E6A3E" stroke-width="0.9"/></svg>')
seg(530, YB + 16, 537, YB + 16, color=ALINE)
tb(538, 66, "actor loss<br>" + i("L") + "<sub>PPO</sub> + λ" + i("L") + "<sub>keep</sub>")
seg(605, YB + 16, 611, YB + 16, color=ALINE)
card(612, YB, 92, HB, "<b>update LoRA</b> (" + i("θ") + ")<br>backbone frozen" + lk, fill=TB2[0], border=TB2[1], fs="7px", color=AINK)
# stage-2 retention
card(468, 297, 104, 24, "Stage 2: fixed successful-prefix<br>retention, " + "+λ" + i("L") + "<sub>keep</sub>", fill="#FFFFFF", border="#B88A52", fs="7px", color=AINK, dashed=True)
seg(523, 322, 523, YB + 9, color=ALINE)
# critic trained separately
seg(197, YB + HB, 197, 382, color=ALINE, head=False, dash="2 1.5")
seg(197, 382, 182, 382, color=ALINE, head=False, dash="2 1.5")
seg(182, 382, 182, YB + HB + 1, color=ALINE, dash="2 1.5")
note(202, 376, 200, "critic " + i("φ") + " updated separately (value loss on returns)", color=AINK)
# credit: one trunk from the advantage box, fanning out to every denoising transition
JX, JY = 372, 256
seg(JX, YB - 1, JX, JY, color="#9C7A4C", sw=2.2, head=False)
raw(f'<div style="position: absolute; left: {JX - 2.5}px; top: {JY - 2.5}px; width: 5px; height: 5px; border-radius: 50%; background: #9C7A4C"></div>')
widths = [0.6, 0.9, 1.3, 1.7, 2.2]
for m, w_ in zip(mids, widths):
    ex = m + 5
    svgpath(f"M{JX} {JY} C {JX - 0.35 * (JX - ex):.0f} {JY}, {ex} {JY - 8}, {ex} {CY + 4}", "#9C7A4C", w_)
note(JX - 114, 302, 110, i("Ã<sub>t,j</sub>") + " to each denoising step", align="right", color=AINK)
# legend
for lx, pal, tx in ((16, C_EX, "executed (H4)"), (110, C_H8, "evaluated only (H8 tail)"), (238, C_RS, "outside window"), (330, C_PA, "aligned with history"),
                    (446, COND, "condition"), (510, TPANEL, "post-training only")):
    swatch(lx, 413, pal[0], pal[1])
    label(lx + 10, 411, 130, tx, fs=S, align="left")
