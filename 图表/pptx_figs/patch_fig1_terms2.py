"""Slide 1 (Fig. 1): shorten rollout label; 'space' -> 'detour' in the reward list."""
import sys
from pptx import Presentation
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src); s = prs.slides[0]
def all_shapes(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6: yield from all_shapes(sh.shapes)
n = 0
for sh in all_shapes(s.shapes):
    if not sh.has_text_frame: continue
    for r in [r for pa in sh.text_frame.paragraphs for r in pa.runs]:
        if r.text == "(4 executed steps, reward ": r.text = "(step reward "; n += 1
        elif r.text.strip() == "space" and "Reward" in sh.text_frame.text: r.text = r.text.replace("space", "detour"); n += 1
prs.save(dst); print("replaced", n)
