"""在 figure_01_v3.1.pptx 中生成全部不依赖实验数据的示意图（可编辑PPT对象）。

python 图表/figures_ppt_schematics.py

页序：
  1 图1 方法总体框架（由 figure_01_ppt_edit.py 从用户PPT修改得到）
  2 图2 点云条件扩散策略网络结构
  3 图3 两层决策过程与滚动执行时序
  4 图S4 EGO-Planner 同协议评价的输入与判定对照
依赖数据的图（图4场景渲染、图5—8、S1—S3、图形摘要）不在此文件中，由各自脚本从数据生成。

尺度约定：与图1相同，页面内容宽约296 mm，按190 mm版宽印刷（缩放约0.64）。
因此正文字号10.5—12 pt（印刷约6.7—7.7 pt），最小10 pt（约6.4 pt）。
网络结构数值取自论文3.3节与 data/network_spec.json（代码实测）。
"""
import runpy
from pathlib import Path

from pptx import Presentation

from ppt_kit import C, P, Canvas, new_blank_slide, set_notes

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figure_01_v3.1.pptx"

# 先重新生成图1页，保证本脚本可重复运行
runpy.run_path(str(ROOT / "figure_01_ppt_edit.py"), run_name="__main__")
prs = Presentation(str(OUT))

BOLD = dict(bold=True)


def panel_label(cv, x, y, text, w=120):
    cv.text(x, y, w, 6, [P(text)], size=13, bold=True, align="l")


def trapezoid(cv, x, y, w, h, fill, line, narrow=0.3):
    """左宽右窄的梯形编码器（与图1相同的画法），返回右缘中点。"""
    d = h * narrow
    cv.path([("M", (x, y)), ("L", (x + w, y + d)), ("L", (x + w, y + h - d)), ("L", (x, y + h)), ("L", (x, y))],
            color=line, lw=1.0, tail=False)
    # 填充：用同形状的自由多边形
    el = cv.tree[-1]
    sppr = el.find("{http://schemas.openxmlformats.org/presentationml/2006/main}spPr")
    A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    sppr.find(".//" + A + "path").set("fill", "norm")
    nf = sppr.find(A + "noFill")
    from lxml import etree
    sf = etree.SubElement(sppr, A + "solidFill")
    etree.SubElement(sf, A + "srgbClr").set("val", fill)
    sppr.replace(nf, sf)
    return (x + w, y + h / 2)


def vec_bar(cv, x, y, w, h, fill, line, label=None, label_pos="below", size=10.5):
    cv.rect(x, y, w, h, fill=fill, line=line, lw=0.75)
    if label:
        if label_pos == "below":
            cv.text(x - 6, y + h + 0.6, w + 12, 4.5, label, size=size)
        else:
            cv.text(x - 6, y - 5.1, w + 12, 4.5, label, size=size)


def plus(cv, cx, cy, r=2.4, color=C["grey"]):
    cv.circle(cx, cy, r, fill=C["white"], line=color, lw=0.9)
    cv.line([(cx - r * 0.6, cy), (cx + r * 0.6, cy)], color, 0.9)
    cv.line([(cx, cy - r * 0.6), (cx, cy + r * 0.6)], color, 0.9)


# =====================================================================
# 图2 网络结构
s2 = new_blank_slide(prs)
cv = Canvas(s2)

# (a) 观测编码器
cv.box(20, 22, 98, 54, fill="F2F8FD", line=C["panel_l"], lw=0.75, r=0.04)
panel_label(cv, 23, 23.5, "(a) Observation encoder (per frame)")
# 点云分支
cv.box(23, 33, 18, 12, fill=C["white"], line=C["pn_l"],
       paras=[P(("P", "i"), ("τ", "i sub")), P("4096 × 3")], size=11)
cv.arrow([(41.3, 39), (46.6, 39)])
tr = trapezoid(cv, 47, 32.5, 23, 13, C["pn_f"], C["pn_l"])
cv.text(47, 32.5, 21, 13, [P("Multi-stage"), P("PointNet")], size=11)
cv.arrow([(70.3, 39), (75.6, 39)])
vec_bar(cv, 76, 33.5, 3.2, 11, C["pn_f"], C["pn_l"], [P("128")], "above")
# 状态分支
cv.box(23, 50, 18, 12, fill=C["white"], line=C["mlp_l"],
       paras=[P(("s", "i"), ("τ", "i sub")), P("9")], size=11)
cv.arrow([(41.3, 56), (46.6, 56)])
trapezoid(cv, 47, 49.5, 23, 13, C["mlp_f"], C["mlp_l"])
cv.text(47, 49.5, 21, 13, [P("State MLP"), P("9→64→64")], size=11)
cv.arrow([(70.3, 56), (75.6, 56)])
vec_bar(cv, 76, 51.5, 3.2, 9, C["mlp_f"], C["mlp_l"], [P("64")], "below")
# 拼接为单帧表示 e_τ
cv.line([(79.4, 39), (82.5, 39), (82.5, 56), (79.4, 56)], C["arrow"], 1.2)
cv.arrow([(82.5, 47.5), (86.6, 47.5)])
vec_bar(cv, 87, 38, 3.4, 19, "D9EEF7", C["pn_l"])
cv.text(82, 32.2, 14, 5, P(("e", "i"), ("τ", "i sub"), " 192"), size=10.5)
cv.arrow([(90.7, 47.5), (106.1, 47.5)])
cv.text(91.0, 49.0, 14.5, 9, [P("3 frames"), P("concat")], size=10, color=C["grey"])
vec_bar(cv, 106.5, 29, 5, 37, C["cond_f"], C["cond_l"])
cv.text(102.5, 66.5, 13, 4.5, P(("c", "i"), ("t", "i sub"), " 576"), size=11, bold=True)
cv.text(23, 68.5, 78, 5, P("Shared by the 3 frames; frozen in Stage 2 (no LoRA)."),
        size=10.5, italic=True, color=C["grey"], align="l")

# (c) 多阶段 PointNet
cv.box(20, 80, 98, 52, fill="F2F8FD", line=C["panel_l"], lw=0.75, r=0.04)
panel_label(cv, 23, 81.5, "(c) Multi-stage PointNet")
cv.box(22, 93.5, 15.5, 9, fill=C["white"], line=C["pn_l"], paras=[P("Conv1d"), P("3→128")], size=10)
cv.arrow([(37.8, 98), (45.6, 98)])
cv.box(40, 89, 75, 22, fill=C["white"], line=C["pn_l"], dash="dash", r=0.06)
cv.text(40.5, 89.3, 40, 4.5, P("stage ", ("s", "i"), " (× 4)"), size=10.5, color=C["pn_l"], align="l")
cv.box(46, 94, 17, 8, fill="E6F7FB", line=C["pn_l"], paras=[P("Conv1d"), P("128→128")], size=10)
cv.arrow([(63.3, 98), (82.1, 98)])
cv.box(66, 102, 16, 8, fill="E6F7FB", line=C["pn_l"], paras=[P("max-pool"), P("over ", ("N", "i"))], size=10)
cv.arrow([(64.5, 98), (64.5, 106), (65.7, 106)], lw=1.0)
cv.arrow([(82.3, 106), (84.5, 106), (84.5, 100.6)], lw=1.0)
plus(cv, 84.5, 98, 2.2)
cv.text(80, 92.0, 9, 4, P("256"), size=10)
cv.arrow([(86.8, 98), (92.6, 98)])
cv.box(93, 94, 20, 8, fill="E6F7FB", line=C["pn_l"], paras=[P("Conv1d"), P("256→128")], size=10)
# 4个阶段输出 → 拼接 → Conv1d → max-pool
cv.arrow([(45, 111.3), (45, 117.6)], lw=1.0)
cv.text(47, 111.8, 40, 4.4, P("outputs of the 4 stages"), size=10, color=C["grey"], italic=True, align="l")
cv.box(23, 118, 30, 9, fill=C["white"], line=C["pn_l"], paras=[P("concat 4 stages"), P("4 × 128 = 512")], size=10)
cv.arrow([(53.3, 122.5), (58.6, 122.5)])
cv.box(59, 118, 20, 9, fill="E6F7FB", line=C["pn_l"], paras=[P("Conv1d"), P("512→128")], size=10)
cv.arrow([(79.3, 122.5), (84.6, 122.5)])
cv.box(85, 118, 19, 9, fill="E6F7FB", line=C["pn_l"], paras=[P("max-pool"), P("over ", ("N", "i"))], size=10)
cv.arrow([(104.3, 122.5), (108.6, 122.5)])
vec_bar(cv, 109, 117.5, 3.2, 10, C["pn_f"], C["pn_l"])
cv.text(106.5, 127.6, 9, 4, P("128"), size=10)

# (b) 条件 1D U-Net
cv.box(124, 22, 192, 110, fill="FBFCFE", line=C["panel_l"], lw=0.75, r=0.03)
panel_label(cv, 127, 23.5, "(b) Conditional 1D U-Net denoiser", w=90)
cv.text(205, 23.5, 60, 6, P(("f", "i"), ("θ", "i sub"), "(", ("Z̄", "i"), ("t", "i sub"), ("k", "i sup"), ", ",
                            ("k", "i"), ", ", ("c", "i"), ("t", "i sub"), ")"), size=12, align="l")
# LoRA 外框（去噪网络的全部 Linear 与 Conv1d）
cv.box(127, 29.5, 186, 77.5, fill=None, line=C["lora"], lw=1.0, dash="dash", r=0.03)
cv.text(268, 30.5, 44, 13, [P("LoRA (", ("r", "i"), " = 8) in all"), P("14 Linear + 33 Conv1d"),
                            P("1.02 M trainable (Stage 2)")], size=10, color=C["stage2"], align="r", anchor="t")
# 时间步嵌入与条件
cv.circle(134, 36, 3.2, fill="FF9D59", line=C["lora"], paras=[P(("k", "i"))], size=11)
cv.arrow([(137.4, 36), (141.6, 36)])
cv.box(142, 32, 25, 8, fill=C["white"], line=C["film"], paras=[P("sinusoidal emb."), P("128")], size=10)
cv.arrow([(167.3, 36), (171.6, 36)])
cv.box(172, 32, 25, 8, fill=C["white"], line=C["film"], paras=[P("MLP"), P("128→512→128")], size=10)
cv.arrow([(197.3, 36), (205.6, 36)])
plus(cv, 208, 36, 2.4)
# c_t 从 (a) 进入
cv.arrow([(111.8, 42.5), (208, 42.5), (208, 38.6)])
cv.text(170, 42.9, 30, 4.5, P(("c", "i"), ("t", "i sub"), " (576)"), size=10.5)
cv.arrow([(210.5, 36), (215.6, 36)])
cv.box(216, 31.5, 50, 9, fill=C["film_f"], line=C["film"],
       paras=[P("FiLM generator (704-D input)"), P("Linear → (", ("γ", "i"), ", ", ("β", "i"), ") per block")], size=10)
# FiLM 总线
BUS = 49.0
cv.line([(240, 40.2), (240, BUS)], C["film"], 1.2)

# U-Net 各块：底边对齐；高度 ∝ 序列长度，宽度 ∝ 通道数（对数）
BASE = 92.0
H = {16: 34.0, 8: 17.0, 4: 8.5}
Wc = {11: 1.6, 256: 3.4, 512: 4.4, 1024: 5.6}
x = 129.5
blocks = []  # (x, w, h, kind)


def bar(ch, L, kind, fill, line):
    global x
    w, h = Wc[ch], H[L]
    cv.rect(x, BASE - h, w, h, fill=fill, line=line, lw=0.75)
    blocks.append((x, w, h, kind))
    x += w


def gap(d):
    global x
    x += d


bar(11, 16, "in", C["white"], C["grey"]); gap(6.5)
levels = [("D1", 256, 16, "256@16"), ("D2", 512, 8, "512@8"), ("D3", 1024, 4, "1024@4"), ("M", 1024, 4, "1024@4"),
          ("U1", 512, 4, "512@4"), ("U2", 256, 8, "256@8")]
lvl_pos = {}
for i, (nm, ch, L, lab) in enumerate(levels):
    x0 = x
    bar(ch, L, nm, C["unet_f"], C["unet_l"]); gap(1.6)
    bar(ch, L, nm, C["unet_f"], C["unet_l"])
    lvl_pos[nm] = (x0, x)
    cv.text(x0 - 5, BASE + 0.8, x - x0 + 10, 4.2, P("mid " + lab if nm == "M" else lab), size=10)
    gap(10.5)
x_final = x
bar(256, 16, "final", "D9E6F8", C["unet_l"]); gap(4.5)
cv.text(x_final - 9, BASE + 0.8, 16, 4.2, P("final conv"), size=10)
bar(11, 16, "out", C["white"], C["grey"])
x_out = blocks[-1][0]
# 输入输出标签
cv.text(124.6, BASE - H[16] - 9.5, 12, 9, [P(("Z̄", "i"), ("t", "i sub"), ("k", "i sup")), P("16 × 11")], size=10.5)
cv.text(x_out - 9, BASE - H[16] - 9.5, 20, 9, [P(("Ẑ", "i"), ("t", "i sub"), ("0", "i sup"), " (", ("x", "i"), ("0", "sub"), "-pred.)"), P("16 × 11")], size=10.5)
# 级间箭头与上下采样
YA = BASE - 4.0
seq = [b for b in blocks]
for (xa, wa, ha, ka), (xb, wb, hb, kb) in zip(seq[:-1], seq[1:]):
    if xb - (xa + wa) > 3:
        cv.arrow([(xa + wa + 0.3, YA), (xb - 0.4, YA)], color=C["grey"], lw=0.9, size="sm")
for nm, sym in (("D1", "↓2"), ("D2", "↓2"), ("U1", "↑2"), ("U2", "↑2")):
    a, b = lvl_pos[nm]
    cv.text(b + 1.2, YA - 6.0, 8, 4, P(sym), size=10, color=C["grey"])
# 跳连（只有 1024@4 和 512@8 被使用）
for src, dst in (("D3", "U1"), ("D2", "U2")):
    xs = lvl_pos[src][1] - Wc[1024 if src == "D3" else 512] / 2
    xd = lvl_pos[dst][0] + Wc[512 if dst == "U1" else 256] / 2
    yy = BASE + 5.4
    cv.arc((xs, yy), (xd, yy), lift=-(5.0 if src == "D2" else 2.6), color=C["lgrey"], lw=1.0)
cv.text(lvl_pos["D3"][1], BASE + 8.6, lvl_pos["U1"][0] - lvl_pos["D3"][1], 4, P("skip (concat)"), size=10,
        color=C["grey"])
# FiLM 箭头：12 个残差块
res = [b for b in blocks if b[3] in ("D1", "D2", "D3", "M", "U1", "U2")]
cv.line([(res[0][0] + res[0][1] / 2, BUS), (res[-1][0] + res[-1][1] / 2, BUS)], C["film"], 1.2)
for bx, bw, bh, _ in res:
    cv.arrow([(bx + bw / 2, BUS), (bx + bw / 2, BASE - bh - 0.5)], color=C["film"], lw=0.9, size="sm")
cv.text(242, BUS - 4.6, 60, 4.3, P("FiLM in all 12 residual blocks"), size=10, color=C["film"], align="l")

# 残差块细节
cv.box(127, 110, 186, 20, fill=C["white"], line=C["panel_l"], lw=0.6, r=0.08)
cv.text(129, 111, 50, 4.5, P("Residual block"), size=10.5, bold=True, align="l")
ry = 120.5
cv.text(129, ry - 2.5, 8, 5, P(("h", "i")), size=11)
cv.arrow([(136, ry), (140.6, ry)])
cv.box(141, ry - 4.5, 34, 9, fill=C["unet_f"], line=C["unet_l"], paras=[P("Conv1d (", ("k", "i"), " = 5)"), P("GroupNorm, Mish")],
       size=10)
cv.arrow([(175.3, ry), (179.6, ry)])
cv.box(180, ry - 4, 30, 8, fill=C["film_f"], line=C["film"],
       paras=[P(("γ", "i"), " ⊙ ", ("h", "i"), " + ", ("β", "i"))], size=10.5)
cv.text(186, 111, 30, 4.2, P("from FiLM"), size=10, color=C["film"])
cv.arrow([(195, 115.4), (195, 116.3)], color=C["film"], lw=0.9, size="sm")
cv.arrow([(210.3, ry), (214.6, ry)])
cv.box(215, ry - 4.5, 34, 9, fill=C["unet_f"], line=C["unet_l"], paras=[P("Conv1d (", ("k", "i"), " = 5)"), P("GroupNorm, Mish")],
       size=10)
cv.arrow([(249.3, ry), (255.4, ry)])
plus(cv, 258, ry, 2.4)
cv.arrow([(260.5, ry), (265.6, ry)])
cv.text(266, ry - 2.5, 9, 5, P("out"), size=10.5, align="l")
cv.arrow([(137.5, ry), (137.5, 127.5), (258, 127.5), (258, ry + 2.6)], color=C["grey"], lw=0.9, size="sm")
cv.text(276.5, 116.0, 36, 9, [P("residual: 1 × 1 conv"), P("if channels change")], size=10, color=C["grey"], align="l")
set_notes(s2, "图2 点云条件扩散策略网络结构（矢量示意，不依赖实验数据）。\n"
          "图注草案：(a)每帧点云经多阶段PointNet得到128维几何特征，9维状态经MLP得到64维特征，拼接为192维单帧表示，三帧拼接为576维条件c_t；"
          "编码器在后训练中冻结且不加LoRA。(b)条件一维U-Net：扩散步k经正弦编码与MLP得到128维嵌入，与c_t拼接为704维，经各残差块的线性层生成FiLM参数(γ,β)，"
          "调制全部12个残差块；块高表示序列长度（16/8/4），块宽表示通道数；只使用1024@4与512@8两个跳连（256@16的跳连在实现中未使用）；"
          "输出为x0预测的16×11轨迹。橙色虚线框表示后训练阶段加入LoRA（秩8）的范围：14个线性层与33个一维卷积层，可训练参数1.02 M。(c)多阶段PointNet的单阶段结构。\n"
          "数值来源：论文3.3节；图表/data/network_spec.json（代码实测）。")

# =====================================================================
# 图3 两层决策与滚动执行
s3 = new_blank_slide(prs)
cv = Canvas(s3)
cv.box(20, 20, 296, 78, fill=C["env_f"], line=C["env_l"], lw=0.75, r=0.03)
panel_label(cv, 23, 21.5, "(a) Two-layer decision process", w=90)
cv.text(110, 21.5, 200, 6, P("environment MDP: one step = one decision ", ("t", "i"), " (generate, execute H4, receive ",
                             ("r", "i"), ("t", "i sub"), ")"), size=11, color=C["grey"], align="r")


def decision(x0, t_lab, nxt=False):
    cv.box(x0, 29, 134, 48, fill=C["white"], line=C["env_l"], lw=0.75, r=0.05)
    cv.text(x0 + 2, 29.8, 40, 5, P("Decision ", ("t", "i"), t_lab), size=11.5, bold=True, align="l")
    tsub = "t" + t_lab
    cv.box(x0 + 3, 50, 13, 10, fill="EAF9FC", line="009AAD", paras=[P(("c", "i"), (tsub, "i sub"))], size=12)
    # 去噪 MDP
    cv.box(x0 + 20, 36, 82, 28, fill="F6FAFF", line="425AFF", lw=0.75, dash="dash", r=0.12)
    cv.text(x0 + 20, 36.6, 82, 9, [P("denoising MDP, ", ("K", "i"), " = 10 DDIM steps"),
                                   P("each step: Gaussian, tractable log-probability")], size=10.5, color="2F44C8")
    cx = [x0 + 29, x0 + 46, x0 + 61, x0 + 76, x0 + 93]
    labs = [[("Z", "i"), (tsub, "i sub"), ("K", "i sup")], [("Z", "i"), (tsub, "i sub"), ("K−1", "i sup")], None,
            [("Z", "i"), (tsub, "i sub"), ("1", "i sup")], [("Z", "i"), (tsub, "i sub"), ("0", "i sup")]]
    cy = 55.0
    for i, (xx, lab) in enumerate(zip(cx, labs)):
        if lab is None:
            cv.text(xx - 4, cy - 3, 8, 6, P("⋯"), size=14)
            continue
        fill = "FFD4AF" if i == 4 else ("EDF7FF" if i == 0 else "DCEBFC")
        cv.circle(xx, cy, 5.6, fill=fill, line="C67E22", lw=0.75, paras=[P(*lab)], size=10, wrap="none")
    mids = []
    for a, b in zip(cx[:-1], cx[1:]):
        cv.arrow([(a + 5.6, cy), (b - 5.8, cy)], color=C["arrow"], lw=1.2, size="sm")
        mids.append((a + b) / 2)
    # c_t 条件作用于每一步
    cv.arrow([(x0 + 16.3, 55), (x0 + 19.6, 55)], color="009AAD", lw=1.2, size="sm")
    # 执行
    cv.box(x0 + 106, 48.5, 26, 13, fill=C["org_f"], line=C["org_l"],
           paras=[P("Execute H4"), P("(4 × 0.3 s)")], size=11)
    cv.arrow([(cx[-1] + 5.6, cy), (x0 + 105.6, cy)], color=C["arrow"], lw=1.2, size="sm")
    return mids


m1 = decision(24, "")
m2 = decision(167, "+1")
cv.arrow([(156.3, 55), (169.6, 55)], color=C["arrow"], lw=1.6)
cv.text(156.5, 48.5, 13, 5, P(("r", "i"), ("t", "i sub")), size=11)
cv.text(156.5, 56.5, 13, 9, [P("new"), P("obs.")], size=10, color=C["grey"])
cv.text(302, 51, 12, 8, P("⋯"), size=16)
# 策略梯度：来自每个去噪转移
cv.box(24, 82, 277, 12, fill=C["grn_f"], line=C["grn_l"], lw=0.75, r=0.15,
       paras=[P("clipped PPO on every denoising transition (", ("t", "i"), ", ", ("j", "i"), "): probability ratio from per-step log-probabilities, advantage ",
                ("Ã", "i"), ("t,j", "i sub"), " = ", ("γ", "i"), ("d", "i sub"), ("K−j−1", "i sup"), " Norm(", ("Â", "i"),
                ("t", "i sub"), ")"), P("updates LoRA only; details in Algorithm 1")], size=11)
for mx in m1 + m2:
    cv.arrow([(mx, 57.2), (mx, 81.6)], color="5B8A2E", lw=0.9, dash="dash", size="sm")

# (b) 滚动时域
cv.box(20, 101, 296, 67, fill="FBFCFE", line=C["panel_l"], lw=0.75, r=0.03)
panel_label(cv, 23, 102.5, "(b) Receding-horizon execution", w=90)
CW, CH = 9.5, 7.0
X0 = 62.0
YT, YN = 117.0, 142.0
COL = lambda i: (C["aligned"] if i < 2 else C["executed"] if i < 6 else C["planned"] if i < 10 else C["white"])


def row(x0, y, lab):
    for i in range(16):
        cv.rect(x0 + i * CW, y, CW, CH, fill=COL(i), line="8E959E", lw=0.6)
    cv.text(23, y, 36, CH, lab, size=11.5, bold=True, align="l")


row(X0, YT, P("Decision ", ("t", "i")))
row(X0 + 4 * CW, YN, P("Decision ", ("t", "i"), "+1"))
for i in (0, 2, 6, 10, 15):
    cv.text(X0 + i * CW, YT + 1.0, CW, 5, P(str(i)), size=10, color="333333")
# 括线与标注
cv.bracket(X0, X0 + 16 * CW, YT - 1.2, down=True)
cv.text(X0, YT - 6.6, 16 * CW, 5, P("H16: full prediction (16 × 11)"), size=10.5)
cv.bracket(X0 + 2 * CW, X0 + 10 * CW, YT + CH + 1.2, down=False)
cv.text(X0 + 2 * CW, YT + CH + 1.6, 8 * CW, 4.6, P("H8: planning window, scored for risk ", ("ρ", "i"), ("t", "i sub")),
        size=10.5)
cv.bracket(X0 + 2 * CW, X0 + 6 * CW, YT + CH + 7.4, down=False, color=C["teal"])
cv.text(X0 + 2 * CW - 6, YT + CH + 7.8, 4 * CW + 12, 4.6, P("H4: executed, progress reward"), size=10.5,
        color=C["teal"])
# 未执行段被替换
cv.line([(X0 + 6 * CW, YN - 2.0), (X0 + 6 * CW, YN + CH + 6.0)], C["teal"], 0.9, dash="dash")
cv.text(X0 + 6 * CW + 1.0, YN + CH + 1.0, 60, 4.5, P("replan at 1.2 s from new observations"), size=10.5,
        color=C["teal"], align="l")
cv.text(X0 + 16 * CW + 3, YT + CH + 1.0, 70, 9.5, [P("indices 6–9 are planned but not"), P("executed; they are discarded")],
        size=10.5, color=C["grey"], align="l", anchor="t")
# 图例
lx, ly = 228.0, 105.0
for k, (f, lab) in enumerate(((C["aligned"], "aligned, not executed"), (C["executed"], "executed (H4)"),
                              (C["planned"], "planned only"), (C["white"], "outside H8"))):
    xx = lx + (k % 2) * 44
    yy = ly + (k // 2) * 5.4
    cv.rect(xx, yy + 0.6, 3.6, 3.6, fill=f, line="8E959E", lw=0.6)
    cv.text(xx + 5, yy, 38, 4.8, P(lab), size=10, align="l")
# 时间轴
YX = 162.0
t0 = X0 + 2 * CW
cv.arrow([(t0, YX), (t0 + 8 * CW + 6, YX)], color=C["grey"], lw=0.9, size="sm")
for k in range(9):
    xx = t0 + k * CW
    cv.line([(xx, YX - 1.2), (xx, YX + 0.4)], C["grey"], 0.75)
    cv.text(xx - 4, YX + 0.6, 8, 4.2, P(f"{0.3 * k:.1f}".rstrip("0").rstrip(".") if k else "0"), size=10)
    if k % 4 == 0:
        cv.shape("diamond", xx - 1.6, YX - 4.6, 3.2, 3.2, fill=C["teal"], line=C["teal"], lw=0.5)
    else:
        cv.circle(xx, YX - 3.0, 1.1, fill=C["grey"], line=C["grey"], lw=0.5)
cv.text(t0 + 8 * CW + 7, YX - 2.2, 12, 4.4, P("time (s)"), size=10, align="l")
cv.text(23, YX - 6.2, 36, 9, [P("● observe every 0.3 s"), P("◆ replan every 1.2 s")], size=10, align="l",
        color=C["grey"])
set_notes(s3, "图3 两层决策过程与滚动执行时序（矢量示意，不依赖实验数据）。\n"
          "图注草案：(a)外层环境MDP的一步对应一次决策t：以条件c_t经K=10步DDIM去噪生成轨迹Z_t^0，执行H4前缀后获得奖励r_t与新观测；"
          "内层去噪MDP的每一步是一次高斯转移，其对数概率可解析计算，PPO在全部去噪转移(t,j)上计算新旧策略概率比，"
          "优势按去噪折扣加权，只更新LoRA，细节见算法1。(b)H16为完整预测，索引2—9构成H8规划窗口（参与风险评价），"
          "索引2—5构成H4执行前缀（4×0.3 s，计算进展奖励）；每0.3 s更新一次观测，每1.2 s重新规划，上一周期未执行的规划段被丢弃。\n"
          "来源：论文3.1节、3.4节、3.5节与算法1。")

# =====================================================================
# 图S4 EGO 对照
s4 = new_blank_slide(prs)
cv = Canvas(s4)
X, Y = 58.0, 26.0
cw = [52.0, 78.0, 92.0]
hdr = ["Item", "Learned policies (BC, post-trained)", "EGO-Planner (controlled adaptation)"]
SAME, ADAPT, INH = ("E7F5F0", "85B5B3"), ("FFF1D8", "F7AB56"), ("EEF0F2", "AEB4BC")
rows = [
    ("Tasks and initial states", "84 original + 24 new tasks; frozen initial observations", "Identical", SAME),
    ("Perception input", "Synthetic depth camera; 4096 points per frame", "Identical 4096-point observation", SAME),
    ("Goal", "Read from the task list", "Read from the task list (planner default replaced)", ADAPT),
    ("Global map", "None; local observations only", "No global map; map bounds enlarged to the task space, resolution unchanged", ADAPT),
    ("Clock", "Simulation time, 0.3 s segments", "Planner timers on simulation time, lock-step with the environment", ADAPT),
    ("Replanning", "Every 1.2 s, after executing H4", "Original timer and distance triggers", INH),
    ("Planner parameters", "—", "Unchanged from demonstration collection", SAME),
    ("Termination and time limit", "Collision, ground contact, arrival; 72 s", "Identical evaluation code", SAME),
]
RH = 11.0
xx = X
for w, h in zip(cw, hdr):
    cv.rect(xx, Y, w, 9, fill=C["frozen"], line="9AA3AE", lw=0.6, paras=[P(h)], size=11, bold=True)
    xx += w
y = Y + 9
for item, mine, ego, (f, l) in rows:
    cv.rect(X, y, cw[0], RH, fill=C["white"], line="9AA3AE", lw=0.6, paras=[P(item)], size=11, bold=True)
    cv.rect(X + cw[0], y, cw[1], RH, fill=C["white"], line="9AA3AE", lw=0.6, paras=[P(mine)], size=10.5)
    cv.rect(X + cw[0] + cw[1], y, cw[2], RH, fill=f, line="9AA3AE", lw=0.6, paras=[P(ego)], size=10.5)
    y += RH
ly = y + 3
for k, ((f, l), lab) in enumerate(((SAME, "identical condition"), (ADAPT, "controlled adaptation"),
                                    (INH, "inherent difference, not aligned"))):
    lx = X + k * 74
    cv.rect(lx, ly + 0.5, 4.5, 4.0, fill=f, line=l, lw=0.6)
    cv.text(lx + 6, ly, 66, 5, P(lab), size=10.5, align="l")
set_notes(s4, "图S4 EGO-Planner同协议评价的输入与判定对照（示意表，不依赖评价结果）。\n"
          "依据：EGO同协议评价执行指引v2（方案B受控适配）及阶段二A确认：目标按任务读取、地图边界覆盖任务空间且分辨率不变、"
          "内部定时器改用仿真时钟并与环境锁步、每帧接收与学习策略相同的4096点观测；规划参数沿用示范采集配置；重规划机制保留原有定时器与距离触发。\n"
          "注意：EGO一次step内参考点的取法（step开始时一次取出或逐0.3 s取最新轨迹）待阶段二B报告确认后，如需要再补入重规划一行。")

prs.save(str(OUT))
print("saved", OUT, "slides:", len(prs.slides))
