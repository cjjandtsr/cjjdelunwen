"""Generate project/Main.dc.html (Figure 1) for the Design canvas.
Canvas 718x404 px = 190x107 mm at 96 px/in. Body text 7 pt = 9.33 px."""
import json, os

ROOT = os.environ.get("FIG_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output"))
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

