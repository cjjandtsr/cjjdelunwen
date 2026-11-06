"""Slide 1 (Fig. 1): replace project-internal labels with generic terms (in place on a deck)."""
import sys
from pptx import Presentation
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src); s = prs.slides[0]
def all_shapes(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6: yield from all_shapes(sh.shapes)
REP = {106: [(" · PPO + success retention · 128 updates", " · PPO + BC regularization · 128 updates")],
       111: [("Fixed successful-prefix reference bank", "Fixed successful-trajectory buffer")],
       116: [("(H4, reward ", "(4 executed steps, reward ")],
       343: [("H4 executed", "executed prefix")],
       344: [("H8 risk window", "planning window")],
       345: [("execute H4,", "execute 4 steps,")],
       151: [("keep", "reg")]}
done = []
for sh in all_shapes(s.shapes):
    if sh.shape_id in REP and sh.has_text_frame:
        for r in [r for pa in sh.text_frame.paragraphs for r in pa.runs]:
            for a, b in REP[sh.shape_id]:
                if r.text == a:
                    r.text = b; done.append((sh.shape_id, a, b))
prs.save(dst)
for d in done: print(d)
assert len(done) == 7, "not all replacements applied"
