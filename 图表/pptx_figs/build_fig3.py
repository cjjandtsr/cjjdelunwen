"""Append Figure 3 variants (slide 4: curve, slide 5: rings) to a deck."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx import Presentation
import fig3_ppt
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
while len(prs.slides) > 3:
    rid = prs.slides._sldIdLst[-1].rId; prs.part.drop_rel(rid); prs.slides._sldIdLst.remove(prs.slides._sldIdLst[-1])
blank = [l for l in prs.slide_layouts if l.name == "Blank"][0]
for v in ("curve", "rings"):
    s = prs.slides.add_slide(blank)
    _, Q, rho = fig3_ppt.build(s, v)
print("q_m =", [round(q, 4) for q in Q], "rho =", round(rho, 4))
prs.save(dst); print("saved", dst)
