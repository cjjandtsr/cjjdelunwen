"""Append the 11-09 redraws (Fig. 4 whole, Fig. 5(a)) as new slides to a deck. Usage: in.pptx out.pptx"""
import sys, os
from pptx import Presentation
import fig4d_ppt, fig5a_ppt
HERE = os.path.dirname(os.path.abspath(__file__))
p = Presentation(sys.argv[1])
lay = p.slides[-1].slide_layout
s = p.slides.add_slide(lay); fig4d_ppt.build(s, os.path.join(HERE, "obs_frames.png"))
s = p.slides.add_slide(lay); fig5a_ppt.build(s, oy=4)
p.save(sys.argv[2])
