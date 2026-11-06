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
# Figure 2 v2: policy network, overview + three zoom-ins (190 x 98 mm = 718 x 372 px)
W, H = 718, 372
FN, TITLE = "Fig2.dc.html", "Figure 2 Point-cloud-conditioned diffusion policy network"

# semantic palette (shared with Fig. 1 and Fig. 3)
FROZ = ("#FFFFFF", "#7F9CC8")          # frozen module: white fill, blue border
CORE = ("#EEF3FA", "#B7C9E5")          # highlighted core region
COND = ("#DCE6F3", "#6E8DBE")          # condition path (c_t, k, FiLM)
LORA = ("#F6EBDA", "#B88A52")          # trainable LoRA (training family, as Fig. 1/3)
FILM = ("#F2C3A0", "#C98A5E")          # FiLM (same orange as Fig. 1)
OUTC = ("#EAF0F8", "#4F6FA3")          # output trajectory
NEUT = ("#FFFFFF", "#8A8F98")          # parameter-free operations
PANEL = ("#F7F9FC", "#A9BEDD")         # panel background (same family as Fig. 1(c))
NOTE = "#5A6270"


def note(x, y, w, text, align="left"):
    label(x, y, w, text, fs=S, italic=True, color=NOTE, align=align)


def dims(x, y, w, text):
    label(x, y, w, text, fs=S, italic=True, color="#3A4452")


def concat_c(x, y):
    raw(f'<div style="position: absolute; left: {x - 6}px; top: {y - 6}px; width: 12px; height: 12px; box-sizing: border-box; border-radius: 50%; '
        f'background: #ffffff; border: 1px solid #4A5563; display: flex; align-items: center; justify-content: center; font-size: 7px; font-weight: 700">C</div>')


def plus(x, y, r=5):
    raw(f'<svg width="{2*r}" height="{2*r}" viewBox="0 0 {2*r} {2*r}" aria-hidden="true" style="position: absolute; left: {x - r}px; top: {y - r}px; width: {2*r}px; height: {2*r}px; overflow: visible">'
        f'<circle cx="{r}" cy="{r}" r="{r - 0.5}" fill="#ffffff" stroke="#4A5563" stroke-width="0.9"/>'
        f'<path d="M{r} 2 L{r} {2*r - 2} M2 {r} L{2*r - 2} {r}" stroke="#4A5563" stroke-width="0.9"/></svg>')


def lockicon(x, y):
    lock(x, y)


def vbar(x, y, w, h, pal, gid=None):
    raw(f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; box-sizing: border-box; background: {pal[0]}; border: 1px solid {pal[1]}; border-radius: 2px"></div>')


def zoom(points, color="#7A8496"):
    """dashed zoom line between panels (illustrative, may be diagonal)."""
    d = "M" + " L".join(f"{x} {y}" for x, y in points)
    raw(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true" style="position: absolute; left: 0px; top: 0px; width: {W}px; height: {H}px; overflow: visible; pointer-events: none">'
        f'<path d="{d}" stroke="{color}" stroke-width="0.8" stroke-dasharray="3 2" fill="none"/></svg>')


Zt = lambda k: i("Z") + "<sub>" + i("t") + "</sub><sup>" + k + "</sup>"

# ======================= (a) overall flow =======================
band(8, 8, 702, 116, *PANEL, radius=8)
ttl(8, 11, 702, "(a) Overall Network Flow")
# input
label(10, 30, 92, "<b>Observations (3 frames)</b>", fs=S)
img(20, 42, 70, 45, "three", "Point clouds of the last three frames")
dims(14, 92, 82, "3 × (4096×3, 9)")
seg(91, 66, 103, 66, color="#5A6B85")
# shared encoder (same identity colours as Fig. 1)
raw('<svg width="66" height="56" viewBox="0 0 66 56" aria-hidden="true" style="position: absolute; left: 104px; top: 38px; width: 66px; height: 56px; overflow: visible">'
    '<defs><linearGradient id="f2enc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E3EBF6"/><stop offset="1" stop-color="#C9D8EC"/></linearGradient></defs>'
    '<polygon points="0,0 66,11 66,45 0,56" fill="url(#f2enc)" stroke="#7F9CC8" stroke-width="0.7"/></svg>')
lk = ('<svg width="7" height="9" viewBox="0 0 7 9" role="img" aria-label="frozen" style="display: inline-block; vertical-align: -1px; margin-left: 2px; width: 7px; height: 9px">'
      '<path d="M1.6 4 V2.6 A1.9 1.9 0 0 1 5.4 2.6 V4" stroke="#2E3B4E" stroke-width="0.9" fill="none"/><rect x="0.5" y="4" width="6" height="4.6" rx="0.8" fill="#2E3B4E"/></svg>')
raw(f'<div style="position: absolute; left: 104px; top: 38px; width: 66px; height: 56px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: {F}; line-height: 1.15; color: #1F3A63"><span>Shared<br>observation<br>encoder{lk}</span></div>')
seg(171, 66, 179, 66, color="#5A6B85")
vbar(180, 40, 12, 52, COND)
label(174, 29, 24, i("c<sub>t</sub>"), bold=True, color="#2E4A73")
dims(172, 94, 28, "576")
# core region
band(206, 27, 360, 93, *CORE, radius=6)
label(414, 106, 148, "<b>Iterative denoising</b>", fs=S, color="#2E4A73", align="right")
bx(214, 44, 64, 28, "", NEUT)
img(218, 47, 56, 12, "noisy", "Gaussian noise")
label(214, 59, 64, "noise " + Zt(i("K")), fs=S)
dims(214, 73, 64, "16×11")
bx(214, 87, 64, 16, "step " + i("k"), COND, fs=S)
seg(279, 58, 297, 58, color="#5A6B85")
seg(279, 95, 285, 95, color="#6E8DBE", head=False)
seg(285, 95, 285, 68, color="#6E8DBE", head=False)
seg(285, 68, 297, 68, color="#6E8DBE")
# U-Net mini cubes (same drawing language as Fig. 1)
u, base, dpt = [], 44, 3
hs = [36, 27, 19, 12]
xx = 3
for hh in hs:
    u.append(cube(xx, base - hh - dpt, 5, hh, dpt, *BL)); u.append(cube(xx + 8, base - hh * 0.8 - 2, 1.5, hh * 0.8, 1.5, *OR)); xx += 10
u.append(cube(xx, base - 7 - dpt, 8, 5, dpt, "#C9D8EC", "#E3EBF6", "#A7BEDF", "#6F8BBA")); xx += 12
for hh in reversed(hs):
    u.append(cube(xx, base - hh * 0.8 - 2, 1.5, hh * 0.8, 1.5, *OR)); u.append(cube(xx + 3, base - hh - dpt, 5, hh, dpt, *BL)); xx += 10
UW = xx + 2
band(298, 40, 112, 66, "#FFFFFF", "#4C72B0", radius=4)
raw(f'<svg width="{UW}" height="54" viewBox="0 0 {UW} 46" role="img" aria-label="Conditional 1D U-Net" style="position: absolute; left: {354 - UW / 2:.0f}px; top: 44px; width: {UW}px; height: 46px; overflow: visible">' + "".join(u) + '</svg>')
label(298, 93, 112, "U-Net" + lk + " + <span style=\"color: #9C7A4C\">LoRA</span>", fs=S, bold=True)
# condition from c_t into the U-Net (bottom)
seg(186, 93, 186, 116, color="#6E8DBE", head=False)
seg(186, 116, 354, 116, color="#6E8DBE", head=False)
seg(354, 116, 354, 107, color="#6E8DBE")
note(250, 103, 70, "condition " + i("c<sub>t</sub>"), align="left")
# x0 prediction -> DDIM update -> loop
seg(411, 70, 461, 70, color="#5A6B85")
label(410, 56, 54, "predict " + Zt("0"), fs=S)
bx(462, 58, 64, 24, "DDIM<br>update", NEUT, fs=S)
seg(494, 58, 494, 31, color="#5A6B85", head=False)
seg(494, 31, 354, 31, color="#5A6B85", head=False)
seg(354, 31, 354, 39, color="#5A6B85")
label(420, 33, 60, "× 10", fs=S, bold=True, color="#2E4A73")
seg(527, 70, 577, 70, color="#5A6B85")
bx(578, 58, 50, 24, "De-<br>normalize", NEUT, fs=S)
seg(629, 70, 637, 70, color="#5A6B85")
# output
band(638, 30, 66, 86, *OUTC, radius=5)
label(638, 33, 66, "<b>Action seq.</b>", fs=S, color="#2E4A73")
dots = "".join(f'<circle cx="{4 + j * 4.6:.1f}" cy="{30 - 22 * (j / 11) + 8 * (j / 11) ** 2:.1f}" r="1.6" fill="#4F6FA3"/>' for j in range(12))
raw(f'<svg width="58" height="34" viewBox="0 0 58 34" role="img" aria-label="Predicted trajectory" style="position: absolute; left: 642px; top: 48px; width: 58px; height: 34px; overflow: visible">'
    f'<path d="M4 30 Q 28 6 55 8" stroke="#4F6FA3" stroke-width="0.7" fill="none"/>{dots}</svg>')
dims(638, 86, 66, "16 steps × 11")

# ======================= (b) shared observation encoder =======================
band(8, 132, 292, 220, *PANEL, radius=8)
ttl(8, 135, 292, "(b) Shared Observation Encoder" + lk)
band(14, 153, 228, 120, "#FFFFFF", "#B9C3D0", radius=4, dashed=True)
label(18, 155, 100, "<b>Point-cloud branch</b>", fs=S, align="left")
img(18, 170, 36, 28, "pc", "Body-frame point cloud")
dims(16, 202, 44, "4096 × 3")
seg(55, 186, 65, 186, color="#5A6B85")
bx(66, 174, 36, 24, "Point<br>Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
seg(103, 186, 113, 186, color="#5A6B85")
# one stage, repeated x4
band(114, 168, 124, 52, "#F2F6FB", "#8EA7CF", radius=4, dashed=True)
label(118, 169, 80, "PointNet stage", fs=S, align="left", color="#3D5A80", bold=True)
label(208, 169, 28, "×4", fs=S, align="right", color="#3D5A80", bold=True)
bx(118, 181, 40, 16, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
seg(159, 189, 179, 189, color="#5A6B85")
seg(138, 197, 138, 202, color="#5A6B85", head=False)
bx(116, 203, 64, 13, "global max-pool", NEUT, fs=S)
seg(181, 209, 186, 209, color="#5A6B85", head=False)
seg(186, 209, 186, 196, color="#5A6B85")
concat_c(186, 189)
seg(192, 189, 201, 189, color="#5A6B85")
bx(202, 181, 34, 16, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
# after stages
seg(176, 231, 176, 240, color="#5A6B85") if False else None
bx(18, 238, 58, 26, "concat 4 stages<br>(4 × 128)", NEUT, fs=S)
seg(77, 251, 87, 251, color="#5A6B85")
bx(88, 241, 38, 20, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
seg(127, 251, 137, 251, color="#5A6B85")
bx(138, 241, 50, 20, "max-pool<br>over points", NEUT, fs=S)
seg(189, 251, 205, 251, color="#5A6B85")
vbar(206, 240, 10, 22, ("#C9D8EC", "#8EA7CF"))
dims(216, 245, 26, "128")
seg(176, 220, 176, 228, color="#5A6B85", head=False)
seg(176, 228, 47, 228, color="#5A6B85", head=False)
seg(47, 228, 47, 237, color="#5A6B85")
# state branch
band(14, 279, 228, 44, "#FFFFFF", "#B9C3D0", radius=4, dashed=True)
label(18, 281, 100, "<b>State branch</b>", fs=S, align="left")
bx(20, 296, 42, 20, "9-d state", ("#FFFFFF", "#5A6B85"), fs=S)
seg(63, 306, 75, 306, color="#5A6B85")
bx(76, 296, 84, 20, "MLP 9→64→64", ("#DCE6F3", "#7F9CC8"), fs=S)
seg(161, 306, 205, 306, color="#5A6B85")
vbar(206, 299, 10, 14, ("#DCE6F3", "#7F9CC8"))
dims(216, 302, 26, "64")
# fusion column
seg(217, 251, 252, 251, head=False, color="#5A6B85") if False else None
seg(241, 251, 245, 251, color="#5A6B85", head=False)
seg(241, 306, 245, 306, color="#5A6B85", head=False)
seg(245, 251, 245, 306, color="#5A6B85", head=False)
seg(245, 278, 255, 278, color="#5A6B85")
bx(256, 262, 38, 32, "concat<br>192 per<br>frame", NEUT, fs=S)
seg(275, 294, 275, 309, color="#5A6B85")
note(250, 296, 22, "×3", align="left")
vbar(266, 310, 18, 30, COND)
label(254, 340, 42, i("c<sub>t</sub>") + " 576", fs=S, bold=True, color="#2E4A73")

# ======================= (c) one denoising call =======================
band(308, 132, 402, 136, *PANEL, radius=8)
ttl(308, 135, 402, "(c) One Denoising Call: Conditional 1D U-Net")


LR = "#B88A52"


def ring(x, y, w, h, pad=2.5, r=4):  # LoRA: dashed outline around the adapted layer
    raw(f'<div style="position: absolute; left: {x - pad}px; top: {y - pad}px; width: {w + 2 * pad}px; height: {h + 2 * pad}px; box-sizing: border-box; '
        f'border: 1px dashed {LR}; border-radius: {r}px; pointer-events: none"></div>')


def ring_poly(x, w, h0, h1, yc, pad=2.5):
    H_ = max(h0, h1) + 2 * pad
    a, b = h0 + 2 * pad, h1 + 2 * pad
    W_ = w + 2 * pad
    pts = f"0,{(H_ - a) / 2} {W_},{(H_ - b) / 2} {W_},{(H_ + b) / 2} 0,{(H_ + a) / 2}"
    raw(f'<svg width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}" aria-hidden="true" style="position: absolute; left: {x - pad}px; top: {yc - H_ / 2}px; width: {W_}px; height: {H_}px; overflow: visible">'
        f'<polygon points="{pts}" fill="none" stroke="{LR}" stroke-width="0.9" stroke-dasharray="2.5 1.8" stroke-linejoin="round"/></svg>')


def lmark(x, y):  # LoRA marker (small orange square inside a block)
    raw(f'<div style="position: absolute; left: {x}px; top: {y}px; width: 5px; height: 5px; box-sizing: border-box; background: #F2C3A0; border: 0.7px solid #C98A5E"></div>')


def stage(x, w, h0, h1, yc, html, fill="#FFFFFF", stroke="#7F9CC8"):
    """U-Net stage: left height = input length, right height = output length."""
    H_ = max(h0, h1)
    pts = f"0,{(H_ - h0) / 2} {w},{(H_ - h1) / 2} {w},{(H_ + h1) / 2} 0,{(H_ + h0) / 2}"
    raw(f'<svg width="{w}" height="{H_}" viewBox="0 0 {w} {H_}" aria-hidden="true" style="position: absolute; left: {x}px; top: {yc - H_ / 2}px; width: {w}px; height: {H_}px; overflow: visible">'
        f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="0.9" stroke-linejoin="round"/></svg>')
    raw(f'<div style="position: absolute; left: {x}px; top: {yc - H_ / 2}px; width: {w}px; height: {H_}px; display: flex; align-items: center; justify-content: center; '
        f'text-align: center; font-size: {S}; line-height: 1.05; color: #1F3A63"><span>{html}</span></div>')


# condition path
bx(316, 151, 40, 14, "step " + i("k"), COND, fs=S)
seg(357, 158, 367, 158, color="#6E8DBE")
bx(368, 150, 66, 16, "time emb. 128", COND, fs=S)
ring(368, 150, 66, 16)
bx(316, 170, 40, 14, i("c<sub>t</sub>"), COND, fs=S)
seg(435, 158, 446, 158, color="#6E8DBE", head=False)
seg(446, 158, 446, 162, color="#6E8DBE")
seg(357, 177, 446, 177, color="#6E8DBE", head=False)
seg(446, 177, 446, 174, color="#6E8DBE")
dims(372, 178, 30, "576")
concat_c(446, 168)
seg(452, 168, 471, 168, color="#6E8DBE")
bx(472, 159, 54, 18, "cond. 704", COND, fs=S)
seg(527, 168, 612, 168, color="#6E8DBE", head=False, dash="3 2")
seg(612, 168, 612, 199, color="#6E8DBE", head=False, dash="3 2")
note(530, 157, 160, "to the FiLM of every residual block")

# U-Net container
band(334, 186, 346, 76, "#FFFFFF", "#8EA7CF", radius=4, dashed=True)
label(334, 188, 250, "<b>1D U-Net</b>: 6 stages × 2 residual blocks", fs=S, color="#2E4A73")
YC = 226
L = {16: 44, 8: 32, 4: 22}
G = 16
spec = [("Down<br>256", 36, 16, 8), ("Down<br>512", 36, 8, 4), ("Down<br>1024", 36, 4, 4), ("Mid<br>1024", 36, 4, 4),
        ("Up<br>512", 36, 4, 8), ("Up<br>256", 36, 8, 16)]
x = 340
geo = {}
bars = []
for k_, (lb, w, a_, b_) in enumerate(spec):
    stage(x, w, L[a_], L[b_], YC, lb)
    ring_poly(x, w, L[a_], L[b_], YC)
    geo[k_] = (x, w, (L[a_] + L[b_]) / 2)
    if k_ < len(spec) - 1:
        bh = min(L[b_], L[spec[k_ + 1][2]])
        bx_ = x + w + 4
        raw(f'<div style="position: absolute; left: {bx_}px; top: {YC - bh / 2}px; width: 8px; height: {bh}px; box-sizing: border-box; background: {FILM[0]}; border: 1px solid {FILM[1]}; border-radius: 1px"></div>')
        seg(x + w, YC, bx_, YC, color="#5A6B85", head=False)
        seg(bx_ + 8, YC, x + w + G, YC, color="#5A6B85", head=False)
        bars.append((bx_ + 4, YC - bh / 2))
        x += w + G
    else:
        seg(x + w + 1, YC, x + w + 9, YC, color="#5A6B85")
        x += w + 10
# condition bus: injected into every FiLM layer from above
seg(int(bars[0][0]), 199, int(bars[-1][0]), 199, color="#6E8DBE", head=False)
for bxc, top in bars:
    seg(int(bxc), 199, int(bxc), int(top) - 1, color="#6E8DBE", sw=0.9)
card(x, YC - 22, 26, 44, "final<br>conv", fill="#FFFFFF", border="#7F9CC8", fs=S, lh="1.05")
ring(x, YC - 22, 26, 44)
seg(x + 27, YC, 685, YC, color="#5A6B85")
label(684, YC - 11, 26, Zt("0") + "<br>16×11", fs=S, color="#2E4A73", bold=True)
label(308, YC - 11, 26, Zt(i("k")) + "<br>16×11", fs=S)
seg(331, YC, 339, YC, color="#5A6B85")


# skip connections (outputs of Down 1024 -> Up 512, Down 512 -> Up 256)
def skip(src, dst, yb):
    xs_, ws_, hs_ = geo[src]
    xd, wd, hd = geo[dst]
    cs, cd = int(xs_ + ws_ / 2), int(xd + wd / 2)
    seg(cs, int(YC + hs_ / 2) + 1, cs, yb, color="#4A5563", sw=0.8, head=False, dash="2 1.5")
    seg(cs, yb, cd, yb, color="#4A5563", sw=0.8, head=False, dash="2 1.5")
    seg(cd, yb, cd, int(YC + hd / 2) + 2, color="#4A5563", sw=0.8, dash="2 1.5")


skip(2, 4, 247)
skip(1, 5, 254)
note(622, 249, 56, "skip (concat)")

# ======================= (d) residual block with LoRA =======================
band(308, 276, 402, 76, *PANEL, radius=8)
ttl(308, 279, 402, "(d) Conditional Residual Block with LoRA")
RY = 320  # main row centre
label(310, RY - 8, 10, i("x"), fs=S)
names = ["Conv1d", "GN", "Mish", "FiLM", "Conv1d", "GN", "Mish"]
ws_ = [32, 20, 24, 26, 32, 20, 24]
xs_ = []
xc = 330
for ww in ws_:
    xs_.append(xc); xc += ww + 9
for xx_, nm, ww in zip(xs_, names, ws_):
    if nm == "FiLM":
        bx(xx_, RY - 8, ww, 16, nm, FILM, fs=S)
    elif nm == "Conv1d":
        bx(xx_, RY - 8, ww, 16, nm, FROZ, fs=S)
        ring(xx_, RY - 8, ww, 16, pad=2)
    else:
        bx(xx_, RY - 8, ww, 16, nm, FROZ, fs=S)
for xx_, ww, nx in zip(xs_[:-1], ws_[:-1], xs_[1:]):
    seg(xx_ + ww, RY, nx - 1, RY, color="#5A6B85", sw=1)
# per-block condition encoder: 704 -> Mish -> Linear(704, 2C) -> (gamma, beta)
fx = xs_[3] + 13
CYD = 300
label(326, CYD - 5, 24, "cond.<br>704", fs="7px", color="#2E4A73", lh="1.0")
seg(349, CYD, 356, CYD, color="#6E8DBE", sw=1)
bx(357, CYD - 6, 24, 12, "Mish", FROZ, fs="7px")
seg(382, CYD, 389, CYD, color="#6E8DBE", sw=1)
bx(390, CYD - 6, 36, 12, "Linear", FROZ, fs="7px")
ring(390, CYD - 6, 36, 12, pad=2)
seg(427, CYD, fx, CYD, color="#6E8DBE", sw=1, head=False)
seg(fx, CYD, fx, RY - 9, color="#6E8DBE", sw=1)
note(fx + 3, CYD + 1, 24, i("γ") + ", " + i("β"))
end = xs_[-1] + ws_[-1]
seg(end, RY, end + 9, RY, color="#5A6B85")
plus(end + 15, RY)
seg(end + 20, RY, end + 28, RY, color="#5A6B85")
label(end + 29, RY - 6, 10, i("y"), fs=S, align="left")
seg(320, RY, 329, RY, color="#5A6B85")
seg(320, RY, 320, 340, color="#5A6B85", head=False)
seg(320, 340, end + 15, 340, color="#5A6B85", head=False)
seg(end + 15, 340, end + 15, RY + 6, color="#5A6B85")
bx(418, 334, 118, 12, "residual: Identity / 1×1 Conv1d", FROZ, fs="7px")
ring(418, 334, 118, 12, pad=2)
band(596, 296, 108, 52, "#FBF6EE", "#B88A52", radius=4, dashed=True)
label(600, 297, 100, "<b>LoRA-adapted layer</b>", fs=S, color="#6B5434", align="left")
seg(600, 324, 604, 324, color="#5A6B85", head=False)
seg(604, 313, 604, 337, color="#5A6B85", head=False)
seg(604, 313, 613, 313, color="#5A6B85")
bx(614, 307, 36, 13, i("W") + "<sub>0</sub>" + lk, FROZ, fs=S)
seg(604, 337, 613, 337, color="#5A6B85")
bx(614, 331, 15, 13, i("A"), LORA, fs=S)
seg(630, 337, 638, 337, color="#5A6B85")
bx(639, 331, 15, 13, i("B"), LORA, fs=S)
seg(651, 313, 658, 313, color="#5A6B85", head=False)
seg(655, 337, 658, 337, color="#5A6B85", head=False)
seg(658, 313, 658, 337, color="#5A6B85", head=False)
note(661, 317, 48, i("y") + " = " + i("W") + "<sub>0</sub>" + i("x") + "<br>+ (" + i("α") + "/" + i("r") + ")" + i("BAx"), align="left")

# zoom lines from (a) to (b), (c)
seg(137, 118, 137, 131, color="#7A8496", sw=0.9, dash="3 2")
seg(354, 121, 354, 131, color="#7A8496", sw=0.9, dash="3 2")

# legend
lock(316, 356)
label(326, 355, 100, "frozen in post-training", fs=S, align="left")
swatch(414, 357, FILM[0], FILM[1])
label(424, 355, 40, "FiLM", fs=S, align="left")
raw(f'<div style="position: absolute; left: 453px; top: 358px; width: 8px; height: 5px; box-sizing: border-box; background: #FFFFFF; border: 1px solid #7F9CC8"></div>')
ring(453, 358, 8, 5, pad=1.8, r=2)
label(465, 355, 140, "LoRA-adapted layer (all Linear / Conv1d)", fs=S, align="left")
swatch(612, 357, COND[0], COND[1])
label(622, 355, 60, "condition", fs=S, align="left")
swatch(664, 357, OUTC[0], OUTC[1])
label(674, 355, 40, "output", fs=S, align="left")
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
