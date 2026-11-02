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
# Figure 2: network architecture (190 x 70 mm = 718 x 265 px)
W, H = 718, 265
FN, TITLE = "Fig2.dc.html", "Figure 2 Network architecture"
ZB = i("Z̄") + "<sub>" + i("t") + "</sub><sup>" + i("k") + "</sup>"


def plus(x, y, r=6):
    raw(f'<svg width="{2*r}" height="{2*r}" viewBox="0 0 {2*r} {2*r}" aria-hidden="true" style="position: absolute; left: {x - r}px; top: {y - r}px; width: {2*r}px; height: {2*r}px; overflow: visible">'
        f'<circle cx="{r}" cy="{r}" r="{r - 0.5}" fill="#ffffff" stroke="#4A5563" stroke-width="0.9"/>'
        f'<path d="M{r} 2.5 L{r} {2*r - 2.5} M2.5 {r} L{2*r - 2.5} {r}" stroke="#4A5563" stroke-width="0.9"/></svg>')


def vbar(x, y, w, h, g1, g2, gid, stroke):
    raw(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; overflow: visible">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient></defs>'
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="2" fill="url(#{gid})" stroke="{stroke}" stroke-width="0.6"/></svg>')


# ================= (a) observation encoder =================
band(8, 8, 228, 122, "#EEF6F1", "#7FB09A", radius=8)
ttl(8, 11, 228, "(a) Observation Encoder (per frame)")
bx(14, 34, 46, 28, i("P<sub>τ</sub>") + "<br>4096 × 3", BLUEB)
seg(61, 48, 67, 48)
trap(68, 32, 62, 32, "#A9ECF7", "#2FB8D6", "f2pn", "Multi-stage<br>PointNet")
seg(131, 48, 137, 48)
vbar(138, 38, 8, 20, "#A9ECF7", "#2FB8D6", "f2b1", "#2FB8D6")
label(130, 27, 24, "128", fs=S)
bx(14, 78, 46, 26, i("s<sub>τ</sub>") + "<br>9", BLUEB)
seg(61, 91, 67, 91)
trap(68, 76, 62, 30, "#C6E79A", "#6FB43F", "f2mlp", "State MLP<br>9→64→64")
seg(131, 91, 137, 91)
vbar(138, 85, 8, 12, "#C6E79A", "#6FB43F", "f2b2", "#6FB43F")
label(130, 98, 24, "64", fs=S)
seg(147, 48, 152, 48, head=False)
seg(147, 91, 152, 91, head=False)
seg(152, 48, 152, 91, head=False)
seg(152, 70, 158, 70)
vbar(159, 44, 10, 52, "#DAE8FC", "#9DB9E4", "f2b3", "#6C8EBF")
label(148, 32, 32, i("e<sub>τ</sub>") + " 192", fs=S)
seg(170, 72, 199, 72)
label(168, 47, 34, "3 frames<br>concat", fs=S, color="#4A5563")
vbar(200, 36, 14, 70, "#6ED8C6", "#1FA38F", "f2b4", "#178A79")
label(190, 108, 36, i("c<sub>t</sub>") + " 576", bold=True)
label(8, 119, 228, "shared by the 3 frames; frozen in post-training (no LoRA)", fs=S, italic=True, color="#4A5563")

# ================= (c) multi-stage PointNet =================
band(8, 138, 228, 119, "#EEF6F1", "#7FB09A", radius=8)
ttl(8, 141, 228, "(c) Multi-stage PointNet")
bx(14, 166, 40, 22, "Conv1d<br>3→128", BLUEB, fs=S)
seg(55, 177, 65, 177)
band(60, 158, 170, 46, "#F7FBFF", "#9DB7D6", radius=4, dashed=True)
label(64, 159, 80, "stage " + i("s") + " (× 4)", fs=S, align="left", color="#3D5A80", bold=True)
bx(66, 170, 44, 20, "Conv1d<br>128→128", BLUEB, fs=S)
seg(111, 180, 151, 180)
seg(122, 180, 122, 188, head=False)
bx(112, 189, 40, 13, "max-pool", ORB, fs=S)
seg(153, 195, 158, 195, head=False)
seg(158, 195, 158, 187)
plus(158, 180)
label(150, 165, 18, "256", fs=S)
seg(165, 180, 171, 180)
bx(172, 170, 52, 20, "Conv1d<br>256→128", BLUEB, fs=S)
seg(90, 204, 90, 209, head=False)
seg(90, 209, 47, 209, head=False)
seg(47, 209, 47, 216)
label(96, 205, 120, "outputs of the 4 stages", fs=S, italic=True, color="#4A5563", align="left")
bx(14, 217, 68, 24, "concat 4 stages<br>4 × 128 = 512", BLUEB, fs=S)
seg(83, 229, 89, 229)
bx(90, 219, 50, 20, "Conv1d<br>512→128", BLUEB, fs=S)
seg(141, 229, 147, 229)
bx(148, 219, 50, 20, "max-pool<br>over " + i("N"), ORB, fs=S)
seg(199, 229, 205, 229)
vbar(206, 218, 8, 22, "#A9ECF7", "#2FB8D6", "f2b5", "#2FB8D6")
label(214, 224, 20, "128", fs=S, align="left")

# ================= (b) conditional 1D U-Net =================
band(244, 8, 466, 249, "#EAF3FC", "#5B9BD5", radius=8)
ttl(244, 11, 466, "(b) Conditional 1D U-Net Denoiser " + i("f<sub>θ</sub>") + "(" + ZB + ", " + i("k") + ", " + i("c<sub>t</sub>") + ")")
raw('<div style="position: absolute; left: 252px; top: 35px; width: 14px; height: 14px; box-sizing: border-box; border-radius: 50%; background: #FF9D59; border: 1px solid #E96D29; display: flex; align-items: center; justify-content: center; font-size: 8px; font-style: italic">k</div>')
seg(267, 42, 273, 42)
bx(274, 32, 66, 20, "sinusoidal emb.<br>128", ORB, fs=S)
seg(341, 42, 347, 42)
bx(348, 32, 70, 20, "MLP<br>128→512→128", ORB, fs=S)
seg(419, 42, 425, 42)
plus(432, 42)
bx(406, 60, 52, 16, i("c<sub>t</sub>") + " (576)", GREENB, fs=S)
seg(432, 60, 432, 49)
seg(439, 42, 447, 42)
label(436, 28, 18, "704", fs=S)
bx(448, 32, 116, 20, "FiLM generator<br>Linear(704 → 2" + i("C") + ") → (" + i("γ") + ", " + i("β") + ")", ORB, fs=S)
bx(576, 30, 128, 36, "<b>LoRA</b> (" + i("r") + " = 8) in all denoiser layers:<br>14 Linear + 33 Conv1d,<br>1.02 M trainable (post-training)", ("#FFF4EA", "#E07B39"), fs=S, dashed=True)
seg(506, 52, 506, 86, color="#E08A1E", head=False)
label(512, 72, 120, "FiLM in all 12 residual blocks", fs=S, color="#B4521B", align="left")

# U-Net row: residual blocks as 2.5D cubes, height by temporal length
HH = {16: 76, 8: 54, 4: 34}
BASE = 176
blocks = []   # (x, length, label)
xs = 262
items = [("in", 16), ("gap", 8),
         ("rb", 16), ("rb", 16), ("lab", "256@16"), ("ds", 0),
         ("rb", 8), ("rb", 8), ("lab", "512@8"), ("ds", 0),
         ("rb", 4), ("rb", 4), ("lab", "1024@4"), ("gap", 10),
         ("rb", 4), ("rb", 4), ("lab", "mid 1024@4"), ("gap", 10),
         ("rb", 4), ("rb", 4), ("lab", "512@4"), ("us", 0),
         ("rb", 8), ("rb", 8), ("lab", "256@8"), ("us", 0),
         ("fc", 16), ("lab", "final conv"), ("gap", 8), ("out", 16)]
svg, film_x, group_x, labs, arrows_x = [], [], [], [], []
x = 0
grp = []
for kind, v in items:
    if kind == "in" or kind == "out":
        h = HH[16]
        svg.append(f'<rect x="{x}" y="{BASE - h}" width="6" height="{h}" fill="#ffffff" stroke="#4A5563" stroke-width="0.7"/>')
        (labs.append(("in", x + 3)) if kind == "in" else labs.append(("out", x + 3)))
        x += 6
    elif kind == "gap":
        if v >= 8:
            arrows_x.append((x + v / 2 - 1, ""))
        x += v
    elif kind == "rb":
        h = HH[v]
        svg.append(cube(x, BASE - h - 3, 10, h, 3, *BL))
        svg.append(cube(x + 13, BASE - h * 0.8 - 2, 2.5, h * 0.8, 2, *OR))
        film_x.append((x + 6, h))
        grp.append(x)
        x += 19
    elif kind == "fc":
        h = HH[16]
        svg.append(cube(x, BASE - h - 3, 10, h, 3, "#C9D7EE", "#E2EAF7", "#9DB2D6", "#6C8EBF"))
        grp.append(x)
        x += 16
    elif kind == "lab":
        labs.append((v, (grp[0] + grp[-1] + 13) / 2)); grp = []
        x += 4
    elif kind in ("ds", "us"):
        arrows_x.append((x + 5, "↓2" if kind == "ds" else "↑2")); x += 12
UW = x
ox = 244 + (466 - UW) / 2
# FiLM distribution line and drops (drawn in figure coordinates)
fl = ['<path d="M%.1f 86 L%.1f 86" stroke="#E08A1E" stroke-width="0.9" fill="none"/>' % (film_x[0][0], film_x[-1][0])]
for fx, h in film_x:
    tb = BASE - h - 3
    fl.append(f'<path d="M{fx} 86 L{fx} {tb - 1}" stroke="#E08A1E" stroke-width="0.7" fill="none"/><path d="M{fx - 1.8} {tb - 3} L{fx} {tb} L{fx + 1.8} {tb - 3} Z" fill="#E08A1E"/>')
# skip connections (only two are used by the network: 1024@4 -> up 512@4 and 512@8 -> up 256@8)
def find(lbl):
    return [p for (t, p) in labs if t == lbl][0]
sk = []
for a_, b_, dy in (("512@8", "256@8", 6), ("1024@4", "512@4", 2)):
    xa, xb = find(a_), find(b_)
    sk.append(f'<path d="M{xa} {BASE + 1} L{xa} {BASE + dy + 4} L{xb} {BASE + dy + 4} L{xb} {BASE + 1}" stroke="#8a8f98" stroke-width="0.7" stroke-dasharray="2 1.5" fill="none"/>')
svg = svg + sk + fl
for (xx_, t_) in arrows_x:
    if t_:
        svg.append(f'<text x="{xx_}" y="{BASE - 18}" font-size="8" text-anchor="middle" fill="#4A5563" font-family="Tinos, serif">{t_}</text>')
        svg.append(f'<path d="M{xx_ - 5} {BASE - 10} L{xx_ + 4} {BASE - 10}" stroke="#4A7FE0" stroke-width="0.9" fill="none"/><path d="M{xx_ + 3} {BASE - 12} L{xx_ + 6} {BASE - 10} L{xx_ + 3} {BASE - 8} Z" fill="#4A7FE0"/>')
    else:
        svg.append(f'<path d="M{xx_ - 3} {BASE - 10} L{xx_ + 2} {BASE - 10}" stroke="#4A7FE0" stroke-width="0.9" fill="none"/><path d="M{xx_ + 1} {BASE - 12} L{xx_ + 4} {BASE - 10} L{xx_ + 1} {BASE - 8} Z" fill="#4A7FE0"/>')
raw(f'<svg width="{UW:.0f}" height="{BASE + 24}" viewBox="0 0 {UW:.0f} {BASE + 24}" role="img" aria-label="Conditional 1D U-Net: residual blocks at 16, 8 and 4 steps, two skip connections, LoRA on every block" '
    f'style="position: absolute; left: {ox:.0f}px; top: 0px; width: {UW:.0f}px; height: {BASE + 24}px; overflow: visible">' + "".join(svg) + '</svg>')
for (t_, px) in labs:
    if t_ == "in":
        label(ox + px - 26, 78, 52, ZB + "<br>16 × 11", fs=S)
    elif t_ == "out":
        label(ox + px - 30, 78, 60, i("Ẑ") + "<sub>" + i("t") + "</sub><sup>0</sup><br>16 × 11", fs=S)
    else:
        label(ox + px - 26, BASE + 13, 52, t_, fs=S)
label(ox + (find("1024@4") + find("512@4")) / 2 - 40, BASE + 23, 80, "skip (concat)", fs=S, color="#4A5563")
# residual block detail
band(252, 218, 450, 34, "#ffffff", "#C9CED6", radius=4)
label(258, 221, 70, "<b>Residual block</b>", fs=S, align="left")
label(258, 236, 12, i("h"), align="left")
seg(268, 241, 279, 241)
bx(278, 231, 100, 20, "Conv1d (" + i("k") + " = 5),<br>GroupNorm, Mish", BLUEB, fs=S)
seg(379, 241, 383, 241)
bx(384, 232, 70, 18, i("γ") + " ⊙ " + i("h") + " + " + i("β"), ORB, fs=S)
label(384, 220, 70, "from FiLM", fs=S, color="#B4521B")
seg(455, 241, 461, 241)
bx(462, 231, 100, 20, "Conv1d (" + i("k") + " = 5),<br>GroupNorm, Mish", BLUEB, fs=S)
seg(563, 241, 567, 241)
plus(574, 241)
seg(581, 241, 589, 241)
label(590, 236, 20, "out", fs=S, align="left")
label(612, 233, 88, "residual: 1 × 1 conv<br>if channels change", fs=S, align="left", color="#4A5563")
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
