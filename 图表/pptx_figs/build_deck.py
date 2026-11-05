import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx import Presentation
import fig2_ppt

src, dst = sys.argv[1], sys.argv[2]
which = sys.argv[3:] or ["2", "3"]
prs = Presentation(src)


def clear(slide):
    tree = slide.shapes._spTree
    for el in list(tree):
        if el.tag.endswith("}sp") or el.tag.endswith("}grpSp") or el.tag.endswith("}pic") or el.tag.endswith("}cxnSp") or el.tag.endswith("}graphicFrame"):
            tree.remove(el)


if "2" in which:
    s = prs.slides[1]; clear(s); fig2_ppt.build(s)
if "3" in which:
    import fig4_ppt
    s = prs.slides[2]; clear(s); fig4_ppt.build(s)
prs.save(dst)
print("saved", dst)
