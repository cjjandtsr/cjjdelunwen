"""2026-11-09 (v10): content trim of Figs. 1, 2, 4 after the method-figure review (图表/2026-11-09_图1-4方法图审视_v1_0.md).
Fig. 1: diffusion-step box in condition colour; Reg-DPPO panel reduced to module level (no standard PPO chain,
        no reward list); execution panel shows rolling plans instead of the index strip (index detail lives in Fig. 4).
Fig. 2: separate 'PointNet stage' detail box removed; three-frame concatenation redrawn as one row.
Fig. 4: credit-assignment layer removed; advantage credit and ratio kept as a post-training strip (fig4c_ppt.py)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx import Presentation
from pptx.dml.color import RGBColor
from pp import Fig
from geom import boxes, inside, remove
import fig4c_ppt

src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
S = 8; F = 9.33
FRZ = ("#DBE3EF", "#899DBE"); CONDF = ("#FBE3D2", "#D9925E"); CREAM = ("#FEF1CB", "#AC9A6A"); CREAM2 = ("#F7E3A8", "#817153")
DARK = "#2F3E5C"; BROWN = "#817153"; TXT = "#5E5236"; AR = "#5C6B85"; NOTE = "#5A6270"
i = lambda s: f"<i>{s}</i>"


def clear_region(slide, rect, keep=()):
    n = 0
    for b in sorted(boxes(slide), key=lambda b: -b[5]):
        sh = b[0]
        if sh.shape_id in keep:
            continue
        if inside(b, rect):
            try:
                remove(sh); n += 1
            except Exception:
                pass
    return n


# ---------------- Fig. 1 ----------------
s1 = prs.slides[0]
bx = boxes(s1)
txt = [b for b in bx if getattr(b[0], "has_text_frame", False) and b[0].has_text_frame and "Diffusion step" in b[0].text_frame.text]
if txt:
    _, tx, ty, tw, th, _ = txt[0]
    cands = [b for b in bx if b[0].shape_type == 1 and b[3] > tw and b[1] <= tx and b[2] <= ty and b[1] + b[3] >= tx + tw and b[0] is not txt[0][0]]
    cands.sort(key=lambda b: b[3] * b[4])
    if cands:
        sh = cands[0][0]; sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(CONDF[0][1:])
        sh.line.color.rgb = RGBColor.from_string(CONDF[1][1:])
n1 = clear_region(s1, (120, 279, 540, 389), keep=(10, 316))
n2 = 0  # execution panel kept as drawn by the user (11-09)
f = Fig(s1)
seg = lambda x1, y1, x2, y2, color=AR, sw=0.9, head=True, dash=None: f.line(x1, y1, x2, y2, color, sw, head, dash)
# Reg-DPPO post-training (module level)
f.card(128, 281, 186, 15, "<b>Stage I</b> · PPO · 128 iterations", CREAM[0], CREAM[1], fs=S, color=TXT)
seg(316, 288.5, 329, 288.5, color=BROWN)
f.card(330, 281, 202, 15, "<b>Stage II</b> · PPO + BC regularization · 128 iterations", CREAM2[0], CREAM2[1], fs=S, color=TXT)
f.card(300, 303, 118, 17, "fixed success trajectory library", "#FFFBED", BROWN, fs=S, color=TXT, dashed=True)
f.card(128, 330, 86, 30, "closed-loop rollouts<br>(step reward " + i("r") + "<sub>" + i("t") + "</sub>)", CREAM[0], CREAM[1], fs=F, color="#3A2F1E")
seg(214, 345, 226, 345, color=BROWN)
f.card(227, 330, 112, 30, "PPO with GAE<br>critic " + i("V") + "<sub>" + i("φ") + "</sub>(" + i("c") + "<sub>" + i("t") + "</sub>, " + i("e") + "<sub>" + i("t") + "</sub>)", CREAM[0], CREAM[1], fs=F, color="#3A2F1E")
seg(339, 345, 352, 345, color=BROWN)
f.plus(359, 345, r=6)
seg(359, 320, 359, 338, color=BROWN)
f.label(286, 322, 70, i("λ") + " · BC reg.", fs=S, italic=True, color=TXT, align="right")
seg(365, 345, 378, 345, color=BROWN)
f.card(379, 330, 153, 30, "<b>update LoRA only</b><br>(pretrained weights frozen)", CREAM2[0], CREAM2[1], fs=F, color="#3A2F1E", lw=1.2)
seg(455, 360, 455, 377, color=BROWN, head=False)
seg(455, 377, 171, 377, color=BROWN, head=False)
seg(171, 377, 171, 361, color=BROWN)
f.label(230, 366, 170, "next iteration uses the updated LoRA", fs=S, italic=True, color=TXT)
# ---------------- Fig. 2 ----------------
s2 = prs.slides[1]
n3 = clear_region(s2, (8, 286, 300, 380))
g = Fig(s2)
g.rect(14, 290, 280, 82, "#FFFFFF", "#C5C9CF", radius=4, dashed=True, lw=0.8)
g.label(18, 292, 200, "<b>Three frames, shared weights</b>", fs=S, align="left")
for k, lb in enumerate([i("t") + "−2", i("t") + "−1", i("t")]):
    x = 24 + k * 54
    g.card(x, 310, 46, 26, "frame " + lb + "<br>192", "#FFFFFF", "#899DBE", fs=S, color=DARK)
    g.line(x + 23, 336, x + 23, 350, AR, 0.9, False)
g.line(47, 350, 196, 350, AR, 0.9, False)
g.line(196, 350, 196, 330, AR, 0.9, True)
g.concat_c(196, 323)
g.line(202, 323, 216, 323, AR, 0.9, True)
g.rect(217, 315, 72, 16, FRZ[0], FRZ[1], radius=1)
for k in (1, 2):
    g.line(217 + 24 * k, 315, 217 + 24 * k, 331, FRZ[1], 0.6, False)
g.label(217, 333, 72, "<b>" + i("c<sub>t</sub>") + "</b> 576", fs=S, color=DARK)

# ---------------- Fig. 4 ----------------
s3 = prs.slides[2]
tree = s3.shapes._spTree
for el in list(tree):
    if el.tag.split('}')[1] in ("sp", "grpSp", "pic", "cxnSp", "graphicFrame"):
        tree.remove(el)
fig4c_ppt.build(s3, oy=40)
prs.save(dst)
print("fig1 removed", n1, n2, "| fig2 removed", n3)
