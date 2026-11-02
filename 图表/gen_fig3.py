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
BLUE = "#4A7FE0"
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


BL = ("#8BB7F4", "#C8DEFF", "#6595D5", "#3871B3")
OR = ("#FF9D59", "#FFC59C", "#E96D29", "#C9541A")
# Figure 3: two-layer decision process (a) and receding-horizon timing (b); 190 x 70 mm
W, H = 718, 265
FN, TITLE = "Fig3.dc.html", "Figure 3 Two-layer decision process and receding-horizon execution"


def node(x, y, html, pal=BLUEB, r=13):
    raw(f'<div style="position: absolute; left: {x - r}px; top: {y - r}px; width: {2*r}px; height: {2*r}px; box-sizing: border-box; border-radius: 50%; '
        f'background: {pal[0]}; border: 1px solid {pal[1]}; display: flex; align-items: center; justify-content: center; font-size: 7.5px; line-height: 1"><span>{html}</span></div>')


def Z(t, k):
    return i("Z") + "<sub>" + t + "</sub><sup>" + k + "</sup>"


# ================= (a) two-layer decision process =================
band(8, 8, 702, 140, "#EEF6F1", "#7FB09A", radius=8)
ttl(8, 11, 702, "(a) Two-layer Decision Process")
label(410, 13, 296, "environment MDP: one step = one decision " + i("t") + " (generate, execute H4, receive " + i("r<sub>t</sub>") + ")", fs=S, align="right", color="#4A5563")


def decision(x0, t, tlabel):
    band(x0, 30, 330, 76, "#ffffff", "#BCD5C9", radius=4)
    label(x0 + 6, 32, 80, "<b>Decision " + tlabel + "</b>", align="left")
    bx(x0 + 8, 58, 28, 22, i("c<sub>" + t + "</sub>"), GREENB)
    band(x0 + 46, 44, 194, 56, "#F7FBFF", "#9DB7D6", radius=4, dashed=True)
    label(x0 + 46, 45, 194, "denoising MDP, " + i("K") + " = 10 DDIM steps", fs=S, color="#3D5A80")
    seg(x0 + 37, 69, x0 + 51, 69)
    xs_ = [x0 + 66, x0 + 106, x0 + 146, x0 + 182, x0 + 222]
    labs_ = [Z(i(t), i("K")), Z(i(t), i("K") + "−1"), "⋯", Z(i(t), "1"), Z(i(t), "0")]
    for j_, (xx_, lb) in enumerate(zip(xs_, labs_)):
        if lb == "⋯":
            label(xx_ - 10, 63, 20, "⋯", fs=T)
        else:
            node(xx_, 72, lb, ORB if j_ == 4 else BLUEB)
    for a_, b_ in zip(xs_[:-1], xs_[1:]):
        seg(a_ + 13, 72, b_ - 13, 72, sw=1)
    label(x0 + 46, 87, 194, "each step: Gaussian transition, tractable log-probability", fs=S, italic=True, color="#4A5563")
    seg(x0 + 235, 72, x0 + 251, 72)
    bx(x0 + 252, 58, 70, 28, "Execute H4<br>(4 × 0.3 s)", REDB)
    return xs_


xa = decision(14, "t", i("t"))
xb = decision(372, "t+1", i("t") + "+1")
seg(337, 72, 371, 72)
label(338, 56, 32, i("r<sub>t</sub>"))
label(336, 78, 36, "new obs.", fs=S, color="#4A5563")
label(702, 62, 8, "⋯", fs=T)
# PPO strip
bx(14, 116, 690, 26, "<b>Clipped PPO on every denoising transition</b> (" + i("t") + ", " + i("j") + "): probability ratio from per-step log-probabilities, advantage "
   + i("Ã<sub>t,j</sub>") + " = " + i("γ") + "<sub>d</sub><sup>" + i("K") + "−" + i("j") + "−1</sup> Norm(" + i("Â<sub>t</sub>") + "); updates LoRA only", ("#ECF2CD", "#987019"))
for xs_ in (xa, xb):
    for xx_ in (xs_[0] + 20, xs_[1] + 20, xs_[3] + 20):
        seg(int(xx_), 100, int(xx_), 115, color="#7A8F3A", sw=0.9, dash="2 1.5")

# ================= (b) receding-horizon execution =================
band(8, 156, 702, 101, "#EAF6FC", "#4AA8D8", radius=8)
ttl(8, 159, 702, "(b) Receding-horizon Execution")
CW = 18
X0 = 100


def cells(x0, y0, idx=True):
    out = []
    for j in range(16):
        fi, bo = (("#BFC2C3", "#6B6E70") if j < 2 else ("#4AD3D5", "#009AA6") if j < 6 else ("#B0CEFA", "#5D88C2") if j < 10 else ("#FFFFFF", "#888888"))
        out.append(f'<rect x="{j * CW}" y="0" width="{CW}" height="13" fill="{fi}" stroke="{bo}" stroke-width="0.6"/>')
        if idx and j in (0, 2, 6, 10, 15):
            out.append(f'<text x="{j * CW + CW / 2}" y="9.5" font-size="7.5" text-anchor="middle" fill="#1f2328" font-family="Tinos, serif">{j}</text>')
    raw(f'<svg width="{16 * CW}" height="13" viewBox="0 0 {16 * CW} 13" role="img" aria-label="sixteen-step predicted sequence" style="position: absolute; left: {x0}px; top: {y0}px; width: {16 * CW}px; height: 13px; overflow: visible">' + "".join(out) + "</svg>")


label(16, 193, 80, "<b>Decision " + i("t") + "</b>", align="left")
cells(X0, 193)
# brackets
raw(f'<svg width="{16 * CW}" height="40" viewBox="0 0 {16 * CW} 40" aria-hidden="true" style="position: absolute; left: {X0}px; top: 183px; width: {16 * CW}px; height: 40px; overflow: visible">'
    f'<path d="M0 6 L0 3 L{16 * CW} 3 L{16 * CW} 6" stroke="#4A5563" stroke-width="0.7" fill="none"/>'
    f'<path d="M{2 * CW} 26 L{2 * CW} 29 L{6 * CW} 29 L{6 * CW} 26" stroke="#009AA6" stroke-width="0.9" fill="none"/>'
    f'<path d="M{2 * CW} 33 L{2 * CW} 37 L{10 * CW} 37 L{10 * CW} 33" stroke="#5D88C2" stroke-width="0.9" fill="none"/></svg>')
label(X0, 174, 16 * CW, "H16: full prediction (16 × 11)", fs=S)
label(X0 + 6 * CW + 4, 207, 120, "H4: executed, progress reward", fs=S, align="left", color="#007A84")
label(X0 + 10 * CW + 4, 216, 160, "H8: planning window, scored for risk " + i("ρ<sub>t</sub>"), fs=S, align="left", color="#3F6AA6")
label(16, 231, 80, "<b>Decision " + i("t") + "+1</b>", align="left")
cells(X0 + 4 * CW, 231, idx=False)
seg(X0 + 4 * CW + 2 * CW, 206, X0 + 4 * CW + 2 * CW, 245, color="#2E9A8A", sw=0.9, head=False, dash="2 2")
label(X0 + 6 * CW + 4, 245, 220, "replan after 1.2 s from new observations", fs=S, align="left", color="#1F7F72")
# legend + time axis on the right
for (lx, ly, fi, bo, tx) in ((470, 178, "#BFC2C3", "#6B6E70", "aligned, not executed"), (590, 178, "#4AD3D5", "#009AA6", "executed (H4)"),
                             (470, 190, "#B0CEFA", "#5D88C2", "planned only"), (590, 190, "#FFFFFF", "#888888", "outside H8")):
    swatch(lx, ly + 1, fi, bo)
    label(lx + 10, ly - 1, 110, tx, fs=S, align="left")
ax = ['<path d="M0 10 L194 10" stroke="#4A5563" stroke-width="0.8" fill="none"/><path d="M192 8 L196 10 L192 12 Z" fill="#4A5563"/>']
for n in range(9):
    xx_ = n * 23
    if n % 4 == 0:
        ax.append(f'<path d="M{xx_} 6 L{xx_ + 4} 10 L{xx_} 14 L{xx_ - 4} 10 Z" fill="#1F7F72"/>')
    else:
        ax.append(f'<circle cx="{xx_}" cy="10" r="2.2" fill="#4A5563"/>')
    ax.append(f'<text x="{xx_}" y="24" font-size="7.5" text-anchor="middle" fill="#1f2328" font-family="Tinos, serif">{n * 0.3:.1f}</text>')
ax.append('<text x="199" y="13" font-size="7.5" fill="#1f2328" font-family="Tinos, serif">time (s)</text>')
raw('<svg width="230" height="26" viewBox="0 0 230 26" role="img" aria-label="observations every 0.3 s, replanning every 1.2 s" style="position: absolute; left: 478px; top: 216px; width: 230px; height: 26px; overflow: visible">' + "".join(ax) + "</svg>")
raw('<svg width="8" height="8" viewBox="0 0 8 8" aria-hidden="true" style="position: absolute; left: 470px; top: 247px; width: 8px; height: 8px"><circle cx="4" cy="4" r="2.2" fill="#4A5563"/></svg>')
label(480, 245, 90, "observe every 0.3 s", fs=S, align="left")
raw('<svg width="8" height="8" viewBox="0 0 8 8" aria-hidden="true" style="position: absolute; left: 576px; top: 247px; width: 8px; height: 8px"><path d="M4 0 L8 4 L4 8 L0 4 Z" fill="#1F7F72"/></svg>')
label(586, 245, 110, "replan every 1.2 s", fs=S, align="left")
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
