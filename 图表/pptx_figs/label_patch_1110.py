"""2026-11-10 panel labels and Fig. 5 fix on the user's deck (in.pptx out.pptx).
Rule (from Enhancing, X-NavDP, FlowPilot, Fly360, Learning High-Speed Flight and journal style guides):
panel labels only where the text cites sub-panels (Fig. 2, 3, 4); label + short title on one line at the panel's top left;
Fig. 1 and Fig. 5 keep module / class names without labels.
Fig. 5: sparse class restored to ρ = 0 (Table 3 note); the two obstacles the edit placed inside R in the sparse panel are
recoloured as ordinary obstacles and moved away from R."""
import sys, copy
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
E = 9525
p = Presentation(sys.argv[1])

def walk(shs):
    for sh in shs:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk(sh.shapes)
        else:
            yield sh

def get(slide, sid):
    for sh in walk(slide.shapes):
        if sh.shape_id == sid:
            return sh
    raise KeyError(sid)

def title(slide, sid, left, top, width, text=None):
    sh = get(slide, sid)
    sh.left, sh.top, sh.width = Emu(left * E), Emu(top * E), Emu(width * E)
    pa = sh.text_frame.paragraphs[0]
    pa.alignment = PP_ALIGN.LEFT
    if text is not None:
        pa.runs[0].text = text
        for r in pa.runs[1:]:
            r.text = ""

def new_label(slide, left, top, text, size=9):
    tb = slide.shapes.add_textbox(Emu(left * E), Emu(top * E), Emu(40 * E), Emu(14 * E))
    tf = tb.text_frame; tf.word_wrap = False
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    r = tf.paragraphs[0].add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = True; r.font.name = "Times New Roman"
    from pptx.dml.color import RGBColor
    r.font.color.rgb = RGBColor(0x2F, 0x3E, 0x5C)

s2, s3, s4, s5 = p.slides[1], p.slides[2], p.slides[3], p.slides[4]
# Fig. 2: labels + titles at top left of each panel
title(s2, 222, 16, 27, 400)
title(s2, 320, 16, 151, 200)
for sid in (321, 322):                      # lock after the (b) title
    sh = get(s2, sid); sh.left = Emu(sh.left - 51 * E)
title(s2, 457, 316, 151, 390)
title(s2, 384, 316, 295, 390)
# Fig. 3: short titles, top left
title(s4, 3, 12, 7, 300, "(a) Progress reward")
title(s4, 63, 336, 7, 300, "(b) Planning risk")
# Fig. 4: move (a)/(b) to the top left of the side column
for sid, y in ((4, 10), (81, 160)):
    sh = get(s3, sid)
    p0 = sh.text_frame.paragraphs[0]._p
    p0.getparent().remove(p0)
    new_label(s3, 12, y, "(a)" if sid == 4 else "(b)")
# Fig. 5: sparse class back to ρ = 0
hdr = get(s5, 101)
runs = hdr.text_frame.paragraphs[0].runs
txt = "".join(r.text for r in runs)
assert "0.01" in txt, txt
for r in runs:
    if "0 < ρ ≤ 0.01" in r.text:
        r.text = r.text.replace("0 < ρ ≤ 0.01", "ρ = 0"); break
else:
    # the condition may be split across runs: rebuild after the class name
    keep = runs[0].text.split(",")[0] + ","
    runs[0].text = keep
    for r in runs[1:]:
        r.text = ""
    runs[-1].text = "  ρ = 0"
ref = get(s5, 105)                            # an ordinary obstacle in the sparse panel
for sid, (x, y) in ((124, (30, 48)), (125, (100, 128))):
    sh = get(s5, sid)
    sh.left, sh.top = Emu(x * E), Emu(y * E)
    sh.fill.solid(); sh.fill.fore_color.rgb = ref.fill.fore_color.rgb
    sh.line.color.rgb = ref.line.color.rgb
p.save(sys.argv[2])
