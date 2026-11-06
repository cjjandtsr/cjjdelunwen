# Figure 1, v4: Enhancing / ML-paper style (tinted panels, centred titles, gradient blocks, draw.io palette)
TT = "12px"          # panel titles (9 pt)
BLUEB = ("#EAF0F8", "#8EA7CF")
GREENB = ("#E6EFE8", "#8FB09B")
YELB = ("#FAF2E6", "#CDB089")
ORB = ("#F4E4CC", "#C49E6C")
REDB = ("#EDD3AF", "#B88A52")
FAT = "#AFC2DE"


def ttl(x, y, w, text, fs=TT):
    label(x, y, w, f"<b>{text}</b>", fs=fs)


def fat(x, y, w, h, direction):
    if direction == "right":
        pts = f"0,{h*0.28} {w*0.55},{h*0.28} {w*0.55},0 {w},{h/2} {w*0.55},{h} {w*0.55},{h*0.72} 0,{h*0.72}"
    else:
        pts = f"{w},{h*0.28} {w*0.45},{h*0.28} {w*0.45},0 0,{h/2} {w*0.45},{h} {w*0.45},{h*0.72} {w},{h*0.72}"
    raw(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; overflow: visible">'
        f'<polygon points="{pts}" fill="{FAT}"/></svg>')


def lock(x, y):
    raw(f'<svg width="7" height="9" viewBox="0 0 7 9" role="img" aria-label="frozen" style="position: absolute; left: {x}px; top: {y}px; width: 7px; height: 9px; overflow: visible">'
        '<path d="M1.6 4 V2.6 A1.9 1.9 0 0 1 5.4 2.6 V4" stroke="#2E3B4E" stroke-width="0.9" fill="none"/>'
        '<rect x="0.5" y="4" width="6" height="4.6" rx="0.8" fill="#2E3B4E"/></svg>')


def trap(x, y, w, h, g1, g2, gid, text):
    raw(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; overflow: visible">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient></defs>'
        f'<polygon points="0,0 {w},{h*0.2} {w},{h*0.8} 0,{h}" fill="url(#{gid})" stroke="{g2}" stroke-width="0.6"/></svg>')
    lk = ('<svg width="7" height="9" viewBox="0 0 7 9" role="img" aria-label="frozen" style="display: inline-block; vertical-align: -1px; margin-left: 2px; width: 7px; height: 9px">'
          '<path d="M1.6 4 V2.6 A1.9 1.9 0 0 1 5.4 2.6 V4" stroke="#2E3B4E" stroke-width="0.9" fill="none"/>'
          '<rect x="0.5" y="4" width="6" height="4.6" rx="0.8" fill="#2E3B4E"/></svg>')
    col = "#10301A" if "MLP" in text else "#08303A"
    raw(f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; display: flex; align-items: center; justify-content: center; '
        f'text-align: center; font-size: {F}; line-height: 1.18; color: {col}"><span>{text}{lk}</span></div>')


def swatch(x, y, fi, bo):
    raw(f'<div style="position: absolute; left: {x}px; top: {y}px; width: 7px; height: 7px; box-sizing: border-box; background: {fi}; border: 1px solid {bo}"></div>')


def bx(x, y, w, h, html, pal, fs=F, dashed=False, bold=False):
    card(x, y, w, h, html, fill=pal[0], border=pal[1], fs=fs, dashed=dashed, bold=bold, radius=3)


Zk = lambda sup: i("Z") + "<sub>" + i("t") + "</sub><sup>" + sup + "</sup>"

# =============== (a) Observation ===============
band(8, 8, 192, 214, "#F4F8F5", "#9DBBA9", radius=8)
ttl(8, 11, 192, "Observation")
for (cx, cy) in ((13, 29), (107, 29), (13, 125), (107, 125)):
    band(cx, cy, 88, 92, "#ffffff", "#CFDDD4", radius=4)
label(13, 32, 88, "<b>Local point cloud</b>")
label(107, 32, 88, "<b>Relative goal</b>")
label(13, 128, 88, "<b>UAV state</b>")
label(107, 128, 88, "<b>Three frames</b>")
img(18, 45, 78, 60, "pc", "Local point cloud in the body frame")
label(13, 106, 88, "body frame, 4096 points", fs=S, color="#4A5563")
img(111, 50, 38, 38, "drone", "Quadrotor")
seg(150, 69, 178, 69, color="#1684FF", sw=1.1, dash="3 2")
raw('<div style="position: absolute; left: 179px; top: 64px; width: 10px; height: 10px; border-radius: 50%; background: #F99537; border: 1px solid #DE8131; box-sizing: border-box"></div>')
label(152, 55, 24, i("g<sub>b</sub>"), color="#1666D9")
label(172, 76, 26, "goal", fs=S, color="#B85E10")
label(107, 101, 88, i("d") + " = ‖" + i("g<sub>b</sub>") + "‖<sub>2</sub>")
img(32, 140, 58, 58, "drone", "Quadrotor body frame")
raw('<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" style="position: absolute; left: 16px; top: 170px; width: 24px; height: 24px; overflow: visible">'
    '<path d="M4 20 L4 5" stroke="#1379FF" stroke-width="1" fill="none"/><path d="M2.6 7 L4 4 L5.4 7 Z" fill="#1379FF"/>'
    '<path d="M4 20 L19 20" stroke="#F3212D" stroke-width="1" fill="none"/><path d="M17 18.6 L20 20 L17 21.4 Z" fill="#F3212D"/>'
    '<path d="M4 20 L14 12" stroke="#08983D" stroke-width="1" fill="none"/>'
    '<text x="0" y="4" font-size="7" font-style="italic" fill="#1379FF" font-family="Tinos, serif">z</text>'
    '<text x="20" y="23" font-size="7" font-style="italic" fill="#F3212D" font-family="Tinos, serif">x</text>'
    '<text x="14.5" y="11" font-size="7" font-style="italic" fill="#08983D" font-family="Tinos, serif">y</text></svg>')
label(13, 201, 88, i("p") + ", sin " + i("ψ") + ", cos " + i("ψ"))
img(111, 143, 82, 53, "three", "Point clouds of the last three frames")
label(108, 199, 30, i("τ") + "−2", fs=S)
label(133, 199, 30, i("τ") + "−1", fs=S)
label(164, 199, 30, i("τ"), fs=S)

# =============== (b) Environment ===============
ttl(214, 11, 152, "Environment")
img(216, 29, 148, 99, "env", "Illustrative obstacle environment: UAV, camera field of view and observed points")
raw('<div style="position: absolute; left: 216px; top: 29px; width: 148px; height: 99px; box-sizing: border-box; border: 1px solid #C9CED6; border-radius: 4px"></div>')
# callout: observation is the UAV's own onboard input
raw('<svg width="40" height="214" viewBox="0 0 40 214" aria-hidden="true" style="position: absolute; left: 200px; top: 8px; width: 40px; height: 214px; overflow: visible">'
    '<polygon points="0,14 25,99 25,113 0,210" fill="#7FB09A" fill-opacity="0.12"/>'
    '<path d="M0 14 L25 99" stroke="#5E9C82" stroke-width="0.8" stroke-dasharray="2 1.5" fill="none"/>'
    '<path d="M0 210 L25 113" stroke="#5E9C82" stroke-width="0.8" stroke-dasharray="2 1.5" fill="none"/>'
    '</svg>')
fat(366, 86, 12, 15, "right")
label(364, 72, 16, i("o<sub>τ</sub>"))
label(214, 132, 152, "<b>Local navigation</b>", fs=T)
label(214, 147, 152, "observe · plan · execute", italic=True, color="#3A4452")
label(296, 178, 72, "depth camera,<br>60° FOV, 0.05–10 m", fs=S, align="left", color="#4A5563")

# =============== (c) Conditional diffusion policy ===============
band(380, 8, 330, 214, "#F5F8FC", "#9DB5D8", radius=8)
ttl(380, 11, 330, "Conditional Diffusion Policy")
label(386, 31, 80, "State history", align="left")
for k_, yy in enumerate((45, 60, 75)):
    sub_ = ["−2", "−1", ""][k_]
    bx(390, yy, 34, 12, i("s") + "<sub>" + i("τ") + sub_ + "</sub>", BLUEB, fs=S)
    seg(424, yy + 6, 430, yy + 6, head=False)
seg(430, 51, 430, 81, head=False)
seg(430, 66, 439, 66)
trap(440, 44, 46, 44, "#DCE6F3", "#C9D8EC", "gmlp", "State<br>MLP")
label(386, 96, 90, "Point-cloud history", align="left")
img(384, 109, 50, 32, "three", "Point-cloud history")
label(384, 142, 52, i("τ") + "−2 … " + i("τ"), fs=S)
seg(435, 126, 439, 126)
trap(440, 104, 46, 44, "#DCE6F3", "#C9D8EC", "gpn", "PointNet")
seg(487, 66, 493, 66)
seg(487, 126, 493, 126)
raw('<svg width="16" height="108" viewBox="0 0 16 108" aria-hidden="true" style="position: absolute; left: 494px; top: 42px; width: 16px; height: 108px; overflow: visible">'
    '<defs><linearGradient id="gcat" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B7C9E5"/><stop offset="1" stop-color="#9DB5D8"/></linearGradient></defs>'
    '<rect x="0" y="0" width="16" height="108" rx="3" fill="url(#gcat)" stroke="#6E8DBE" stroke-width="0.6"/>'
    '<text x="8" y="54" font-size="8" fill="#2E4A73" font-weight="700" text-anchor="middle" dominant-baseline="middle" transform="rotate(-90 8 54)" font-family="Tinos, serif">3-frame concat</text></svg>')
label(488, 152, 28, i("c<sub>t</sub>"), fs=T, bold=True)
seg(511, 96, 523, 96)
# noise and step inputs
bx(524, 26, 88, 32, "", BLUEB)
label(524, 28, 88, "Noisy trajectory " + Zk(i("K")))
img(534, 44, 68, 11, "noisy", "Noisy trajectory samples")
bx(618, 26, 86, 32, "", BLUEB)
label(618, 28, 86, "Diffusion step " + i("k"))
raw('<div style="position: absolute; left: 654px; top: 42px; width: 14px; height: 14px; box-sizing: border-box; border-radius: 50%; background: #C9D8EC; border: 1px solid #6E8DBE; display: flex; align-items: center; justify-content: center; font-size: 8px; font-style: italic; color: #1f2328">k</div>')
seg(568, 58, 568, 65)
seg(661, 58, 661, 65)
# U-Net
band(524, 66, 180, 104, "#ffffff", "#9DB5D8", radius=4)
label(524, 69, 180, "<b>Conditional 1D U-Net</b>")
def cube(x, y, w, h, d, front, top, side, stroke):
    return (f'<rect x="{x}" y="{y + d}" width="{w}" height="{h}" fill="{front}" stroke="{stroke}" stroke-width="0.6"/>'
            f'<path d="M{x} {y + d} L{x + d} {y} L{x + w + d} {y} L{x + w} {y + d} Z" fill="{top}" stroke="{stroke}" stroke-width="0.6"/>'
            f'<path d="M{x + w} {y + d} L{x + w + d} {y} L{x + w + d} {y + h} L{x + w} {y + h + d} Z" fill="{side}" stroke="{stroke}" stroke-width="0.6"/>')


BL = ("#B9CCE8", "#DCE6F3", "#93AED6", "#6F8BBA")
OR = ("#F2C3A0", "#F8DCC7", "#E0A77E", "#C98A5E")
u, base, dpt = [], 58, 4
heights = [44, 34, 25, 17]
x = 4
pos_enc, pos_dec, film_x = [], [], []
for hh in heights:
    u.append(cube(x, base - hh - dpt, 9, hh, dpt, *BL)); pos_enc.append((x + 5, base - hh - dpt))
    u.append(cube(x + 13, base - hh * 0.8 - 2, 2.5, hh * 0.8, 2, *OR)); film_x.append(x + 14.25)
    x += 17
u.append(cube(x, base - 9 - dpt, 16, 7, dpt, "#C9D8EC", "#E3EBF6", "#A7BEDF", "#6F8BBA")); mid_c = x + 8
x += 22
for hh in reversed(heights):
    u.append(cube(x, base - hh * 0.8 - 2, 2.5, hh * 0.8, 2, *OR)); film_x.append(x + 1.25)
    u.append(cube(x + 5, base - hh - dpt, 9, hh, dpt, *BL)); pos_dec.append((x + 10, base - hh - dpt))
    x += 17
x += 2
for (xe, ye), (xd, yd) in zip(pos_enc, reversed(pos_dec)):
    ty = min(ye, yd) - 5
    u.append(f'<path d="M{xe} {ye} C {xe} {ty - 5}, {xd} {ty - 5}, {xd} {yd}" stroke="#8a8f98" stroke-width="0.7" stroke-dasharray="2 2" fill="none"/>')
UW = x
# shared condition [c_t, k] feeds every FiLM layer
u.append(f'<path d="M{min(film_x):.1f} 66 L{max(film_x):.1f} 66" stroke="#6E8DBE" stroke-width="0.9" fill="none"/>')
for fx_ in film_x:
    u.append(f'<path d="M{fx_:.1f} 66 L{fx_:.1f} 61.5" stroke="#6E8DBE" stroke-width="0.8" fill="none"/>'
             f'<path d="M{fx_ - 1.8:.1f} 61.6 L{fx_:.1f} 58.6 L{fx_ + 1.8:.1f} 61.6 Z" fill="#6E8DBE"/>')
ux = 524 + (180 - UW) / 2
raw(f'<svg width="{UW:.0f}" height="70" viewBox="0 0 {UW:.0f} 70" role="img" aria-label="Conditional 1D U-Net with FiLM layers and skip connections" '
    f'style="position: absolute; left: {ux:.0f}px; top: 80px; width: {UW:.0f}px; height: 70px; overflow: visible">' + "".join(u) + '</svg>')
# legend
lock(388, 174)
label(398, 173, 120, "frozen after pretraining", fs=S, align="left")
swatch(388, 187, "#B9CCE8", "#6F8BBA")
label(398, 185, 60, "U-Net block", fs=S, align="left")
swatch(444, 187, "#F2C3A0", "#C98A5E")
label(454, 185, 70, "FiLM from [" + i("c<sub>t</sub>") + ", " + i("k") + "]", fs=S, align="left")
# output
seg(560, 170, 560, 177)
bx(524, 178, 80, 16, "DDIM ×10", BLUEB)
seg(605, 186, 613, 186)
dots = "".join(f'<circle cx="{3 + j * 5:.1f}" cy="{12 - 9 * (j / 11) + 4 * (j / 11) ** 2:.1f}" r="1.5" fill="#4F6FA3"/>' for j in range(12))
raw(f'<svg width="62" height="16" viewBox="0 0 62 16" role="img" aria-label="Predicted trajectory" style="position: absolute; left: 614px; top: 177px; width: 62px; height: 16px; overflow: visible">'
    f'<path d="M3 12 Q 30 4 58 4" stroke="#7F9CC8" stroke-width="0.7" fill="none"/>{dots}</svg>')
label(590, 198, 116, "Predicted action seq. " + Zk("0"))
seg(678, 186, 703, 186, head=False)
seg(703, 186, 703, 239)

# =============== (d) Training ===============
band(8, 240, 540, 156, "#FCF8F2", "#D9BC94", radius=8)
ttl(8, 243, 540, "Training: BC Pretraining + Two-stage DPPO Post-training")
# d1 pretraining
band(14, 262, 92, 128, "#ffffff", "#E6D8C3", radius=4)
label(14, 265, 92, "<b>BC pretraining</b>")
bx(20, 282, 80, 26, "EGO-Planner<br>demos (988)", YELB)
seg(60, 308, 60, 315)
bx(20, 316, 80, 20, i("L") + "<sub>BC</sub> + " + i("λ") + "<sub>geo</sub>" + i("L") + "<sub>geo</sub>", YELB)
seg(60, 336, 60, 343)
bx(20, 344, 80, 26, "Update all<br>parameters", ORB)
seg(106, 330, 117, 330, color="#555B63")
label(102, 318, 22, "init.", fs=S, color="#444")
# d2 two-stage post-training (overview only; two-layer MDP is in Fig. 3)
band(118, 262, 424, 128, "#ffffff", "#E6D8C3", radius=4)
label(118, 265, 424, "<b>Two-stage DPPO post-training</b>")
bx(126, 281, 196, 14, "<b>Stage 1</b> · PPO · 128 updates", YELB, fs=S)
bx(328, 281, 206, 14, "<b>Stage 2</b> · PPO + success retention · 128 updates", ORB, fs=S)
bx(126, 300, 200, 18, "Reward: terminal · progress · risk · time · space", YELB, fs=S)
seg(161, 318, 161, 326, color="#B08A57")
bx(356, 300, 178, 18, "Fixed successful-prefix reference bank", ("#FFFAF3", "#B88A52"), fs=S, dashed=True)
# main row
Y0, HB = 327, 34
row = [(126, 70, "Rollouts<br>(H4, reward " + i("r<sub>t</sub>") + ")", YELB),
       (204, 66, "Critic<br>" + i("V<sub>φ</sub>") + "(" + i("c<sub>t</sub>") + ", " + i("e<sub>t</sub>") + ")", YELB),
       (278, 66, "Advantage<br>" + i("Â<sub>t</sub>") + " (GAE)", YELB),
       (352, 64, "PPO loss<br>(denoising steps)", ORB, S)]
for xx, ww, tx, pal, *fs_ in row:
    bx(xx, Y0, ww, HB, tx, pal, fs=(fs_[0] if fs_ else F))
for (xx, ww, *_), (nx, *_) in zip(row[:-1], row[1:]):
    seg(xx + ww, Y0 + 17, nx - 1, Y0 + 17)
# actor-loss sum node
SX, SY = 432, Y0 + 17
seg(416, SY, SX - 7, SY)
raw(f'<svg width="12" height="12" viewBox="0 0 12 12" role="img" aria-label="sum" style="position: absolute; left: {SX - 6}px; top: {SY - 6}px; width: 12px; height: 12px; overflow: visible">'
    '<circle cx="6" cy="6" r="5.5" fill="#ffffff" stroke="#8E6A3E" stroke-width="0.9"/><path d="M6 2.2 V9.8 M2.2 6 H9.8" stroke="#8E6A3E" stroke-width="0.9"/></svg>')
seg(SX, 318, SX, SY - 7, color="#B08A57")
label(SX - 63, 319, 60, "+ " + i("λL") + "<sub>keep</sub>", fs=S, align="right", color="#8E6A3E")
seg(SX + 6, SY, 455, SY)
label(436, SY + 3, 22, i("L") + "<sub>actor</sub>", fs="7px", color="#8E6A3E")
bx(456, Y0, 78, HB, "Update actor LoRA<br>(backbone frozen)", REDB, fs=S)
# critic has its own optimisation
bx(198, 368, 78, 12, "value loss → update " + i("V<sub>φ</sub>"), ("#FFFFFF", "#C49E6C"), fs="7px")
seg(237, 368, 237, 362, color="#B08A57")
# loop
seg(495, 361, 495, 384, color="#B08A57", head=False)
seg(495, 384, 161, 384, color="#B08A57", head=False)
seg(161, 384, 161, 362, color="#B08A57")
label(296, 373, 190, "next iteration uses the updated LoRA", fs=S, italic=True, color="#8E6A3E")

# =============== (e) Receding horizon ===============
band(556, 240, 154, 156, "#F3F9F9", "#94C6C0", radius=8)
ttl(556, 243, 154, "Receding-horizon<br>Execution")
label(556, 280, 154, "Generate 16 steps,<br>execute steps 3–6")
cell = []
for j in range(16):
    fi, bo = (("#DADDE0", "#9AA1A7") if j < 2 else ("#93CEC6", "#5A9E96") if j < 6 else ("#D3EBE8", "#8CC0B9") if j < 10 else ("#FFFFFF", "#A8B0B5"))
    cell.append(f'<rect x="{j * 8}" y="0" width="8" height="12" fill="{fi}" stroke="{bo}" stroke-width="0.6"/>')
cell.append('<path d="M17 16 L47 16" stroke="#5A9E96" stroke-width="0.9" fill="none"/><path d="M17 14 L17 18 M47 14 L47 18" stroke="#5A9E96" stroke-width="0.9"/>')
cell.append('<path d="M17 27 L79 27" stroke="#8CC0B9" stroke-width="0.9" fill="none"/><path d="M17 25 L17 29 M79 25 L79 29" stroke="#8CC0B9" stroke-width="0.9"/>')
cell.append('<text x="51" y="19" font-size="8" fill="#3F7F78" font-family="Tinos, serif">H4 executed</text>')
cell.append('<text x="83" y="30" font-size="8" fill="#5E8F89" font-family="Tinos, serif">H8 risk window</text>')
raw('<svg width="128" height="32" viewBox="0 0 128 32" role="img" aria-label="Sixteen-step trajectory; the first four steps after two aligned steps are executed; eight steps form the risk window" '
    'style="position: absolute; left: 569px; top: 312px; width: 128px; height: 32px; overflow: visible">' + "".join(cell) + "</svg>")
bx(578, 360, 110, 26, "Update observations<br>and replan", ("#E6F3F1", "#8CC0B9"))

# =============== closed loop back to the environment ===============
seg(600, 240, 600, 231, head=False)
seg(600, 231, 290, 231, head=False)
seg(290, 231, 290, 162)
label(214, 186, 72, "execute H4,<br>observe, replan", align="right", italic=True, color="#4F6A93")
