"""Append the data-free evaluation-setting figure as slide 6."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx import Presentation
import fig_setup_ppt
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
while len(prs.slides) > 5:
    sid = prs.slides._sldIdLst[-1]; prs.part.drop_rel(sid.rId); prs.slides._sldIdLst.remove(sid)
blank = [l for l in prs.slide_layouts if l.name == "Blank"][0]
fig_setup_ppt.build(prs.slides.add_slide(blank), oy=20)
prs.save(dst); print("slides:", len(prs.slides))
