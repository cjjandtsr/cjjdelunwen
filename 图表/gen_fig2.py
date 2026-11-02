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
LORA = ("#F8DCC7", "#C98A5E")          # trainable LoRA
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
bx(18, 90, 74, 14, i("P<sub>τ</sub>") + ", " + i("s<sub>τ</sub>") + ", " + i("τ") + " = 1…3", ("#FFFFFF", "#5A6B85"), fs=S)
dims(14, 106, 82, "3 × (4096×3, 9)")
seg(95, 66, 103, 66, color="#5A6B85")
# shared encoder (same identity colours as Fig. 1)
raw('<svg width="66" height="56" viewBox="0 0 66 56" aria-hidden="true" style="position: absolute; left: 104px; top: 38px; width: 66px; height: 56px; overflow: visible">'
    '<defs><linearGradient id="f2enc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E3EBF6"/><stop offset="1" stop-color="#C9D8EC"/></linearGradient></defs>'
    '<polygon points="0,0 66,11 66,45 0,56" fill="url(#f2enc)" stroke="#7F9CC8" stroke-width="0.7"/></svg>')
lk = ('<svg width="7" height="9" viewBox="0 0 7 9" role="img" aria-label="frozen" style="display: inline-block; vertical-align: -1px; margin-left: 2px; width: 7px; height: 9px">'
      '<path d="M1.6 4 V2.6 A1.9 1.9 0 0 1 5.4 2.6 V4" stroke="#2E3B4E" stroke-width="0.9" fill="none"/><rect x="0.5" y="4" width="6" height="4.6" rx="0.8" fill="#2E3B4E"/></svg>')
raw(f'<div style="position: absolute; left: 104px; top: 38px; width: 66px; height: 56px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: {F}; line-height: 1.15; color: #1F3A63"><span>Shared<br>observation<br>encoder{lk}</span></div>')
note(100, 97, 76, "per frame, frozen", align="center")
seg(171, 66, 179, 66, color="#5A6B85")
vbar(180, 40, 12, 52, COND)
label(174, 29, 24, i("c<sub>t</sub>"), bold=True, color="#2E4A73")
dims(172, 94, 28, "576")
# core region
band(206, 27, 360, 93, *CORE, radius=6)
label(414, 106, 148, "<b>Iterative denoising</b> (" + i("K") + " = 10 DDIM steps)", fs=S, color="#2E4A73", align="right")
bx(214, 44, 64, 28, "", NEUT)
img(218, 47, 56, 12, "noisy", "Gaussian noise")
label(214, 59, 64, "noise " + Zt(i("K")), fs=S)
dims(214, 73, 64, "16×11")
bx(214, 87, 64, 16, "step " + i("k"), COND, fs=S)
seg(279, 58, 297, 58, color="#5A6B85")
seg(279, 95, 290, 95, color="#6E8DBE", head=False)
seg(290, 95, 290, 66, color="#6E8DBE", head=False)
seg(290, 66, 297, 66, color="#6E8DBE")
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
label(298, 93, 112, "Conditional 1D U-Net" + lk, fs=S, bold=True)
# condition from c_t into the U-Net (bottom)
seg(186, 93, 186, 113, color="#6E8DBE", head=False)
seg(186, 113, 354, 113, color="#6E8DBE", head=False)
seg(354, 113, 354, 107, color="#6E8DBE")
note(250, 103, 70, "condition " + i("c<sub>t</sub>"), align="left")
# x0 prediction -> DDIM update -> loop
seg(411, 70, 461, 70, color="#5A6B85")
label(410, 56, 54, "predict " + Zt("0"), fs=S)
dims(410, 72, 54, "16×11")
bx(462, 58, 64, 24, "DDIM update<br>" + Zt(i("k")) + " → " + Zt(i("k") + "−1"), NEUT, fs=S)
seg(494, 58, 494, 36, color="#5A6B85", head=False)
seg(494, 36, 354, 36, color="#5A6B85", head=False)
seg(354, 36, 354, 39, color="#5A6B85")
label(420, 38, 60, "repeat × 10", fs=S, bold=True, color="#2E4A73")
seg(527, 70, 577, 70, color="#5A6B85")
bx(578, 58, 50, 24, "De-<br>normalize", NEUT, fs=S)
seg(629, 70, 637, 70, color="#5A6B85")
# output
band(638, 30, 66, 86, *OUTC, radius=5)
label(638, 33, 66, "<b>Trajectory</b>", fs=S, color="#2E4A73")
dots = "".join(f'<circle cx="{4 + j * 4.6:.1f}" cy="{30 - 22 * (j / 11) + 8 * (j / 11) ** 2:.1f}" r="1.6" fill="#4F6FA3"/>' for j in range(12))
raw(f'<svg width="58" height="34" viewBox="0 0 58 34" role="img" aria-label="Predicted trajectory" style="position: absolute; left: 642px; top: 48px; width: 58px; height: 34px; overflow: visible">'
    f'<path d="M4 30 Q 28 6 55 8" stroke="#4F6FA3" stroke-width="0.7" fill="none"/>{dots}</svg>')
dims(638, 86, 66, "16 steps × 11")
note(638, 97, 66, "position, velocity, acc., yaw", align="center")

# ======================= (b) shared observation encoder =======================
band(8, 132, 292, 220, *PANEL, radius=8)
ttl(8, 135, 292, "(b) Shared Observation Encoder" + lk)
band(14, 153, 228, 120, "#FFFFFF", "#B9C3D0", radius=4, dashed=True)
label(18, 155, 100, "<b>Point-cloud branch</b>", fs=S, align="left")
note(110, 155, 128, "4096 points → 128-d geometry feature", align="right")
img(18, 170, 40, 31, "pc", "Body-frame point cloud")
dims(16, 202, 44, "4096 × 3")
seg(59, 186, 65, 186, color="#5A6B85")
bx(66, 174, 40, 24, "Point<br>Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
seg(107, 186, 113, 186, color="#5A6B85")
# one stage, repeated x4
band(114, 168, 124, 52, "#F2F6FB", "#8EA7CF", radius=4, dashed=True)
label(118, 169, 80, "PointNet stage", fs=S, align="left", color="#3D5A80", bold=True)
label(208, 169, 28, "×4", fs=S, align="right", color="#3D5A80", bold=True)
bx(118, 181, 40, 16, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
seg(159, 189, 183, 189, color="#5A6B85")
seg(138, 197, 138, 202, color="#5A6B85", head=False)
bx(116, 203, 70, 13, "global max-pool", NEUT, fs=S)
seg(187, 209, 190, 209, color="#5A6B85", head=False)
seg(190, 209, 190, 196, color="#5A6B85")
concat_c(190, 189)
seg(197, 189, 201, 189, color="#5A6B85")
bx(202, 181, 34, 16, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
# after stages
seg(176, 231, 176, 240, color="#5A6B85") if False else None
bx(18, 238, 58, 26, "concat 4 stages<br>(4 × 128)", NEUT, fs=S)
seg(77, 251, 83, 251, color="#5A6B85")
bx(84, 241, 42, 20, "Conv1d", ("#EAF0F8", "#8EA7CF"), fs=S)
seg(127, 251, 133, 251, color="#5A6B85")
bx(134, 241, 50, 20, "max-pool<br>over points", NEUT, fs=S)
seg(185, 251, 205, 251, color="#5A6B85")
vbar(206, 240, 10, 22, ("#C9D8EC", "#8EA7CF"))
dims(216, 245, 26, "128")
seg(176, 220, 176, 228, color="#5A6B85", head=False)
seg(176, 228, 47, 228, color="#5A6B85", head=False)
seg(47, 228, 47, 237, color="#5A6B85")
note(60, 228, 120, "outputs of the 4 stages", align="left")
# state branch
band(14, 279, 228, 44, "#FFFFFF", "#B9C3D0", radius=4, dashed=True)
label(18, 281, 100, "<b>State branch</b>", fs=S, align="left")
note(110, 281, 128, "goal, distance, position, heading", align="right")
bx(20, 296, 42, 20, "9-d state", ("#FFFFFF", "#5A6B85"), fs=S)
seg(63, 306, 75, 306, color="#5A6B85")
bx(76, 296, 84, 20, "MLP 9→64→64", ("#DCE6F3", "#7F9CC8"), fs=S)
seg(161, 306, 205, 306, color="#5A6B85")
vbar(206, 299, 10, 14, ("#DCE6F3", "#7F9CC8"))
dims(216, 302, 26, "64")
# fusion column
seg(217, 251, 252, 251, head=False, color="#5A6B85") if False else None
seg(243, 251, 250, 251, color="#5A6B85", head=False)
seg(243, 306, 250, 306, color="#5A6B85", head=False)
seg(250, 251, 250, 306, color="#5A6B85", head=False)
seg(250, 278, 255, 278, color="#5A6B85")
bx(256, 262, 38, 32, "concat<br>192 per<br>frame", NEUT, fs=S)
seg(275, 294, 275, 309, color="#5A6B85")
note(250, 296, 22, "×3", align="left")
vbar(266, 310, 18, 30, COND)
label(254, 340, 42, i("c<sub>t</sub>") + " 576", fs=S, bold=True, color="#2E4A73")
note(14, 328, 236, "identical weights for the 3 frames; no LoRA in the encoder", align="left")

# ======================= (c) one denoising call =======================
band(308, 132, 402, 136, *PANEL, radius=8)
ttl(308, 135, 402, "(c) One Denoising Call: Conditional 1D U-Net")
bx(316, 154, 40, 14, "step " + i("k"), COND, fs=S)
seg(357, 161, 363, 161, color="#6E8DBE")
bx(364, 154, 62, 14, "time embedding", COND, fs=S)
bx(316, 172, 40, 14, i("c<sub>t</sub>") + " (576)", COND, fs=S)
seg(427, 161, 436, 161, color="#6E8DBE", head=False)
seg(357, 179, 436, 179, color="#6E8DBE", head=False)
seg(436, 161, 436, 179, color="#6E8DBE", head=False)
seg(436, 170, 443, 170, color="#6E8DBE")
bx(444, 162, 52, 16, "concat 704", COND, fs=S)
seg(497, 170, 503, 170, color="#6E8DBE")
bx(504, 160, 60, 20, "<b>FiLM</b> (" + i("γ") + ", " + i("β") + ")", COND, fs=S)
note(568, 160, 140, "scales and shifts every block's<br>features by (step, observation)", align="left")
# blocks row
BY, BH = 202, 26
blocks = [("256@16", 340), ("512@8", 390), ("1024@4", 440), ("mid<br>1024@4", 488), ("512@4", 536), ("256@8", 586)]
BW = 38
seg(534, 180, 534, 188, color="#6E8DBE", head=False)
seg(359, 188, 605, 188, color="#6E8DBE", head=False)
for lb, bxx in blocks:
    seg(bxx + BW // 2, 188, bxx + BW // 2, BY - 1, color="#6E8DBE", sw=0.9)
    bx(bxx, BY, BW, BH, lb, FROZ, fs=S)
    raw(f'<div style="position: absolute; left: {bxx + BW - 5}px; top: {BY + 3}px; width: 3px; height: {BH - 6}px; background: #E0A77E"></div>')
label(312, BY + 2, 28, Zt(i("k")) + "<br>16×11", fs=S)
seg(338, BY + 13, 339, BY + 13, color="#5A6B85") if False else None
for (a_, b_, t_) in ((378, 389, "↓2"), (428, 439, "↓2"), (478, 487, ""), (526, 535, ""), (574, 585, "↑2")):
    seg(a_, BY + 13, b_, BY + 13, color="#5A6B85")
    if t_:
        label(a_ - 4, BY - 9, 18, t_, fs=S, color="#4A5563")
seg(625, BY + 13, 635, BY + 13, color="#5A6B85")
label(618, BY - 9, 18, "↑2", fs=S, color="#4A5563")
bx(636, BY, 30, BH, "final<br>conv", FROZ, fs=S)
seg(667, BY + 13, 673, BY + 13, color="#5A6B85")
label(672, BY + 2, 36, Zt("0") + "<br>16×11", fs=S, color="#2E4A73", bold=True)
label(312, BY + 28, 30, "noisy", fs=S, color=NOTE, italic=True)
label(670, BY + 28, 40, "clean", fs=S, color="#2E4A73", italic=True)
# skip connections
seg(459, BY + BH, 459, BY + BH + 6, color="#4A5563", sw=0.8, head=False, dash="2 1.5")
seg(459, BY + BH + 6, 555, BY + BH + 6, color="#4A5563", sw=0.8, head=False, dash="2 1.5")
seg(555, BY + BH + 6, 555, BY + BH + 1, color="#4A5563", sw=0.8, dash="2 1.5")
seg(409, BY + BH, 409, BY + BH + 12, color="#4A5563", sw=0.8, head=False, dash="2 1.5")
seg(409, BY + BH + 12, 605, BY + BH + 12, color="#4A5563", sw=0.8, head=False, dash="2 1.5")
seg(605, BY + BH + 12, 605, BY + BH + 1, color="#4A5563", sw=0.8, dash="2 1.5")
note(470, BY + BH + 13, 120, "skip connections (concat)", align="left")
note(316, 250, 390, "each box = 2 conditional residual blocks (12 in total); encoder–bottleneck–decoder over the 16-step axis", align="left")

# ======================= (d) residual block with LoRA =======================
band(308, 276, 402, 76, *PANEL, radius=8)
ttl(308, 279, 402, "(d) Conditional Residual Block with LoRA")
label(314, 304, 12, i("x"), fs=S)
names = ["Conv1d", "GN", "Mish", "FiLM", "Conv1d", "GN", "Mish"]
ws_ = [32, 20, 24, 26, 32, 20, 24]
xs_ = []
xc = 330
for ww in ws_:
    xs_.append(xc); xc += ww + 6
for xx_, nm, ww in zip(xs_, names, ws_):
    bx(xx_, 304, ww, 16, nm, COND if nm == "FiLM" else FROZ, fs=S)
for xx_, ww, nx in zip(xs_[:-1], ws_[:-1], xs_[1:]):
    seg(xx_ + ww, 312, nx - 1, 312, color="#5A6B85", sw=1)
fx = xs_[3] + 13
seg(fx, 297, fx, 303, color="#6E8DBE")
end = xs_[-1] + ws_[-1]
seg(end, 312, end + 6, 312, color="#5A6B85")
plus(end + 12, 312)
seg(end + 17, 312, end + 21, 312, color="#5A6B85")
label(end + 21, 306, 10, i("y"), fs=S, align="left")
seg(324, 312, 329, 312, color="#5A6B85")
seg(324, 312, 324, 328, color="#5A6B85", head=False)
seg(324, 328, end + 12, 328, color="#5A6B85", head=False)
seg(end + 12, 328, end + 12, 318, color="#5A6B85")
note(332, 329, 200, "residual path (1×1 conv if channels change)", align="left")
band(580, 296, 124, 52, "#FFFAF5", "#C98A5E", radius=4, dashed=True)
label(584, 297, 60, "<b>LoRA</b> (trainable)", fs=S, color="#9A6A45", align="left")
seg(584, 320, 588, 320, color="#5A6B85", head=False)
seg(588, 313, 588, 337, color="#5A6B85", head=False)
seg(588, 313, 593, 313, color="#5A6B85")
bx(594, 307, 40, 13, i("W") + "<sub>0</sub>" + lk, FROZ, fs=S)
seg(588, 337, 593, 337, color="#5A6B85")
bx(594, 331, 17, 13, i("A"), LORA, fs=S)
seg(612, 337, 616, 337, color="#5A6B85")
bx(617, 331, 17, 13, i("B"), LORA, fs=S)
seg(635, 313, 640, 313, color="#5A6B85", head=False)
seg(635, 337, 640, 337, color="#5A6B85", head=False)
seg(640, 313, 640, 337, color="#5A6B85", head=False)
note(645, 306, 58, i("W") + " = " + i("W") + "<sub>0</sub> + " + i("BA") + "<br>rank 8<br>" + i("B") + " = 0 at start", align="left")
note(316, 340, 260, "LoRA in all 14 Linear and 33 Conv1d layers (1.4% of parameters)", align="left")

# zoom lines from (a) to (b), (c)
seg(137, 118, 137, 131, color="#7A8496", sw=0.9, dash="3 2")
seg(354, 121, 354, 131, color="#7A8496", sw=0.9, dash="3 2")

# legend
for (lx, kind, tx) in ((316, "lock", "frozen in post-training"), (430, LORA, "trainable LoRA"), (512, COND, "condition path"), (600, OUTC, "output")):
    if kind == "lock":
        lock(lx, 356)
    else:
        swatch(lx, 357, kind[0], kind[1])
    label(lx + 10, 355, 100, tx, fs=S, align="left")
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
