"""Minimal pptx drawing kit in canvas pixel units (96 px/in -> 9525 EMU/px).
Mirrors the Design-canvas primitives (seg/card/band/label/img) so canvas figures can be ported
as native, editable PowerPoint shapes. Text: Times New Roman; 9.33 px = 7 pt, 8 px = 6 pt."""
import re, math
from html.parser import HTMLParser
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
from PIL import ImageFont

PX = 9525
FONT = "Times New Roman"
INK = "#1f2328"
_FD = "/usr/share/fonts/truetype/liberation/LiberationSerif-"
_fonts = {}


def E(v):
    return Emu(int(round(v * PX)))


def rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return RGBColor.from_string(h.upper())


def pt_of(fs):  # fs in px (number or '8px')
    if isinstance(fs, str):
        fs = float(fs.replace("px", ""))
    return round(fs * 0.75 * 2) / 2 if fs * 0.75 >= 6 else 6.0


def _font(bold, italic, size_pt):
    key = (bold, italic, size_pt)
    if key not in _fonts:
        st = {(0, 0): "Regular", (1, 0): "Bold", (0, 1): "Italic", (1, 1): "BoldItalic"}[(int(bold), int(italic))]
        _fonts[key] = ImageFont.truetype(_FD + st + ".ttf", size=int(size_pt * 20))
    return _fonts[key]


# ---------------- rich text ----------------
class _RP(HTMLParser):
    def __init__(self):
        super().__init__()
        self.st = [dict(b=False, i=False, sub=False, sup=False, color=None)]
        self.lines = [[]]

    def handle_starttag(self, tag, attrs):
        s = dict(self.st[-1])
        if tag == "br":
            self.lines.append([]); return
        if tag == "b": s["b"] = True
        if tag == "i": s["i"] = True
        if tag == "sub": s["sub"] = True
        if tag == "sup": s["sup"] = True
        if tag == "span":
            m = re.search(r"color:\s*(#[0-9A-Fa-f]{3,6})", dict(attrs).get("style", "") or "")
            if m: s["color"] = m.group(1)
        self.st.append(s)

    def handle_endtag(self, tag):
        if tag != "br" and len(self.st) > 1:
            self.st.pop()

    def handle_data(self, d):
        if d:
            self.lines[-1].append((d, dict(self.st[-1])))


def parse(html):
    p = _RP(); p.feed(html.replace("<br/>", "<br>")); return p.lines


def measure(html, size_pt, bold=False, italic=False):
    """width in px of the widest line."""
    w = 0
    for line in parse(html):
        lw = 0
        for t, s in line:
            sz = size_pt * (0.7 if (s["sub"] or s["sup"]) else 1)
            f = _font(bold or s["b"], italic or s["i"], sz)
            lw += f.getlength(t) / 20 / 0.75
        w = max(w, lw)
    return w


def fill_tf(tf, html, size_pt, align="center", bold=False, italic=False, color=INK, anchor="middle",
            inset=(0, 0, 0, 0), wrap=True, lsp=None):
    tf.clear()
    tf.word_wrap = wrap
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = [E(v) for v in inset]
    tf.vertical_anchor = {"middle": MSO_ANCHOR.MIDDLE, "top": MSO_ANCHOR.TOP, "bottom": MSO_ANCHOR.BOTTOM}[anchor]
    bp = tf._txBody.find(qn("a:bodyPr"))
    for c in list(bp):
        bp.remove(c)
    etree.SubElement(bp, qn("a:noAutofit"))
    lines = parse(html)
    for li, line in enumerate(lines):
        para = tf.paragraphs[0] if li == 0 else tf.add_paragraph()
        para.alignment = {"center": PP_ALIGN.CENTER, "left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT}[align]
        if lsp:
            para.line_spacing = lsp
        if not line:
            line = [(" ", dict(b=False, i=False, sub=False, sup=False, color=None))]
        for t, s in line:
            r = para.add_run(); r.text = t
            f = r.font; f.name = FONT; f.size = Pt(size_pt)
            f.bold = bold or s["b"]; f.italic = italic or s["i"]
            f.color.rgb = rgb(s["color"] or color)
            rPr = r._r.get_or_add_rPr()
            for tag in ("a:ea", "a:cs"):
                el = rPr.find(qn(tag))
                if el is None:
                    el = etree.SubElement(rPr, qn(tag))
                el.set("typeface", FONT)
            if s["sub"]:
                rPr.set("baseline", "-25000"); f.size = Pt(round(size_pt * 1.25 * 2) / 2)
            if s["sup"]:
                rPr.set("baseline", "30000"); f.size = Pt(round(size_pt * 1.25 * 2) / 2)
        # end paragraph props so empty trailing text keeps size
        epr = para._p.get_or_add_endParaRPr(); epr.set("sz", str(int(size_pt * 100)))


class Fig:
    def __init__(self, slide, ox=0, oy=0):
        self.s = slide; self.ox = ox; self.oy = oy; self.n = 0

    def _name(self, sh, kind):
        self.n += 1
        sh.name = f"{kind}-{self.n}"
        return sh

    # ------------- basic shapes -------------
    def rect(self, x, y, w, h, fill="#FFFFFF", line="#8a8f98", radius=3, dashed=False, lw=1.0, shape=None,
             line_dash="dash"):
        st = shape or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE)
        sh = self.s.shapes.add_shape(st, E(x + self.ox), E(y + self.oy), E(w), E(h))
        if st == MSO_SHAPE.ROUNDED_RECTANGLE:
            sh.adjustments[0] = min(0.5, radius / max(1e-6, min(w, h)))
        if fill is None:
            sh.fill.background()
        else:
            sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        if line is None:
            sh.line.fill.background()
        else:
            sh.line.color.rgb = rgb(line); sh.line.width = Pt(lw * 0.75)
            if dashed:
                ln = sh.line._get_or_add_ln()
                d = etree.SubElement(ln, qn("a:prstDash")); d.set("val", line_dash)
        sh.shadow.inherit = False
        return self._name(sh, "box")

    def card(self, x, y, w, h, html, fill="#ffffff", border="#8a8f98", fs=9.33, top=False, radius=3, dashed=False,
             bold=False, color=INK, italic=False, lw=1.0):
        sh = self.rect(x, y, w, h, fill, border, radius, dashed, lw=lw)
        fill_tf(sh.text_frame, html, pt_of(fs), bold=bold, italic=italic, color=color,
                anchor="top" if top else "middle", inset=(2, 2 if top else 1, 2, 1))
        return sh

    def label(self, x, y, w, html, fs=9.33, align="center", bold=False, color=INK, italic=False, h=None, anchor="top"):
        n = len(parse(html))
        size = pt_of(fs)
        hh = h if h is not None else n * size / 0.75 * 1.2 + 1
        tb = self.s.shapes.add_textbox(E(x + self.ox), E(y + self.oy), E(w), E(hh))
        fill_tf(tb.text_frame, html, size, align=align, bold=bold, italic=italic, color=color, anchor=anchor,
                wrap=False)
        return self._name(tb, "text")

    def line(self, x1, y1, x2, y2, color="#6A84AE", sw=1.2, head=True, dash=None, both=False):
        c = self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1 + self.ox), E(y1 + self.oy), E(x2 + self.ox), E(y2 + self.oy))
        c.line.color.rgb = rgb(color); c.line.width = Pt(sw * 0.75)
        ln = c.line._get_or_add_ln()
        if dash:
            d = etree.SubElement(ln, qn("a:prstDash")); d.set("val", "sysDash" if dash == "dot" else "dash")
        if both:
            he = etree.SubElement(ln, qn("a:headEnd")); he.set("type", "triangle"); he.set("w", "med"); he.set("len", "med")
        if head:
            te = etree.SubElement(ln, qn("a:tailEnd")); te.set("type", "triangle"); te.set("w", "med"); te.set("len", "med")
        return self._name(c, "arrow" if head else "line")

    def poly(self, pts, fill=None, line="#7F9CC8", lw=0.9, closed=True, dash=None, head=False, grad=None):
        pts = [(x + self.ox, y + self.oy) for x, y in pts]
        fb = self.s.shapes.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
        fb.add_line_segments([(E(x), E(y)) for x, y in pts[1:]], close=closed)
        sh = fb.convert_to_shape()
        if grad:
            sh.fill.gradient(); sh.fill.gradient_angle = 0
            st = sh.fill.gradient_stops
            st[0].color.rgb = rgb(grad[0]); st[0].position = 0
            st[1].color.rgb = rgb(grad[1]); st[1].position = 1.0
        elif fill is None:
            sh.fill.background()
        else:
            sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        if line is None:
            sh.line.fill.background()
        else:
            sh.line.color.rgb = rgb(line); sh.line.width = Pt(lw * 0.75)
            ln = sh.line._get_or_add_ln()
            if dash:
                d = etree.SubElement(ln, qn("a:prstDash")); d.set("val", dash)
            if head:
                te = etree.SubElement(ln, qn("a:tailEnd")); te.set("type", "triangle"); te.set("w", "med"); te.set("len", "med")
        sh.shadow.inherit = False
        return self._name(sh, "poly")

    def curve(self, p0, p1, p2, p3, color, sw, head=True, n=24):
        pts = []
        for k in range(n + 1):
            t = k / n
            x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
            y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
            pts.append((x, y))
        return self.poly(pts, fill=None, line=color, lw=sw, closed=False, head=head)

    def oval(self, cx, cy, r, fill="#FFFFFF", line="#4A5563", lw=0.9, html=None, fs=8, bold=False, color=INK, rx=None):
        rx = rx or r
        sh = self.s.shapes.add_shape(MSO_SHAPE.OVAL, E(cx - rx + self.ox), E(cy - r + self.oy), E(2 * rx), E(2 * r))
        sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        sh.line.color.rgb = rgb(line); sh.line.width = Pt(lw * 0.75)
        sh.shadow.inherit = False
        if html:
            fill_tf(sh.text_frame, html, pt_of(fs), bold=bold, color=color, wrap=False)
        return self._name(sh, "node")

    def concat_c(self, x, y):
        return self.oval(x, y, 6, html="<b>C</b>", fs=8)

    def plus(self, x, y, r=5):
        self.oval(x, y, r)
        self.line(x, y - r + 2, x, y + r - 2, color="#4A5563", sw=0.9, head=False)
        self.line(x - r + 2, y, x + r - 2, y, color="#4A5563", sw=0.9, head=False)

    def lock(self, x, y):
        """7x9 px padlock at top-left (x,y)."""
        pts = []
        for k in range(13):
            a = math.pi * k / 12
            pts.append((x + 3.5 - 1.9 * math.cos(a), y + 2.6 - 1.9 * math.sin(a)))
        pts = [(x + 1.6, y + 4.2)] + pts + [(x + 5.4, y + 4.2)]
        self.poly(pts, fill=None, line="#2E3B4E", lw=0.9, closed=False)
        self.rect(x + 0.5, y + 4, 6, 4.6, fill="#2E3B4E", line=None, radius=0.8)

    def img(self, x, y, w, h, path):
        from PIL import Image
        im = Image.open(path); iw, ih = im.size
        sc = min(w / iw, h / ih); ww, hh = iw * sc, ih * sc
        pic = self.s.shapes.add_picture(path, E(x + (w - ww) / 2 + self.ox), E(y + (h - hh) / 2 + self.oy), E(ww), E(hh))
        return self._name(pic, "img")

    def text_lock(self, x, y, w, h, html, fs=9.33, color=INK, bold=False, align="center"):
        """Centered multi-line label with a padlock after the last line (canvas inline lock)."""
        size = pt_of(fs)
        lines = parse(html)
        n = len(lines)
        self.label(x, y, w, html, fs=fs, color=color, bold=bold, h=h, anchor="middle", align=align)
        last = "".join(t for t, _ in lines[-1])
        lw_ = measure(last, size, bold=bold)
        lh = size / 0.75 * 1.2
        ly = y + h / 2 + (n / 2 - 1) * lh
        lx = x + w / 2 + lw_ / 2 + 2 if align == "center" else x + lw_ + 2
        self.lock(lx, ly + (lh - 9) / 2 + 0.5)
