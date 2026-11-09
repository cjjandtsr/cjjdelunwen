"""2026-11-09 text pass on the user's deck (layout unchanged): naming per 大纲 v5 (UAV-iDP3, Reg-DPPO, Stage I/II),
Fig. 2 time-embedding dimension, Fig. 4 header line, Fig. 3 label overlap."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx import Presentation
from pptx.util import Emu
from pp import fill_tf
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
def all_shapes(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6: yield from all_shapes(sh.shapes)
def runs(sh): return [r for pa in sh.text_frame.paragraphs for r in pa.runs]
log = []
def rep_run(slide_i, old, new, exact=True):
    n = 0
    for sh in all_shapes(prs.slides[slide_i].shapes):
        if not sh.has_text_frame: continue
        for r in runs(sh):
            if (r.text == old) if exact else (old in r.text):
                r.text = new if exact else r.text.replace(old, new); n += 1
    log.append(f"slide{slide_i+1}: {old!r} -> {new!r} x{n}")
    return n
# ---- slide 1 (Fig. 1) ----
rep_run(0, "Conditional Diffusion Policy", "UAV-iDP3 Policy")
rep_run(0, "Training: BC Pretraining + Two-stage DPPO Post-training", "Training: UAV-iDP3 Pretraining + Reg-DPPO Post-training")
rep_run(0, "BC pretraining", "Pretraining")
rep_run(0, "Two-stage DPPO post-training", "Reg-DPPO post-training")
rep_run(0, "retention", "regularization", exact=False)
rep_run(0, "Stage 1", "Stage I"); rep_run(0, "Stage 2", "Stage II")
rep_run(0, "128 updates", "128 iterations", exact=False)
rep_run(0, "Fixed successful-trajectory buffer", "Fixed success trajectory library")
# ---- slide 2 (Fig. 2) ----
rep_run(1, "time embedding", "time embedding 128")
rep_run(1, "condition path", "condition / FiLM")
# ---- slide 3 (Fig. 4) ----
rep_run(2, "Stage 1", "Stage I", exact=False); rep_run(2, "Stage 2", "Stage II", exact=False)
for sh in all_shapes(prs.slides[2].shapes):
    if sh.has_text_frame and "post-training samples Gaussian" in sh.text_frame.text:
        i_ = lambda s: f"<i>{s}</i>"
        html = (i_("K") + " = 10 steps; post-training samples Gaussian transitions " + i_("π") + "<sub>" + i_("θ") + "</sub>(" +
                i_("Z") + "<sup>" + i_("k") + "−1</sup> | " + i_("Z") + "<sup>" + i_("k") + "</sup>, " + i_("c") + "<sub>" + i_("t") +
                "</sub>); evaluation uses deterministic DDIM")
        r0 = runs(sh)[0]; size = r0.font.size.pt if r0.font.size else 6.0
        fill_tf(sh.text_frame, html, size, align="left", italic=True, color="#2E4A73", anchor="top", wrap=False)
        log.append("slide3: header line rewritten")
# ---- slides 4-5 (Fig. 3): move 'unexecuted plan 5–8' below the flight line, clear of the obstacle band ----
for si in (3, 4):
    for sh in all_shapes(prs.slides[si].shapes):
        if sh.has_text_frame and sh.text_frame.text.strip() == "executed prefix 1–4":
            ex = sh
    for sh in all_shapes(prs.slides[si].shapes):
        if sh.has_text_frame and sh.text_frame.text.strip() == "unexecuted plan 5–8":
            ex.left = Emu(ex.left - int(8 * 9525)); sh.left = Emu(ex.left + int(49 * 9525)); sh.top = ex.top
            for r in runs(sh): r.text = r.text.replace("unexecuted plan 5–8", "unexecuted 5–8")
            for r in runs(ex): r.text = r.text.replace("executed prefix 1–4", "executed 1–4")
            log.append(f"slide{si+1}: plan label beside prefix label")
prs.save(dst); print("\n".join(log))
