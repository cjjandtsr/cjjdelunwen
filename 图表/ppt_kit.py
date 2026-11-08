"""在PPT页面上画可编辑示意图的小工具（Times New Roman、单位mm），供图1—图3和S4脚本共用。

文字用 runs 列表表示：[(文本, 标记)]，标记可含 b（粗）i（斜）sub（下标）sup（上标）。
一个段落是一个 runs 列表，paras 是段落列表。
"""
from lxml import etree

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
A = "{%s}" % NS["a"]
PN = "{%s}" % NS["p"]
MM = 36000
FONT = "Times New Roman"

# 与图1一致的配色
C = dict(ink="0B1020", grey="555B63", lgrey="8C939D", arrow="5997FF", blue_f="EDF5FF", blue_l="548BDD",
         yel_f="FFF8E4", yel_l="FF861B", grn_f="ECF2CD", grn_l="987019", org_f="FFD4B1", org_l="FF6C14",
         s2_f="FFF1D8", s2_l="F7AB56", s1_f="E8F1FD", s1_l="7FA7DE", white="FFFFFF", lora="E96D29",
         stage1="3B6FB6", stage2="B4561A", film="F08A20", film_f="FFF0D7",
         unet_f="8BB7F4", unet_l="3871B3", pn_f="8CE5F6", pn_l="009DD6", mlp_f="C3DF94", mlp_l="589226",
         cond_f="DBED9E", cond_l="9DAF32", panel_f="F4F9FD", panel_l="9DBBD8", env_f="EEF6F3", env_l="85B5B3",
         aligned="BFC2C3", executed="4AD3D5", planned="B0CEFA", teal="1A7F72", frozen="DCE3EE")


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def runs_xml(runs, size, color, bold=False, italic=False):
    out = []
    for text, flags in runs:
        b = "1" if (bold or "b" in flags) else "0"
        it = "1" if (italic or "i" in flags) else "0"
        base = ' baseline="-25000"' if "sub" in flags else (' baseline="30000"' if "sup" in flags else "")
        out.append(
            f'<a:r><a:rPr lang="en-US" sz="{int(round(size * 100))}" b="{b}" i="{it}"{base} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:rPr>'
            f'<a:t>{_esc(text)}</a:t></a:r>')
    return "".join(out)


def P(*parts):
    """快捷构造段落：P("text", ("Z","i"), ("t","i sub"))。"""
    return [(p, "") if isinstance(p, str) else p for p in parts]


class Canvas:
    def __init__(self, slide):
        self.tree = slide.shapes._spTree
        self._id = max([int(e.get("id")) for e in self.tree.iter(PN + "cNvPr")] + [1]) + 1

    def nid(self):
        self._id += 1
        return self._id

    def _add(self, xml):
        el = etree.fromstring(xml)
        self.tree.append(el)
        return el

    # ---- 文字 ----
    def text(self, x, y, w, h, paras, size=11, color=C["ink"], bold=False, italic=False, align="ctr",
             anchor="ctr", wrap="none", rot=0, name="Text"):
        if paras and isinstance(paras[0], tuple):
            paras = [paras]
        ps = "".join(f'<a:p><a:pPr algn="{align}"/>{runs_xml(r, size, color, bold, italic)}</a:p>' for r in paras)
        r = f' rot="{int(rot * 60000)}"' if rot else ""
        return self._add(
            f'<p:sp xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="{self.nid()}" name="{name}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm{r}><a:off x="{int(x * MM)}" y="{int(y * MM)}"/>'
            f'<a:ext cx="{int(w * MM)}" cy="{int(h * MM)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="{wrap}" lIns="0" tIns="0" rIns="0" bIns="0" '
            f'anchor="{anchor}" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>{ps}</p:txBody></p:sp>')

    # ---- 形状 ----
    def shape(self, prst, x, y, w, h, fill=None, line=C["grey"], lw=0.75, dash=None, adj=None, paras=None,
              size=11, color=C["ink"], bold=False, italic=False, name="Shape", flipH=False, flipV=False, rot=0,
              wrap="square"):
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
        ln = ("<a:ln><a:noFill/></a:ln>" if line is None else
              f'<a:ln w="{int(lw * 12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>'
              + (f'<a:prstDash val="{dash}"/>' if dash else "") + "</a:ln>")
        av = "".join(f'<a:gd name="{k}" fmla="val {int(v)}"/>' for k, v in (adj or {}).items())
        fl = (' flipH="1"' if flipH else "") + (' flipV="1"' if flipV else "") + (f' rot="{int(rot * 60000)}"' if rot else "")
        if paras:
            if isinstance(paras[0], tuple):
                paras = [paras]
            ps = "".join(f'<a:p><a:pPr algn="ctr"/>{runs_xml(r, size, color, bold, italic)}</a:p>' for r in paras)
        else:
            ps = '<a:p><a:endParaRPr lang="en-US"/></a:p>'
        return self._add(
            f'<p:sp xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="{self.nid()}" name="{name}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm{fl}><a:off x="{int(x * MM)}" y="{int(y * MM)}"/>'
            f'<a:ext cx="{int(w * MM)}" cy="{int(h * MM)}"/></a:xfrm><a:prstGeom prst="{prst}"><a:avLst>{av}</a:avLst>'
            f'</a:prstGeom>{fill_xml}{ln}</p:spPr><p:txBody><a:bodyPr wrap="{wrap}" lIns="18000" tIns="0" '
            f'rIns="18000" bIns="0" anchor="ctr" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>{ps}</p:txBody></p:sp>')

    def box(self, x, y, w, h, fill=C["white"], line=C["grey"], lw=0.75, dash=None, r=0.12, **kw):
        return self.shape("roundRect", x, y, w, h, fill, line, lw, dash, {"adj": r * 100000}, **kw)

    def rect(self, x, y, w, h, fill=C["white"], line=C["grey"], lw=0.75, dash=None, **kw):
        return self.shape("rect", x, y, w, h, fill, line, lw, dash, **kw)

    def circle(self, cx, cy, r, fill=C["white"], line=C["grey"], lw=0.75, **kw):
        return self.shape("ellipse", cx - r, cy - r, 2 * r, 2 * r, fill, line, lw, **kw)

    # ---- 线 ----
    def path(self, segs, color=C["arrow"], lw=1.5, head=False, tail=True, dash=None, name="Line", size="med"):
        """segs: [('M',(x,y)),('L',(x,y)),('C',p1,p2,p3)]，单位mm。"""
        pts = [p for s in segs for p in s[1:]]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, y0 = min(xs), min(ys)
        w, h = max(max(xs) - x0, 0.01), max(max(ys) - y0, 0.01)

        def pt(p):
            return f'<a:pt x="{int((p[0] - x0) * MM)}" y="{int((p[1] - y0) * MM)}"/>'
        body = "".join(
            f"<a:moveTo>{pt(s[1])}</a:moveTo>" if s[0] == "M" else
            f"<a:lnTo>{pt(s[1])}</a:lnTo>" if s[0] == "L" else
            f"<a:cubicBezTo>{pt(s[1])}{pt(s[2])}{pt(s[3])}</a:cubicBezTo>" for s in segs)
        he = f'<a:headEnd type="triangle" w="{size}" len="{size}"/>' if head else ""
        te = f'<a:tailEnd type="triangle" w="{size}" len="{size}"/>' if tail else ""
        d = f'<a:prstDash val="{dash}"/>' if dash else ""
        W, H = int(w * MM), int(h * MM)
        return self._add(
            f'<p:sp xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="{self.nid()}" name="{name}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x0 * MM)}" y="{int(y0 * MM)}"/>'
            f'<a:ext cx="{W}" cy="{H}"/></a:xfrm><a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>'
            f'<a:rect l="0" t="0" r="r" b="b"/><a:pathLst><a:path w="{W}" h="{H}" fill="none">{body}</a:path>'
            f'</a:pathLst></a:custGeom><a:noFill/><a:ln w="{int(lw * 12700)}" cap="flat"><a:solidFill>'
            f'<a:srgbClr val="{color}"/></a:solidFill>{d}<a:miter lim="800000"/>{he}{te}</a:ln></p:spPr></p:sp>')

    def arrow(self, points, color=C["arrow"], lw=1.5, tail=True, head=False, dash=None, size="med"):
        segs = [("M", points[0])] + [("L", p) for p in points[1:]]
        return self.path(segs, color, lw, head=head, tail=tail, dash=dash, size=size)

    def line(self, points, color=C["grey"], lw=0.75, dash=None):
        return self.arrow(points, color, lw, tail=False, dash=dash)

    def arc(self, p0, p1, lift, color=C["lgrey"], lw=1.0, dash="dash", tail=True):
        """p0 → p1 的上拱曲线，lift 为拱高（mm，正数向上）。"""
        (x0, y0), (x1, y1) = p0, p1
        c1 = (x0 + (x1 - x0) * 0.15, min(y0, y1) - lift)
        c2 = (x1 - (x1 - x0) * 0.15, min(y0, y1) - lift)
        return self.path([("M", p0), ("C", c1, c2, p1)], color, lw, tail=tail, dash=dash, size="sm")

    def bracket(self, x0, x1, y, down=True, color=C["grey"], lw=0.75, tick=1.6):
        t = tick if down else -tick
        return self.line([(x0, y - t), (x0, y), (x1, y), (x1, y - t)], color, lw)


def new_blank_slide(prs, layout_name="空白"):
    layout = next((l for l in prs.slide_layouts if l.name == layout_name), prs.slide_layouts[6])
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text
