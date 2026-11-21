"""Append Fig. 4 v-e (slide-3 skeleton + slide-7 content) as a new slide. Usage: in.pptx out.pptx"""
import sys, os
from pptx import Presentation
import fig4e_ppt
HERE = os.path.dirname(os.path.abspath(__file__))
p = Presentation(sys.argv[1])
s = p.slides.add_slide(p.slides[-1].slide_layout)
fig4e_ppt.build(s, os.path.join(HERE, "obs_frames.png"))
p.save(sys.argv[2])
