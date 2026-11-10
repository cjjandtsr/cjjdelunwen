"""Append an alternative-layout Figure 2 (Enhancing palette) as the last slide."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx import Presentation
import fig2b_ppt
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
blank = [l for l in prs.slide_layouts if l.name == "Blank"][0]
s = prs.slides.add_slide(blank)
fig2b_ppt.use_enhancing(); fig2b_ppt.build(s)
prs.save(dst); print("added alternative Fig. 2 as slide", len(prs.slides))
