"""Generate project/Main.dc.html (Figure 1) for the Design canvas.
Canvas 718x404 px = 190x107 mm at 96 px/in. Body text 7 pt = 9.33 px."""
import json, os

ROOT = "/home/claude/figdesign/root/project"
os.makedirs(ROOT, exist_ok=True)

A = {
    "drone": "/_blob/6fb6a1fbb210442fc20eb36d9d510346",
    "pc": "/_blob/d15f94499e964d7038eaa5d1f2e15735",
    "three": "/_blob/a646c67ce9be84e224eae73c3fed3463",
    "env": "/_blob/f64253a3a18a5c9292a5f2bb1feb0676",
    "noisy": "/_blob/aff9bc8c320638e461d94abc1100d791",
}
W, H = 718, 404
F, T, S = "9.33px", "10.67px", "8px"   # 7 pt, 8 pt, 6 pt
INK = "#1f2328"
BLUE = "#6A84AE"
ORANGE = "#E96D29"

bands, arrows, cards, labels = [], [], [], []
_mid = [0]


def seg(x1, y1, x2, y2, color=BLUE, sw=1.2, head=True, dash=None):
    """One straight horizontal/vertical segment, tail (x1,y1) -> tip (x2,y2)."""
    _mid[0] += 1
    h = 2 * sw if head else 0
    style_extra = f" stroke-dasharray: {dash};" if dash else ""
    defs = ""
    mk = ""
    if head:
        mid = f"dc-arrow-head-filled-{_mid[0]}"
        defs = (f'<defs><marker id="{mid}" orient="auto" markerWidth="5" markerHeight="5" refX="2" refY="2" overflow="visible">'
                f'<path d="M0 0 L4 2 L0 4 Z" fill="{color}" stroke="none" style="stroke: none; fill: {color}; fill: context-stroke"/></marker></defs>')
        mk = f' marker-end="url(#{mid})"'
    if y1 == y2:  # horizontal
        n = abs(x2 - x1)
        left, top = min(x1, x2), y1 - 4
        d = f"M 0 4 L {n - h} 4" if x2 > x1 else f"M {n} 4 L {h} 4"
        w_, h_ = n, 8
    else:
        n = abs(y2 - y1)
        left, top = x1 - 4, min(y1, y2)
        d = f"M 4 0 L 4 {n - h}" if y2 > y1 else f"M 4 {n} L 4 {h}"
        w_, h_ = 8, n
    arrows.append(
        f'<svg width="{w_}" height="{h_}" viewBox="0 0 {w_} {h_}" preserveAspectRatio="none" aria-hidden="true" '
        f'style="position: absolute; left: {left}px; top: {top}px; width: {w_}px; height: {h_}px; overflow: visible; fill: none; '
        f'stroke: {color}; stroke-width: {sw}; stroke-linecap: round; stroke-linejoin: round;{style_extra}">'
        f'{defs}<path d="{d}"{mk}></path></svg>')


def card(x, y, w, h, html, fill="#ffffff", border="#8a8f98", fs=F, top=False, radius=3, dashed=False,
         bold=False, color=INK, clip=None, lh="1.18"):
    b = "none" if clip else f"1px {'dashed' if dashed else 'solid'} {border}"
    al = "flex-start" if top else "center"
    pad = "3px 3px" if not top else "3px 3px 0 3px"
    cp = f" clip-path: {clip};" if clip else ""
    fw = " font-weight: 700;" if bold else ""
    cards.append(
        f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; box-sizing: border-box; '
        f'padding: {pad}; display: flex; align-items: {al}; justify-content: center; text-align: center; '
        f'background: {fill}; border: {b}; border-radius: {radius}px; font-size: {fs}; line-height: {lh}; color: {color};{fw}{cp}">'
        f'<span>{html}</span></div>')


def band(x, y, w, h, fill, border, radius=6, dashed=False):
    bands.append(f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; box-sizing: border-box; '
                 f'background: {fill}; border: 1px {"dashed" if dashed else "solid"} {border}; border-radius: {radius}px"></div>')


def label(x, y, w, html, fs=F, align="center", bold=False, color=INK, italic=False, lh="1.18"):
    st = (f"position: absolute; left: {x}px; top: {y}px; width: {w}px; font-size: {fs}; line-height: {lh}; "
          f"text-align: {align}; color: {color};")
    if bold:
        st += " font-weight: 700;"
    if italic:
        st += " font-style: italic;"
    labels.append(f'<div style="{st}">{html}</div>')


def img(x, y, w, h, key, alt):
    labels.append(f'<img src="{A[key]}" alt="{alt}" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; object-fit: contain">')


def raw(html):
    labels.append(html)


i = lambda s: f"<i>{s}</i>"

# Figure 1, v4: Enhancing / ML-paper style (tinted panels, centred titles, gradient blocks, draw.io palette)
TT = "12px"          # panel titles (9 pt)
BLUEB = ("#DAE8FC", "#6C8EBF")
GREENB = ("#D5E8D4", "#82B366")
YELB = ("#FFF2CC", "#D6B656")
ORB = ("#FFE6CC", "#D79B00")
REDB = ("#F8CECC", "#B85450")
FAT = "#7EA6E0"


def ttl(x, y, w, text, fs=TT):
    label(x, y, w, f"<b>{text}</b>", fs=fs)


def fat(x, y, w, h, direction):
    if direction == "right":
        pts = f"0,{h*0.28} {w*0.55},{h*0.28} {w*0.55},0 {w},{h/2} {w*0.55},{h} {w*0.55},{h*0.72} 0,{h*0.72}"
    else:
        pts = f"{w},{h*0.28} {w*0.45},{h*0.28} {w*0.45},0 0,{h/2} {w*0.45},{h} {w*0.45},{h*0.72} {w},{h*0.72}"
    raw(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; overflow: visible">'
        f'<polygon points="{pts}" fill="{FAT}"/></svg>')


def lock(x, y):
    raw(f'<svg width="7" height="9" viewBox="0 0 7 9" role="img" aria-label="frozen" style="position: absolute; left: {x}px; top: {y}px; width: 7px; height: 9px; overflow: visible">'
        '<path d="M1.6 4 V2.6 A1.9 1.9 0 0 1 5.4 2.6 V4" stroke="#2E3B4E" stroke-width="0.9" fill="none"/>'
        '<rect x="0.5" y="4" width="6" height="4.6" rx="0.8" fill="#2E3B4E"/></svg>')


def trap(x, y, w, h, g1, g2, gid, text):
    raw(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; overflow: visible">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient></defs>'
        f'<polygon points="0,0 {w},{h*0.2} {w},{h*0.8} 0,{h}" fill="url(#{gid})" stroke="{g2}" stroke-width="0.6"/></svg>')
    lk = ('<svg width="7" height="9" viewBox="0 0 7 9" role="img" aria-label="frozen" style="display: inline-block; vertical-align: -1px; margin-left: 2px; width: 7px; height: 9px">'
          '<path d="M1.6 4 V2.6 A1.9 1.9 0 0 1 5.4 2.6 V4" stroke="#2E3B4E" stroke-width="0.9" fill="none"/>'
          '<rect x="0.5" y="4" width="6" height="4.6" rx="0.8" fill="#2E3B4E"/></svg>')
    col = "#10301A" if "MLP" in text else "#08303A"
    raw(f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; display: flex; align-items: center; justify-content: center; '
        f'text-align: center; font-size: {F}; line-height: 1.18; color: {col}"><span>{text}{lk}</span></div>')


def swatch(x, y, fi, bo):
    raw(f'<div style="position: absolute; left: {x}px; top: {y}px; width: 7px; height: 7px; box-sizing: border-box; background: {fi}; border: 1px solid {bo}"></div>')


def bx(x, y, w, h, html, pal, fs=F, dashed=False, bold=False):
    card(x, y, w, h, html, fill=pal[0], border=pal[1], fs=fs, dashed=dashed, bold=bold, radius=3)


Zk = lambda sup: i("Z") + "<sub>" + i("t") + "</sub><sup>" + sup + "</sup>"


def cube(x, y, w, h, d, front, top, side, stroke):
    return (f'<rect x="{x}" y="{y + d}" width="{w}" height="{h}" fill="{front}" stroke="{stroke}" stroke-width="0.6"/>'
            f'<path d="M{x} {y + d} L{x + d} {y} L{x + w + d} {y} L{x + w} {y + d} Z" fill="{top}" stroke="{stroke}" stroke-width="0.6"/>'
            f'<path d="M{x + w} {y + d} L{x + w + d} {y} L{x + w + d} {y + h} L{x + w} {y + h + d} Z" fill="{side}" stroke="{stroke}" stroke-width="0.6"/>')


BL = ("#B9CCE8", "#DCE6F3", "#93AED6", "#6F8BBA")
OR = ("#F2C3A0", "#F8DCC7", "#E0A77E", "#C98A5E")
# Figure 3 v2: (a) receding-horizon execution, common to deployment and rollouts;
#              (b) post-training only: two-layer MDP and denoising credit assignment.
W, H = 718, 338
FN, TITLE = "Fig3.dc.html", "Figure 3 Execution and DPPO post-training"

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


def shade(n):
    return C_EX if n < 4 else (C_H8 if n < 8 else C_RS)


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

# ======================= (a) execution =======================
band(8, 8, 702, 122, *PANEL, radius=8)
ttl(8, 11, 702, "(a) Receding-Horizon Execution (deployment and training rollouts)")
# one decision
card(18, 52, 56, 34, "observation<br>" + i("o<sub>t</sub>") + " (3 frames)", fill=COND[0], border=COND[1], fs=S)
seg(75, 69, 87, 69, color=LINE)
card(88, 48, 64, 42, "<b>policy " + i("π<sub>θ</sub>") + "</b><br>" + i("K") + " = 10 DDIM<br>steps", fill="#FFFFFF", border="#4F6FA3", fs=S)
seg(153, 69, 165, 69, color=LINE)
CX0, CW = 166, 9
for n in range(16):
    cell(CX0 + n * CW, 63, 8, 12, shade(n))
for n in (0, 3, 7, 15):
    label(CX0 + n * CW - 4, 77, 16, str(n), fs="7px", color="#3A4452")
E = lambda n: CX0 + n * CW + 8
bracket(CX0, E(15), 36)
bracket(CX0, E(7), 46)
bracket(CX0, E(3), 56)
label(CX0, 25, E(15) - CX0, "H16: planned trajectory (16 × 0.3 s)", fs=S)
label(E(7) + 3, 41, 70, "H8: risk window", fs=S, align="left")
label(E(3) + 3, 51, 70, "H4: executed", fs=S, align="left", bold=True, color="#2E4A73")
note(CX0, 89, 150, "one cell = one 0.3 s waypoint segment", align="left")

# timeline of repeated decisions
X0, TW = 360, 18          # px per 0.3 s
rows = [(X0, 40), (X0 + 72, 56), (X0 + 144, 72)]
for r, (rx, ry) in enumerate(rows):
    for n in range(16):
        x = rx + n * TW
        if x + TW > 698:
            break
        op = 1.0 if (n < 4 or r == 2) else 0.4
        cell(x, ry, TW - 1, 11, shade(n), op)
    seg(rx, 99, rx, ry + 12, color="#4F6FA3", sw=0.8, head=False, dash="2 1.5")
# zoom from the single decision to the first row
svgpath(f"M{E(15) + 2} 63 L{X0 - 2} 46", "#7A8496", 0.8, head=False, dash="3 2")
# time axis
seg(352, 104, 704, 104, color="#4A5563", sw=0.9)
for k in range(0, 19):
    x = X0 + k * TW
    if x > 696:
        break
    tall = 4 if k % 4 == 0 else 2
    raw(f'<div style="position: absolute; left: {x - 0.4}px; top: {104 - tall}px; width: 0.8px; height: {2*tall}px; background: #4A5563"></div>')
for k, t in enumerate(["0", "1.2", "2.4", "3.6"]):
    label(X0 + 72 * k - 12, 109, 24, t, fs=S)
label(674, 109, 32, "time (s)", fs=S, align="right")
for k in range(3):
    diamond(X0 + 72 * k, 104)
# executed path along the axis
raw(f'<div style="position: absolute; left: {X0}px; top: 91px; width: {216}px; height: 3px; background: #6E8DBE; border-radius: 1.5px"></div>')
note(X0 + 220, 86, 110, "flown path: executed H4 segments")
note(X0 + 214, 27, 130, "faded: discarded at replan")
label(330, 118, 100, "", fs=S)
note(X0 + 2, 116, 200, "◆ replan every 1.2 s · ticks: new observation every 0.3 s", align="left")

# ======================= (b) post-training =======================
band(8, 138, 702, 180, *TPANEL, radius=8)
ttl(8, 141, 702, "(b) Post-Training Only: Two-Layer MDP and Denoising Credit Assignment")
# left: two-layer MDP
band(16, 160, 508, 150, "#FFFFFF", "#D8C6A6", radius=4, dashed=True)
note(22, 168, 34, "outer<br>MDP", color=AINK)
note(22, 222, 34, "inner<br>MDP", color=AINK)
# outer row
card(58, 166, 40, 20, i("s<sub>t</sub>"), fill=COND[0], border=COND[1], fs=F)
card(430, 166, 40, 20, i("s<sub>t</sub>") + "<sub>+1</sub>", fill=COND[0], border=COND[1], fs=F)
seg(78, 187, 78, 216, color=LINE)
note(82, 196, 20, i("c<sub>t</sub>"))
# inner chain
CY, R = 228, 11
xs = [78, 152, 222, 292, 366]
circ(xs[0], CY, R, Zs(i("K")), ("#FFFFFF", "#8EA7CF"))
circ(xs[1], CY, R, Zs(i("K") + "−1"), ("#F2F6FB", "#8EA7CF"))
label(xs[2] - 12, CY - 7, 24, "⋯", fs=F)
circ(xs[3], CY, R, Zs("1"), ("#DCE6F3", "#7F9CC8"))
circ(xs[4], CY, R, Zs("0"), OUTC, bold=True)
for a, b in ((0, 1), (1, 2), (2, 3), (3, 4)):
    x1 = xs[a] + (R if a != 2 else 10) + 1
    x2 = xs[b] - (R if b != 2 else 10) - 1
    seg(x1, CY, x2, CY, color=LINE)
label(168, CY - 34, 150, i("π<sub>θ</sub>") + "(" + Zs(i("k") + "−1") + " | " + Zs(i("k")) + ", " + i("c<sub>t</sub>") + ")", fs=S, align="left")
note(168, CY - 20, 150, "Gaussian step, tractable log-prob")
note(xs[2] - 30, CY + 13, 60, i("K") + " = 10 steps", align="center")
# Z0 -> execute -> s_{t+1}
seg(xs[4], CY - R, xs[4], 176, color=LINE, head=False)
seg(xs[4], 176, 429, 176, color=LINE)
note(xs[4] + 4, 186, 70, "execute H4")
# reward to the right column
seg(471, 176, 579, 176, color=ALINE)
label(488, 163, 80, i("r<sub>t</sub>"), fs=S, bold=True, color=AINK)
# right: credit-assignment pipeline
PX, PW = 580, 122
card(PX, 164, PW, 24, "<b>reward " + i("r<sub>t</sub>") + "</b><br>H4 progress + H8 risk", fill=TB1[0], border=TB1[1], fs=S, color=AINK)
seg(PX + PW // 2, 189, PX + PW // 2, 197, color=ALINE)
card(PX, 198, PW, 22, "critic " + i("V<sub>φ</sub>") + " + GAE → " + i("Â<sub>t</sub>"), fill=TB1[0], border=TB1[1], fs=S, color=AINK)
note(PX - 54, 205, 52, i("V<sub>φ</sub>") + " ← returns", align="right", color=AINK)
seg(PX + PW // 2, 221, PX + PW // 2, 229, color=ALINE)
card(PX, 230, PW, 22, "<b>denoising discount</b> " + i("γ<sub>d</sub>") + "<sup><i>K</i>−<i>j</i>−1</sup>", fill=TB2[0], border=TB2[1], fs=S, color=AINK)
seg(PX + PW // 2, 253, PX + PW // 2, 261, color=ALINE)
card(PX, 261, PW, 25, "clipped PPO on " + i("R<sub>t,j</sub>") + "<br>+ λ" + i("L") + "<sub>keep</sub> (stage 2)", fill=TB1[0], border=TB1[1], fs=S, color=AINK)
seg(PX + PW // 2, 287, PX + PW // 2, 294, color=ALINE)
card(PX, 295, PW, 16, "<b>update LoRA only</b> · " + i("W") + "<sub>0</sub>" + lk, fill=LORA[0], border=LORA[1], fs=S, color="#7A4E2E")
# credit arcs: thin (early denoising step) -> thick (final step)
mids = [(xs[0] + xs[1]) / 2, (xs[1] + xs[2]) / 2 + 4, (xs[2] + xs[3]) / 2 - 4, (xs[3] + xs[4]) / 2]
widths = [0.6, 1.0, 1.4, 1.9]
jl = ["0", "1", i("K") + "−2", i("K") + "−1"]
BUS = 278
seg(PX - 1, 241, 540, 241, color=ALINE, sw=1.0, head=False)
seg(540, 241, 540, BUS, color=ALINE, sw=1.0, head=False)
seg(540, BUS, int(mids[0]), BUS, color=ALINE, sw=1.0, head=False)
for m, w_, t in zip(mids, widths, jl):
    seg(int(m), BUS, int(m), CY + 4, color=ALINE, sw=w_)
    label(int(m) + 4, CY + 22, 30, i("j") + "=" + t, fs="7px", color=AINK, align="left")
label(60, BUS + 6, 460, i("Ã<sub>t,j</sub>") + " = " + i("γ<sub>d</sub>") + "<sup><i>K</i>−<i>j</i>−1</sup>" + i("Â<sub>t</sub>") + " · line width = credit: later denoising steps receive more", fs=S, color=AINK)

# legend
for (lx, kind, tx) in ((16, "lock", "frozen"), (70, LORA, "trainable LoRA"), (152, C_EX, "executed segment (H4)"),
                       (270, ("#FBF6EE", "#CDB089"), "post-training only (not run at deployment)")):
    if kind == "lock":
        lock(lx, 324)
    else:
        swatch(lx, 325, kind[0], kind[1])
    label(lx + 10, 323, 220, tx, fs=S, align="left")
body = "\n".join(bands + arrows + cards + labels)
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{TITLE}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Tinos:ital,wght@0,400;0,700;1,400;1,700&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#2F5FC4}}a:hover{{color:#1d3f8a}}
</style>
</helmet>
<div style="position: relative; width: {W}px; height: {H}px; background: #ffffff; font-family: 'Tinos', 'Times New Roman', serif; color: {INK}; overflow: hidden">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
open(os.path.join(ROOT, FN), "w", encoding="utf-8").write(html)
