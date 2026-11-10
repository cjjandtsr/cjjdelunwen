"""Fig. 1: condition bar [c_t, k] to the condition colour used in Figs. 2 and 4; drop extra slides after slide 5."""
import sys
from pptx import Presentation
from pptx.dml.color import RGBColor
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
def all_shapes(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6: yield from all_shapes(sh.shapes)
n = 0
for sh in all_shapes(prs.slides[0].shapes):
    if sh.shape_id == 425:
        sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string("FBE3D2")
        sh.line.color.rgb = RGBColor.from_string("D9925E"); n += 1
    if sh.shape_id == 444 and sh.has_text_frame:
        for pa in sh.text_frame.paragraphs:
            for r in pa.runs: r.font.color.rgb = RGBColor.from_string("8A4B22")
while len(prs.slides) > 5:
    sid = prs.slides._sldIdLst[-1]; prs.part.drop_rel(sid.rId); prs.slides._sldIdLst.remove(sid)
prs.save(dst); print("condition bar recoloured:", n, "slides:", len(prs.slides))
