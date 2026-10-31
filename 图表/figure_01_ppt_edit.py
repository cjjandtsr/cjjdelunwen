"""按《论文配图总体方案v3.1》§3.1修改用户的图1 PPT（不改原文件）。

输入：图表/Local Point Cloud-状态历史-编码条件.pptx 的第2页（带 Time embedding 圆圈的最新版）
输出：图表/figure_01_v3.1.pptx（只含修改后的一页，全部为可编辑的PowerPoint对象）

python 图表/figure_01_ppt_edit.py

主要改动：
- 删除顶部总标题；Observation Space → Observation；符号统一为 ψ、‖g_b‖₂、s_τ、c_t、Z_t^K 等。
- 策略面板只写模块名：去掉 64-D/128-D/576-D、Time embedding、Skip connections/Encoder/Bottleneck/Decoder、X0 prediction 框。
- 底部 DPPO 面板重画为两阶段训练：Stage 1 BC 预训练 + Stage 2 DPPO 链条（rollouts → critic → advantage → PPO → LoRA），
  原来的两条去噪链移到图3，GAE/概率比/价值回归等计算细节移到算法1。
- Receding 面板图例去掉 "token" 说法。
- 回环线加标注 "execute H4, observe, replan"；Environment → Policy 箭头标 o_τ。
- 所有连接线转为普通折线/曲线（custGeom），PowerPoint、WPS 和 LibreOffice 显示一致。
- 新文字不小于 10.5 pt（整图按 190 mm 宽印刷时约 6 pt）。
"""
import copy
import math
from pathlib import Path

from lxml import etree
from pptx import Presentation

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "Local Point Cloud-状态历史-编码条件.pptx"
OUT = ROOT / "figure_01_v3.1.pptx"
SLIDE_INDEX = 1  # 第2页

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
A = "{%s}" % NS["a"]
PN = "{%s}" % NS["p"]
MM = 36000  # EMU per mm
FONT = "Times New Roman"

# 原图配色（取自PPT中的形状）
C = dict(ink="0B1020", grey="555B63", arrow="5997FF", blue_f="EDF5FF", blue_l="548BDD",
         yel_f="FFF8E4", yel_l="FF861B", grn_f="ECF2CD", grn_l="987019", org_f="FFD4B1", org_l="FF6C14",
         s2_f="FFF1D8", s2_l="F7AB56", s1_f="E8F1FD", s1_l="7FA7DE", white="FFFFFF", lora="E96D29",
         stage1="3B6FB6")

prs = Presentation(str(SRC))
# 只保留第2页
sldIdLst = prs.slides._sldIdLst
for i, sldId in reversed(list(enumerate(list(sldIdLst)))):
    if i != SLIDE_INDEX:
        prs.part.drop_rel(sldId.rId)
        sldIdLst.remove(sldId)
slide = prs.slides[0]
tree = slide.shapes._spTree
_next_id = [max(int(e.get("id")) for e in tree.iter(PN + "cNvPr")) + 1]


def nid():
    _next_id[0] += 1
    return _next_id[0]


def find(sid):
    for e in tree.iter(PN + "cNvPr"):
        if e.get("id") == str(sid):
            el = e.getparent().getparent()
            return el
    raise KeyError(sid)


def delete(*sids):
    for s in sids:
        el = find(s)
        el.getparent().remove(el)


def xfrm_of(el):
    return el.find(".//" + A + "xfrm")


# ---------------- 文字 ----------------
def _runs_xml(runs, size, color, bold=False, italic=False):
    """runs: [(text, flags)]，flags 可含 b i sub sup。"""
    out = []
    for text, flags in runs:
        b = "1" if (bold or "b" in flags) else "0"
        it = "1" if (italic or "i" in flags) else "0"
        base = ' baseline="-25000"' if "sub" in flags else (' baseline="30000"' if "sup" in flags else "")
        out.append(
            f'<a:r><a:rPr lang="en-US" sz="{int(size * 100)}" b="{b}" i="{it}"{base} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:rPr>'
            f'<a:t>{_esc(text)}</a:t></a:r>')
    return "".join(out)


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def textbox_xml(x, y, w, h, paras, size=11, color=C["ink"], bold=False, italic=False, align="ctr",
                anchor="ctr", wrap="none", name="Text"):
    ps = "".join(f'<a:p><a:pPr algn="{align}"/>{_runs_xml(r, size, color, bold, italic)}</a:p>' for r in paras)
    return (f'<p:sp xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="{nid()}" name="{name}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x)}" y="{int(y)}"/>'
            f'<a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="{wrap}" lIns="0" tIns="0" rIns="0" bIns="0" '
            f'anchor="{anchor}" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>{ps}</p:txBody></p:sp>')


def add_text_mm(x, y, w, h, paras, parent=None, **kw):
    el = etree.fromstring(textbox_xml(x * MM, y * MM, w * MM, h * MM, paras, **kw))
    (parent if parent is not None else tree).append(el)
    return el


def replace_text(sid, paras, pad_mm=(0, 0), shift_mm=(0, 0), **kw):
    """用可编辑文本框替换文字图片/旧文本框：位置取原对象（组内对象用组内坐标），字号由 kw 指定。"""
    el = find(sid)
    xf = xfrm_of(el)
    off, ext = xf.find(A + "off"), xf.find(A + "ext")
    x, y, w, h = (int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy")))
    parent = el.getparent()
    # 组内坐标：把 mm 的扩边换算到组内单位
    sx = sy = MM
    g = parent.getparent()
    if parent.tag == PN + "grpSp":
        gx = parent.find(PN + "grpSpPr").find(A + "xfrm")
        sx = MM * int(gx.find(A + "chExt").get("cx")) / int(gx.find(A + "ext").get("cx"))
        sy = MM * int(gx.find(A + "chExt").get("cy")) / int(gx.find(A + "ext").get("cy"))
    dx, dy = pad_mm[0] * sx, pad_mm[1] * sy
    x, y = x + shift_mm[0] * sx, y + shift_mm[1] * sy
    new = etree.fromstring(textbox_xml(x - dx, y - dy, w + 2 * dx, h + 2 * dy, paras, **kw))
    parent.replace(el, new)
    return new


# ---------------- 形状与线 ----------------
def rect_mm(x, y, w, h, fill, line, lw_pt=0.75, dash=None, radius=0.12, name="Box"):
    d = f'<a:prstDash val="{dash}"/>' if dash else ""
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    xml = (f'<p:sp xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="{nid()}" name="{name}"/>'
           f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x * MM)}" y="{int(y * MM)}"/>'
           f'<a:ext cx="{int(w * MM)}" cy="{int(h * MM)}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst>'
           f'<a:gd name="adj" fmla="val {int(radius * 100000)}"/></a:avLst></a:prstGeom>{fill_xml}'
           f'<a:ln w="{int(lw_pt * 12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>{d}</a:ln>'
           f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US"/></a:p></p:txBody></p:sp>')
    el = etree.fromstring(xml)
    tree.append(el)
    return el


def path_xml(pts_emu, segs, color, lw_pt, head=False, tail=True, dash=None, name="Arrow", tag="sp"):
    """pts_emu: 绝对坐标点列；segs: [('M',p)|('L',p)|('C',p1,p2,p3)]，点为 (x,y) EMU。"""
    xs = [p[0] for p in pts_emu]
    ys = [p[1] for p in pts_emu]
    x0, y0 = min(xs), min(ys)
    w, h = max(max(xs) - x0, 1), max(max(ys) - y0, 1)

    def pt(p):
        return f'<a:pt x="{int(p[0] - x0)}" y="{int(p[1] - y0)}"/>'
    body = []
    for s in segs:
        if s[0] == "M":
            body.append(f"<a:moveTo>{pt(s[1])}</a:moveTo>")
        elif s[0] == "L":
            body.append(f"<a:lnTo>{pt(s[1])}</a:lnTo>")
        else:
            body.append(f"<a:cubicBezTo>{pt(s[1])}{pt(s[2])}{pt(s[3])}</a:cubicBezTo>")
    he = '<a:headEnd type="triangle" w="med" len="med"/>' if head else ""
    te = '<a:tailEnd type="triangle" w="med" len="med"/>' if tail else ""
    d = f'<a:prstDash val="{dash}"/>' if dash else ""
    return (f'<p:{tag} xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="{nid()}" name="{name}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x0)}" y="{int(y0)}"/>'
            f'<a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm><a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>'
            f'<a:rect l="0" t="0" r="r" b="b"/><a:pathLst><a:path w="{int(w)}" h="{int(h)}" fill="none">'
            f'{"".join(body)}</a:path></a:pathLst></a:custGeom><a:noFill/>'
            f'<a:ln w="{int(lw_pt * 12700)}" cap="flat"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{d}'
            f'<a:miter lim="800000"/>{he}{te}</a:ln></p:spPr></p:{tag}>')


def arrow_mm(points, color=C["arrow"], lw=1.5, **kw):
    pts = [(x * MM, y * MM) for x, y in points]
    segs = [("M", pts[0])] + [("L", p) for p in pts[1:]]
    el = etree.fromstring(path_xml(pts, segs, color, lw, **kw))
    tree.append(el)
    return el


# ---------------- 连接线 → 折线/曲线 ----------------
def connector_points(prst, w, h, adj):
    """返回局部坐标下的路径段（OOXML presetShapeDefinitions）。"""
    if prst in ("line", "straightConnector1"):
        return [("M", (0, 0)), ("L", (w, h))]
    if prst == "bentConnector2":
        return [("M", (0, 0)), ("L", (w, 0)), ("L", (w, h))]
    if prst == "bentConnector3":
        x1 = w * adj.get("adj1", 50000) / 100000
        return [("M", (0, 0)), ("L", (x1, 0)), ("L", (x1, h)), ("L", (w, h))]
    if prst == "bentConnector4":
        x1 = w * adj.get("adj1", 50000) / 100000
        y2 = h * adj.get("adj2", 50000) / 100000
        return [("M", (0, 0)), ("L", (x1, 0)), ("L", (x1, y2)), ("L", (w, y2)), ("L", (w, h))]
    if prst == "curvedConnector3":
        x2 = w * adj.get("adj1", 50000) / 100000
        x1, x3, y3 = x2 / 2, (w + x2) / 2, h * 3 / 4
        return [("M", (0, 0)), ("C", (x1, 0), (x2, h / 4), (x2, h / 2)), ("C", (x2, y3), (x3, h), (w, h))]
    raise ValueError(prst)


def flatten_connector(el):
    sppr = el.find(PN + "spPr")
    xf = sppr.find(A + "xfrm")
    geom = sppr.find(A + "prstGeom")
    if geom is None:
        return
    off, ext = xf.find(A + "off"), xf.find(A + "ext")
    ox, oy, w, h = (int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy")))
    rot = int(xf.get("rot", "0")) / 60000.0
    fh, fv = xf.get("flipH") == "1", xf.get("flipV") == "1"
    adj = {g.get("name"): int(g.get("fmla").split()[1]) for g in geom.iter(A + "gd")}
    segs = connector_points(geom.get("prst"), w, h, adj)
    cx, cy = w / 2, h / 2
    th = math.radians(rot)

    def T(p):
        x, y = p
        if fh:
            x = w - x
        if fv:
            y = h - y
        dx, dy = x - cx, y - cy
        return (ox + cx + dx * math.cos(th) - dy * math.sin(th), oy + cy + dx * math.sin(th) + dy * math.cos(th))
    segs = [(s[0],) + tuple(T(p) for p in s[1:]) for s in segs]
    pts = [p for s in segs for p in s[1:]]
    ln = sppr.find(A + "ln")
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    W, H = max(max(xs) - x0, 1), max(max(ys) - y0, 1)
    xf.attrib.pop("rot", None); xf.attrib.pop("flipH", None); xf.attrib.pop("flipV", None)
    off.set("x", str(int(x0))); off.set("y", str(int(y0)))
    ext.set("cx", str(int(W))); ext.set("cy", str(int(H)))

    def pt(p):
        return f'<a:pt x="{int(p[0] - x0)}" y="{int(p[1] - y0)}"/>'
    body = "".join(
        f"<a:moveTo>{pt(s[1])}</a:moveTo>" if s[0] == "M" else
        f"<a:lnTo>{pt(s[1])}</a:lnTo>" if s[0] == "L" else
        f"<a:cubicBezTo>{pt(s[1])}{pt(s[2])}{pt(s[3])}</a:cubicBezTo>" for s in segs)
    cg = etree.fromstring(
        f'<a:custGeom xmlns:a="{NS["a"]}"><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
        f'<a:pathLst><a:path w="{int(W)}" h="{int(H)}" fill="none">{body}</a:path></a:pathLst></a:custGeom>')
    sppr.replace(geom, cg)
    # 去掉吸附关系，避免PowerPoint按吸附点重新布线
    # LibreOffice 会把 cxnSp 按端点重新布线、忽略 custGeom，所以改成普通形状 p:sp
    nv = el.find(PN + "nvCxnSpPr")
    cnvpr = copy.deepcopy(nv.find(PN + "cNvPr"))
    sp = etree.Element(PN + "sp")
    nvsp = etree.SubElement(sp, PN + "nvSpPr")
    nvsp.append(cnvpr)
    etree.SubElement(nvsp, PN + "cNvSpPr")
    etree.SubElement(nvsp, PN + "nvPr")
    sp.append(sppr)
    st = el.find(PN + "style")
    if st is not None:
        sp.append(st)
    el.getparent().replace(el, sp)
    return segs


# =====================================================================
# 1 全图：删除总标题
delete(8, 9)

# 2 Observation 面板（组 715 内）
replace_text(13, [[("Observation", "")]], size=20, bold=True, anchor="t")
replace_text(62, [[("d", "i"), (" = ‖", ""), ("g", "i"), ("b", "i sub"), ("‖", ""), ("2", "sub")]], size=14)
replace_text(78, [[("p", "i"), (", sin ", ""), ("ψ", "i"), (", cos ", ""), ("ψ", "i")]], size=13)

# 3 策略面板
replace_text(671, [[("State history", "")]], size=11, align="l")
replace_text(676, [[("Point-cloud", "")], [("history", "")]], size=11, align="l", wrap="square")
for sid, sub in ((681, "τ−2"), (682, "τ−1"), (683, "τ")):
    replace_text(sid, [[("s", "i"), (sub, "i sub")]], size=10)
replace_text(136, [[("State MLP", "")]], size=13)        # 去掉 64-D
replace_text(157, [[("PointNet", "")]], size=13)         # 去掉 128-D
replace_text(677, [[("c", "i"), ("t", "i sub")]], size=16, bold=True)  # 去掉 Encoding Condition 576-D
replace_text(185, [[("Noisy trajectory ", ""), ("Z", "i"), ("t", "i sub"), ("K", "i sup")]], size=11.5)
replace_text(190, [[("Diffusion step ", ""), ("k", "i")]], size=12, shift_mm=(0, -0.9))
delete(196)                                              # Time embedding
delete(218, 259, 262, 265)                               # Skip connections / Encoder / Bottleneck / Decoder
replace_text(269, [[("FiLM(", ""), ("c", "i"), ("t", "i sub"), (", ", ""), ("k", "i"), (")", "")]], size=12)
replace_text(287, [[("Frozen backbone", "")]], size=10, align="l", pad_mm=(0, 0.4), shift_mm=(1.0, 0))
replace_text(293, [[("Trainable LoRA", "")]], size=10, align="l", pad_mm=(0, 0.4), shift_mm=(1.0, 0))
delete(693, 298, 306, 307)                               # X0 prediction 框及其箭头
replace_text(692, [[("DDIM × 10", "")]], size=11.5)
replace_text(325, [[("Trajectory ", ""), ("Z", "i"), ("t", "i sub"), ("0", "i sup")]], size=11.5, pad_mm=(4, 0.5))

# 4 Receding 面板（组 722 内）：图例去掉 token；括线下的重复词删除，只留数字
for sid, txt in ((572, "Aligned"), (576, "Executed"), (580, "Planned"), (584, "Unplanned")):
    replace_text(sid, [[(txt, "")]], size=10, align="l", pad_mm=(0, 0.4), shift_mm=(-0.6, 0))
for sid, txt in ((544, "2"), (548, "4"), (552, "4"), (556, "6")):
    replace_text(sid, [[(txt, "")]], size=10.5)
delete(559, 562, 565, 568, 558, 561, 564, 567)

# 5 连接线统一转为折线/曲线（保证各软件显示一致）
for e in list(tree.iter(PN + "cxnSp")):
    flatten_connector(e)
ret = find(721)  # 回环线：Receding → Environment

# 6 底部面板：保留外框（组 723 中的 330），其余重画
grp = find(723)
outer = None
for e in grp.iter(PN + "cNvPr"):
    if e.get("id") == "330":
        outer = e.getparent().getparent()
# 把外框按绝对坐标移到顶层
gx = grp.find(PN + "grpSpPr").find(A + "xfrm")
gox, goy = int(gx.find(A + "off").get("x")), int(gx.find(A + "off").get("y"))
gex, gey = int(gx.find(A + "ext").get("cx")), int(gx.find(A + "ext").get("cy"))
gcx, gcy = int(gx.find(A + "chOff").get("x")), int(gx.find(A + "chOff").get("y"))
gcex, gcey = int(gx.find(A + "chExt").get("cx")), int(gx.find(A + "chExt").get("cy"))
sxg, syg = gex / gcex, gey / gcey
of = outer.find(".//" + A + "xfrm")
o, ex = of.find(A + "off"), of.find(A + "ext")
o.set("x", str(int(gox + (int(o.get("x")) - gcx) * sxg))); o.set("y", str(int(goy + (int(o.get("y")) - gcy) * syg)))
ex.set("cx", str(int(int(ex.get("cx")) * sxg))); ex.set("cy", str(int(int(ex.get("cy")) * syg)))
# 自由多边形的路径坐标是相对 ext 的，path w/h 不变即可随 ext 缩放
tree.replace(grp, outer)
delete(713)  # r(t+1)

PX, PY, PW, PH = 12.4, 115.6, 250.2, 71.8
add_text_mm(PX + 4, PY + 1.2, PW - 8, 8.5, [[("Two-stage training", "")]], size=20, bold=True)

# Stage 1
s1 = (16.0, 126.0, 52.0, 58.0)
rect_mm(*s1, fill=C["s1_f"], line=C["s1_l"], lw_pt=0.75, radius=0.06, name="Stage1 panel")
add_text_mm(s1[0], s1[1] + 1.0, s1[2], 6, [[("Stage 1: BC pre-training", "")]], size=12.5, bold=True,
            color=C["stage1"])
bx, bw = s1[0] + 5, s1[2] - 10
rect_mm(bx, 135.0, bw, 11.0, fill=C["white"], line=C["blue_l"], name="Demos")
add_text_mm(bx, 135.0, bw, 11.0, [[("EGO-Planner demos", "")], [("988 episodes", "")]], size=11.5, wrap="square")
arrow_mm([(s1[0] + s1[2] / 2, 146.2), (s1[0] + s1[2] / 2, 150.6)])
rect_mm(bx, 151.0, bw, 10.0, fill=C["white"], line=C["blue_l"], name="BC loss")
add_text_mm(bx, 151.0, bw, 10.0, [[("L", "i"), ("BC", "sub"), (" + ", ""), ("λ", "i"), ("geo", "sub"), (" ", ""),
                                   ("L", "i"), ("geo", "sub")]], size=12)
arrow_mm([(s1[0] + s1[2] / 2, 161.2), (s1[0] + s1[2] / 2, 165.6)], color=C["stage1"], lw=2.25)
rect_mm(bx, 166.0, bw, 11.0, fill="D6E6FA", line=C["stage1"], lw_pt=1.0, name="Update all")
add_text_mm(bx, 166.0, bw, 11.0, [[("Update all", "")], [("parameters", "")]], size=11.5, wrap="square")

# Stage 1 → Stage 2
arrow_mm([(s1[0] + s1[2] + 0.3, 155.0), (75.6, 155.0)], color=C["grey"], lw=1.5)
add_text_mm(68.3, 148.6, 7.5, 5.5, [[("init.", "")]], size=10.5, color=C["grey"])

# Stage 2
s2 = (76.0, 126.0, 183.5, 58.0)
rect_mm(*s2, fill=C["s2_f"], line=C["s2_l"], lw_pt=0.75, radius=0.06, name="Stage2 panel")
add_text_mm(s2[0], s2[1] + 1.0, s2[2], 6,
            [[("Stage 2: DPPO post-training (encoders and BC-pretrained U-Net frozen)", "")]],
            size=12.5, bold=True, color="B4561A")
boxes = [
    ([[("Closed-loop", "")], [("rollouts", "")], [("(H4, reward ", ""), ("r", "i"), ("t", "i sub"), (")", "")]], C["yel_f"], C["yel_l"]),
    ([[("Critic", "")], [("V", "i"), ("φ", "i sub"), ("(", ""), ("c", "i"), ("t", "i sub"), (", ", ""), ("β", "i"),
                         ("t", "i sub"), (")", "")]], C["blue_f"], C["blue_l"]),
    ([[("Advantage ", ""), ("Â", "i"), ("t", "i sub")], [("(GAE)", "")]], C["yel_f"], C["yel_l"]),
    ([[("Clipped PPO on", "")], [("denoising steps", "")]], C["grn_f"], C["grn_l"]),
    ([[("Update LoRA", "")], [("(policy only)", "")]], C["org_f"], C["org_l"]),
]
bw2, gap, by, bh = 33.0, 3.8, 136.0, 17.0
x = s2[0] + (s2[2] - (5 * bw2 + 4 * gap)) / 2
centers = []
for paras, f, l in boxes:
    rect_mm(x, by, bw2, bh, fill=f, line=l, lw_pt=0.75, name="Stage2 box")
    add_text_mm(x + 0.5, by, bw2 - 1, bh, paras, size=11.5, wrap="square")
    centers.append(x + bw2 / 2)
    x += bw2 + gap
for i in range(4):
    arrow_mm([(centers[i] + bw2 / 2 + 0.2, by + bh / 2), (centers[i + 1] - bw2 / 2 - 0.3, by + bh / 2)])
# LoRA 更新后用于下一轮采样（只在面板内闭合，不跨面板）
yl = by + bh + 6.0
arrow_mm([(centers[4], by + bh + 0.2), (centers[4], yl), (centers[0], yl), (centers[0], by + bh + 0.4)],
         color=C["lora"], lw=2.25)
add_text_mm(centers[1] - 10, yl + 0.8, centers[3] - centers[1] + 20, 5,
            [[("next iteration uses the updated LoRA", "")]], size=11, color="B4561A", italic=True)
add_text_mm(s2[0] + 3, s2[1] + s2[3] - 8.0, s2[2] - 6, 6,
            [[("Log-probabilities of the DDIM steps give the policy gradient; details in Fig. 3 and Algorithm 1.", "")]],
            size=10.5, color=C["grey"], italic=True)

# 7 闭环标注
add_text_mm(173.0, 50.6, 9.0, 5.5, [[("o", "i"), ("τ", "i sub")]], size=13)
# 回环线标注：放在回环线水平段下方
cg = ret.find(".//" + A + "custGeom")
rx = ret.find(".//" + A + "xfrm")
roff = rx.find(A + "off")
ry = None
pts = [(int(p.get("x")), int(p.get("y"))) for p in cg.iter(A + "pt")]
ys = sorted(set(round(p[1] / 1000) for p in pts))
# 取最长水平段
best = None
for i in range(len(pts) - 1):
    (x1, y1), (x2, y2) = pts[i], pts[i + 1]
    if abs(y1 - y2) < 2000:
        L = abs(x2 - x1)
        if best is None or L > best[0]:
            best = (L, min(x1, x2), y1)
if best:
    L, xs0, yy = best
    ax = (int(roff.get("x")) + xs0) / MM
    ay = (int(roff.get("y")) + yy) / MM
    add_text_mm(ax + 4, ay + 0.5, 70, 4.6, [[("execute H4, observe, replan", "")]], size=11, color="2F5597",
                italic=True, align="l", anchor="t")
    print(f"return line horizontal segment: x={ax:.1f}..{ax + L / MM:.1f} mm, y={ay:.1f} mm")

prs.save(str(OUT))
print("saved", OUT)
