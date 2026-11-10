"""2026-11-10 whole-figure consistency patch on the deck (in.pptx out.pptx):
Fig. 1/2 notation (noise has no symbol; output is Z_t), sentence-case panel titles, unified 'frozen in post-training',
Fig. 3(a) legend 'no progress reward' (time penalty and detour cost still apply, Eq. 4), Fig. 4 slide rebuilt from fig4f_ppt."""
import sys, os
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
import fig4f_ppt
HERE = os.path.dirname(os.path.abspath(__file__))
p = Presentation(sys.argv[1])

def walk(shs):
    for sh in shs:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk(sh.shapes)
        else:
            yield sh

def by_id(slide, sid):
    for sh in walk(slide.shapes):
        if sh.shape_id == sid:
            return sh
    raise KeyError(sid)

def set_run(slide, sid, old, new):
    sh = by_id(slide, sid)
    for pa in sh.text_frame.paragraphs:
        for r in pa.runs:
            if r.text == old:
                r.text = new; return
    raise ValueError((sid, old))

def drop(slide, sid):
    el = by_id(slide, sid)._element; el.getparent().remove(el)

s1, s2, s3, s4 = p.slides[0], p.slides[1], p.slides[2], p.slides[3]
# Fig. 1
for sid in (217, 218, 219, 312):
    drop(s1, sid)
set_run(s1, 216, "Noisy trajectory ", "Noisy trajectory")
set_run(s1, 733, "Observation Space", "Observation space")
set_run(s1, 196, "UAV-iDP3 Policy", "UAV-iDP3 policy")
set_run(s1, 313, "Training: UAV-iDP3 Pretraining + Reg-DPPO Post-training", "Training: UAV-iDP3 pretraining + Reg-DPPO post-training")
set_run(s1, 320, "Execution", "execution")
set_run(s1, 291, "frozen after pretraining", "frozen in post-training")
# Fig. 2
for sid in (240, 241):
    drop(s2, sid)
set_run(s2, 239, "Z", "𝒩(0, I)")
by_id(s2, 239).text_frame.word_wrap = False
set_run(s2, 222, "(a) Overall Network Flow", "(a) Overall network flow")
set_run(s2, 320, "(b) Shared Observation Encoder", "(b) Shared observation encoder")
set_run(s2, 457, "(c) One Denoising Call: Conditional 1D U-Net", "(c) One denoising call: conditional 1D U-Net")
set_run(s2, 384, "(d) Conditional Residual Block with LoRA", "(d) Conditional residual block with LoRA")
# Fig. 3 (rings)
set_run(s4, 61, "detour or revisit → no reward, no penalty", "detour or revisit → no progress reward")
# Fig. 4: rebuild slide 3
for sh in list(s3.shapes):
    sh._element.getparent().remove(sh._element)
fig4f_ppt.build(s3, os.path.join(HERE, "obs_frames.png"))
p.save(sys.argv[2])
