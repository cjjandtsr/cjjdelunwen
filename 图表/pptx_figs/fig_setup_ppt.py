"""New Figure (4.1 / 4.4): evaluation setting, data-free.
(a) task difficulty from corridor occupancy (4.1.1): sparse rho = 0, moderate 0 < rho <= rho_med, dense rho > rho_med,
    rho_med = median over training-world tasks, fixed before evaluation;
(b) kinematic closed-loop environment used for training and main evaluation (3.6);
(c) Gazebo + PX4 software-in-the-loop with EGO-Planner as expert reference (4.4).
Facts only from 论文大稿_v3 3.6 and 4.1/4.4; nothing about the number of executed steps in Gazebo (pending)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pp import Fig

S = 8; F = 9.33; TT = 12
PANEL = ("#F5F5F5", "#A9AEB5"); ENV = ("#EFEFEF", "#A9AEB5"); OBS = ("#E7F3DF", "#8DB580"); POL = ("#DBE3EF", "#899DBE")
TRJ = ("#EEF2F8", "#95A9CE"); CTL = ("#E3E3E3", "#8A8F98"); RISK = ("#EDD3D3", "#A65D61")
DARK = "#2F3E5C"; NOTE = "#5A6270"; AR = "#5C6B85"; GREYT = "#3A3F47"
i = lambda s: f"<i>{s}</i>"


def build(slide, oy=30, only_a=False):
    f = Fig(slide, 0, oy)
    seg = lambda x1, y1, x2, y2, color=AR, sw=0.9, head=True, dash=None: f.line(x1, y1, x2, y2, color, sw, head, dash)
    box = lambda x, y, w, h, t, pal, bold=False, color=DARK, dashed=False: f.card(x, y, w, h, t, pal[0], pal[1], S, bold=bold, color=color, dashed=dashed)
    note = lambda x, y, w, t, align="left": f.label(x, y, w, t, fs=S, italic=True, color=NOTE, align=align)

    # ===================== (a) task difficulty =====================
    f.rect(4, 4, 254, 326, *PANEL, radius=6)
    f.label(10, 7, 246, "<b>Task difficulty classes</b>", fs=TT, align="left")
    W = 16.0                                    # px per metre in the main sketch
    SX, GX, Y = 34, 228, 98
    f.rect(SX, Y - W, GX - SX, 2 * W, "#EEF2F8", "#95A9CE", radius=0, dashed=True, lw=0.8)
    seg(SX, Y, GX, Y, color="#6F82A8", sw=0.8, head=False, dash="dash")
    # obstacles: outside, intersecting (overlap shaded), cylinder outside
    f.rect(64, 38, 22, 22, "#D5D9DF", "#8A8F98", radius=1)
    f.rect(120, 64, 22, 30, "#D5D9DF", "#8A8F98", radius=1)
    f.rect(120, Y - W, 22, 94 - (Y - W), RISK[0], RISK[1], radius=0, lw=0.6)
    f.oval(186, 134, 10, fill="#D5D9DF", line="#8A8F98", lw=0.8)
    f.oval(170, 96, 8, fill="#D5D9DF", line="#8A8F98", lw=0.8)
    f.poly([(162, 98), (178, 98), (176.9, 102), (174, 104.9), (170, 106), (166, 104.9), (163.1, 102)], RISK[0], RISK[1], 0.6)
    f.oval(SX, Y, 3.2, fill=DARK, line=DARK); f.oval(GX, Y, 3.2, fill="#FFFFFF", line=DARK, lw=1.0)
    note(SX - 15, Y + W + 2, 30, "start", align="center"); note(GX - 15, Y + W + 2, 30, "goal", align="center")
    seg(238, Y - W, 238, Y + W, color=NOTE, sw=0.7, head=True, dash=None)
    seg(238, Y + W, 238, Y - W, color=NOTE, sw=0.7, head=True, dash=None)
    f.label(240, Y - 5, 20, "2 m", fs=S, align="left", color=NOTE)
    f.label(10, 150, 244, i("ρ") + " = obstacle volume within 1.0 m of the route / volume of that region", fs=S, color=GREYT)
    f.rect(70, 164, 8, 8, RISK[0], RISK[1], radius=0)
    f.label(81, 163, 160, "obstacle volume counted in " + i("ρ"), fs=S, align="left", color=GREYT)
    # three classes
    cls = [("sparse", i("ρ") + " = 0", []),
           ("moderate", "0 < " + i("ρ") + " ≤ " + i("ρ") + "<sub>med</sub>", [(30, 16, 8, 6)]),
           ("dense", i("ρ") + " > " + i("ρ") + "<sub>med</sub>", [(14, 12, 9, 14), (40, 18, 9, 12), (58, 10, 7, 10)])]
    for k, (name, rule, hits) in enumerate(cls):
        x0 = 12 + k * 82; y0 = 190
        f.rect(x0, y0, 76, 84, "#FFFFFF", "#C5C9CF", radius=4)
        cy = y0 + 40
        f.rect(x0 + 6, cy - 9, 64, 18, "#EEF2F8", "#95A9CE", radius=0, dashed=True, lw=0.6)
        seg(x0 + 6, cy, x0 + 70, cy, color="#6F82A8", sw=0.6, head=False, dash="dash")
        f.oval(x0 + 6, cy, 2.2, fill=DARK, line=DARK); f.oval(x0 + 70, cy, 2.2, fill="#FFFFFF", line=DARK, lw=0.8)
        # obstacles away from the corridor
        f.rect(x0 + 14, y0 + 8, 10, 10, "#D5D9DF", "#8A8F98", radius=1)
        f.rect(x0 + 48, y0 + 60, 12, 10, "#D5D9DF", "#8A8F98", radius=1)
        for (dx, dy, w, h) in hits:
            ox, oyy = x0 + 6 + dx, cy - 9 + dy - h / 2
            f.rect(ox, oyy, w, h, "#D5D9DF", "#8A8F98", radius=1)
            top = max(oyy, cy - 9); bot = min(oyy + h, cy + 9)
            if bot > top:
                f.rect(ox, top, w, bot - top, RISK[0], RISK[1], radius=0, lw=0.5)
        f.label(x0, y0 + 86, 76, f"<b>{name}</b><br>{rule}", fs=S, color=GREYT)
    note(10, 306, 244, i("ρ") + "<sub>med</sub> = 0.04623, fixed before evaluation", align="center")

    if only_a:
        return f
    # ===================== (b) kinematic closed loop =====================
    f.rect(264, 4, 450, 150, *PANEL, radius=6)
    f.label(270, 7, 440, "<b>(b) Kinematic closed-loop environment</b> (training and main evaluation)", fs=TT, align="left")
    Y1 = 44; H = 34
    box(272, Y1, 66, H, "world geometry<br>boxes, cylinders", ENV)
    seg(338, Y1 + H / 2, 350, Y1 + H / 2)
    box(351, Y1, 76, H, "synthesized depth<br>point cloud<br>320×240, 60° FOV", OBS)
    seg(427, Y1 + H / 2, 439, Y1 + H / 2)
    box(440, Y1, 70, H, "<b>UAV-iDP3</b><br>(+ Reg-DPPO)", POL)
    seg(510, Y1 + H / 2, 522, Y1 + H / 2)
    box(523, Y1, 74, H, "trajectory 16×11<br>execute prefix", TRJ)
    seg(597, Y1 + H / 2, 609, Y1 + H / 2)
    box(610, Y1, 96, H, "kinematic update<br>of position and yaw", ENV)
    seg(658, Y1 + H, 658, 94)
    box(610, 95, 96, 30, "continuous-path check:<br>collision · ground · arrival", RISK, color="#6B2E33")
    seg(610, 110, 305, 110, head=False)
    seg(305, 110, 305, Y1 + H + 1)
    note(330, 112, 260, "new observation every 0.3 s; replan after the prefix", align="center")
    note(272, 132, 434, "no flight dynamics: the executed path is the planned prefix", align="left")

    # ===================== (c) Gazebo + PX4 SITL =====================
    f.rect(264, 160, 450, 170, *PANEL, radius=6)
    f.label(270, 163, 440, "<b>(c) Gazebo + PX4 software-in-the-loop</b> (Section 4.4)", fs=TT, align="left")
    Y2 = 196
    box(272, Y2, 66, H, "Gazebo world<br>+ depth camera", ENV)
    seg(338, Y2 + H / 2, 350, Y2 + H / 2)
    box(351, Y2, 76, H, "point cloud<br>(body frame)", OBS)
    seg(427, Y2 + H / 2, 439, Y2 + H / 2)
    box(440, Y2, 70, H, "<b>UAV-iDP3</b><br>(+ Reg-DPPO)", POL)
    seg(510, Y2 + H / 2, 522, Y2 + H / 2)
    box(523, Y2, 74, H, "trajectory<br>setpoints", TRJ)
    seg(597, Y2 + H / 2, 609, Y2 + H / 2)
    box(610, Y2, 96, H, "<b>PX4 position<br>controller</b>", CTL, color=GREYT)
    seg(658, Y2 + H, 658, 248)
    box(610, 249, 96, 28, "multirotor dynamics<br>(Gazebo physics)", CTL, color=GREYT)
    # EGO-Planner branch (same depth camera, same controller)
    box(351, 249, 246, 28, "<b>EGO-Planner</b> (expert reference): local map 0.1 m, inflation 0.3 m<br>→ trajectory optimization, speed ≤ 0.5 m/s", ("#FFFFFF", "#8A8F98"), color=GREYT, dashed=True)
    seg(305, Y2 + H, 305, 263, color="#8A8F98", head=False)
    seg(305, 263, 350, 263, color="#8A8F98")
    seg(597, 263, 603, 263, color="#8A8F98", head=False)
    seg(603, 263, 603, Y2 + 26, color="#8A8F98", head=False)
    seg(603, Y2 + 26, 609, Y2 + 26, color="#8A8F98")
    seg(658, 277, 658, 296, head=False)
    seg(658, 296, 290, 296, head=False)
    seg(290, 296, 290, Y2 + H + 1)
    note(330, 298, 300, "state and new depth frame; collision = crash or flip", align="center")
    note(272, 312, 434, "same 40 held-out tasks for the three methods; 240 s limit per flight", align="left")

    # legend
    LY = 336
    items = [(ENV, "environment"), (OBS, "observation"), (POL, "policy"), (TRJ, "trajectory"), (CTL, "control and dynamics"), (RISK, "collision / occupancy")]
    x = 60
    for pal, t in items:
        f.rect(x, LY, 9, 8, pal[0], pal[1], radius=0)
        f.label(x + 12, LY - 1, 140, t, fs=S, align="left")
        x += 12 + len(t) * 3.6 + 18
    return f
