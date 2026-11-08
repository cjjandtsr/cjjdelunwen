"""论文数据表（唯一版本）：每个数字只出现一次；训练外结果只按任务难度（总体/稀疏/适中/密集）展示。
运行：python3 -I paper_data_workbook.py <oprime/rows.json> <oprime 目录> <g12_summary.csv> <g3 table_main.csv> <out.xlsx>
rows.json、oprime/*.csv 由 o_prime_analysis.py、curves_clearance.py、s3_oprime.py 生成。"""
import json, sys, csv, collections, statistics
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L

rows_p, OP, G12, G3, OUT = sys.argv[1:6]
R = json.load(open(rows_p))
rd = lambda p: list(csv.reader(open(p, encoding='utf-8-sig')))[1:]
NAME = {'P0': 'BC策略', 'P2': '单阶段后训练', 'P6': '本文方法', 'P3': '两阶段后训练（不中断，不加正则）',
        'P4': '两阶段后训练（分叉，不加正则）', 'P14': '单阶段后训练（第二次运行）', 'P15': '本文方法（第二次运行）'}
ORDER = ['P0', 'P2', 'P6', 'P3', 'P4', 'P14', 'P15']
USE = {'P0': '表 3、表 4', 'P2': '表 3、表 4', 'P6': '表 3、表 4', 'P3': '表 4', 'P4': '表 4', 'P14': '表 4', 'P15': '表 4'}
DIFF = ['总体', '稀疏', '适中', '密集']
F = 'Arial'; H = PatternFill('solid', start_color='DCE6F3'); th = Side(style='thin', color='BFBFBF'); B = Border(left=th, right=th, top=th, bottom=th)
BLUE = '0000FF'
wb = Workbook()
def sheet(title, note, cols, widths):
    ws = wb.create_sheet(title)
    ws.append([note]); ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cols))
    ws['A1'].font = Font(name=F, italic=True, color='404040'); ws['A1'].alignment = Alignment(wrap_text=True, vertical='top'); ws.row_dimensions[1].height = 48
    ws.append(cols)
    for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w
    for c in ws[2]: c.font = Font(name=F, bold=True); c.fill = H; c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = B
    ws.freeze_panes = 'A3'; return ws
def style(ws):
    for row in ws.iter_rows(min_row=3):
        for c in row: c.font = Font(name=F, color=c.font.color, bold=c.font.bold); c.border = B; c.alignment = Alignment(vertical='top', wrap_text=True)
def blue(ws, r, cols):
    for col in cols: ws[f'{col}{r}'].font = Font(name=F, color=BLUE)

# 说明（索引，不重复数字）
ws = wb.active; ws.title = '说明'
ws.column_dimensions['A'].width = 16; ws.column_dimensions['B'].width = 30; ws.column_dimensions['C'].width = 58
info = [
 '论文数据表（唯一版本，2026-11-08）。每个数字只在一页出现一次；训练外结果只按任务难度（总体 / 稀疏 / 适中 / 密集）展示，不按世界来源拆分。',
 '训练外评价集：42 个世界，199 个任务（稀疏 59 / 适中 70 / 密集 70），每种方法 995 回合；回合 = 任务 × 5 次重复。区间为按世界聚类的 bootstrap 95% 区间（20000 次）。',
 '蓝字为原始记录计数或脚本输出常数，黑字为公式。']
for i, t in enumerate(info, 1):
    ws.cell(i, 1, t).font = Font(name=F, bold=(i == 1)); ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=3)
    ws.cell(i, 1).alignment = Alignment(wrap_text=True); ws.row_dimensions[i].height = 32
ws.append([]); ws.append(['页', '用在论文哪里', '支撑什么结论'])
for c in ws[ws.max_row]: c.font = Font(name=F, bold=True); c.fill = H; c.border = B
for r in [('1 结局', '表 3（BC、单阶段、本文方法）；表 4（其余）；摘要；4.2 总体性能、安全与效率', '后训练显著提高安全到达率，三类难度都提高；提升来自超时减少，碰撞不增加'),
          ('2 配对比较', '摘要；贡献 3；4.2 总体性能、消融；表 4；补充 S4', '主判据（本文方法 − BC）；第一阶段贡献主体；第二阶段加正则在两次运行中都提高、不加正则不提高；第二次运行的结果'),
          ('3 超时距离', '4.2 失败形态；图 9', '剩余失败主要是已接近目标但未进入到达范围'),
          ('4 路径与行为', '表 5；图 7', '行为克隆正则保持路径直接，不加正则时绕远、回退'),
          ('5 安全余量', '表 3 一列', '如实报告：本文方法在密集类以更小余量通过，碰撞不增加'),
          ('6 训练过程', '4.2 训练过程；图 8', '加正则时第二阶段训练平稳'),
          ('7 直线参考', '4.1 或图 6 参考线', '难度分类有效：密集类直线几乎都碰撞'),
          ('8 图10选例', '图 10', '三类难度各一例 BC 失败、本文方法到达'),
          ('9 方法与设置', '表 1、表 2、3.6', '复现所需设置'),
          ('S2 截断±1.0', '补充 S2', '评价设置的敏感性对照（训练世界）'),
          ('S3 分类界限', '补充 S3', '难度界限取一半或两倍时结论不变'),
          ('S4b 训练与验证世界', '补充 S4b', '开发用世界上规律一致'),
          ('S5 检查点', '补充 S5', '用固定预算终点，不按评价选检查点'),
          ('（待实验）Gazebo', '4.3、图 11、表 6', 'BC、本文方法、EGO-Planner，48 个任务 × 2 次；尚无数据')]:
    ws.append(list(r))
    for c in ws[ws.max_row]: c.font = Font(name=F); c.border = B; c.alignment = Alignment(wrap_text=True, vertical='top')

cat = lambda r, d: d == '总体' or r['cat'] == d
# 1 结局
ws = sheet('1 结局', '训练外评价集上各方法的结局。到达率、碰撞率、超时率由计数公式计算。', ['方法', '难度', '回合', '到达', '碰撞', '超时', '到达率', '到达率区间（%）', '碰撞率', '超时率', '用在'],
           [30, 7, 7, 7, 7, 7, 9, 15, 9, 9, 12])
MAIN = {(r[2], r[1]): r for r in rd(f'{OP}/main.csv') if r[0] == 'O′'}
for p in ORDER:
    for d in DIFF:
        m = MAIN[(p, d)]; i = ws.max_row + 1
        ws.append([NAME[p], d, int(m[3]), int(m[5]), int(m[6]), int(m[7]), f'=D{i}/C{i}', m[9], f'=E{i}/C{i}', f'=F{i}/C{i}', USE[p]])
        blue(ws, i, 'CDEFH')
        for col in 'GIJ': ws[f'{col}{i}'].number_format = '0.0%'
style(ws)
# 2 配对比较
CMP = [('P6', 'P0', '主判据：本文方法相对 BC'), ('P2', 'P0', '第一阶段的贡献'), ('P6', 'P2', '第二阶段（加正则）的提升'),
       ('P4', 'P2', '不加正则的继续训练（分叉）'), ('P3', 'P2', '不加正则的继续训练（不中断）'), ('P6', 'P4', '正则比较'), ('P6', 'P3', '正则比较'),
       ('P15', 'P14', '第二次运行：第二阶段的提升'), ('P15', 'P0', '第二次运行：本文方法相对 BC（预先登记判据）'), ('P14', 'P0', '第二次运行：第一阶段相对 BC（预先登记判据）')]
ws = sheet('2 配对比较', '同一任务同一次重复配对。差值 =（新增 − 流失）/ 回合，单位为比例。新增 = 前者到达而后者未到达。',
           ['比较', '作用', '难度', '回合', '新增', '流失', '差值', '区间（百分点）'], [44, 30, 7, 7, 7, 7, 9, 15])
PR = {(r[2], r[1]): r for r in rd(f'{OP}/pairs.csv') if r[0] == 'O′'}
for a, b, role in CMP:
    for d in DIFF:
        m = PR[(f'{a}-{b}', d)]; i = ws.max_row + 1
        ws.append([f'{NAME[a]} − {NAME[b]}', role, d, int(m[3]), int(m[6]), int(m[7]), f'=(E{i}-F{i})/D{i}', m[5]])
        blue(ws, i, 'DEFH'); ws[f'G{i}'].number_format = '+0.0%;-0.0%;0.0%'
style(ws)
# 3 超时距离
ws = sheet('3 超时距离', '超时回合按执行路径到目标的最近距离分档。', ['方法', '难度', '超时', '<1 m', '1—2 m', '>2 m', '<1 m 占比'], [30, 7, 7, 7, 7, 7, 10])
for p in ORDER:
    for d in DIFF:
        x = [r['near'] for r in R if r['policy'] == p and cat(r, d) and r['out'] == 'time_limit']; i = ws.max_row + 1
        ws.append([NAME[p], d, len(x), sum(v < 1 for v in x), sum(1 <= v < 2 for v in x), sum(v >= 2 for v in x), f'=IF(C{i}=0,0,D{i}/C{i})'])
        blue(ws, i, 'CDEF'); ws[f'G{i}'].number_format = '0.0%'
style(ws)
# 4 路径与行为
ws = sheet('4 路径与行为', '只计到达回合，取中位数。路径效率 = 起终点直线距离 / 执行路径长度。', ['方法', '难度', '到达回合', '路径效率', '最大横向偏离（m）', '回退距离（m）'], [30, 7, 9, 9, 14, 12])
BH = {(r[2], r[1]): r for r in rd(f'{OP}/behavior.csv')}
for p in ORDER:
    for d in DIFF:
        m = BH[(p, d)]; ws.append([NAME[p], d, int(m[3]), float(m[4]), float(m[5]), float(m[7])]); blue(ws, ws.max_row, 'CDEF')
style(ws)
# 5 安全余量
ws = sheet('5 安全余量', '到达回合中执行路径到障碍表面最小距离的中位数（机体半径 0.1 m 未扣除）。只导出了下列四种方法。', ['方法', '难度', '回合', '最小障碍距离中位数（m）'], [30, 7, 7, 18])
for r in rd(f'{OP}/clearance.csv'):
    ws.append([NAME[r[0]], r[1], int(r[2]), float(r[3])]); blue(ws, ws.max_row, 'CD')
style(ws)
# 6 训练过程
RUN = {'P2_P3': '第一阶段 + 不中断续训（同一运行）', 'P6': '本文方法第二阶段', 'P4': '分叉不加正则（第二阶段）', 'P14': '第一阶段（第二次运行）', 'P15': '本文方法第二阶段（第二次运行）'}
ws = sheet('6 训练过程', '训练中每 16 轮的采集到达率（Σ到达 / Σ完成回合）与近似 KL 中位数。', ['运行', '轮次', '采集到达率', '近似 KL'], [34, 12, 12, 12])
for r in rd(f'{OP}/curve_blocks.csv'):
    ws.append([RUN[r[0]], r[1], float(r[2]) / 100, float(r[3])]); i = ws.max_row
    ws[f'C{i}'].number_format = '0.0%'; ws[f'D{i}'].number_format = '0.0E+00'; blue(ws, i, 'CD')
style(ws)
# 7 直线参考（合并为训练外评价集，只按难度）
ws = sheet('7 直线参考', '沿起点到目标的直线飞行，按任务计（直线飞行确定，同一任务各重复结局相同）。', ['难度', '任务数', '直线到达任务数', '直线到达率'], [8, 8, 14, 12])
g = collections.Counter(); n = collections.Counter()
CN = {'Sparse': '稀疏', 'Moderate': '适中', 'Dense': '密集', 'All': '总体'}
for r in rd(G12):
    if r[0] in ('test12', 'extv2'): n[CN[r[1]]] += int(r[2]); g[CN[r[1]]] += int(r[4])
for d in DIFF:
    i = ws.max_row + 1; ws.append([d, n[d], g[d], f'=C{i}/B{i}']); blue(ws, i, 'BC'); ws[f'D{i}'].number_format = '0.0%'
style(ws)
# 8 图10选例
ws = sheet('8 图10选例', '事先规则：BC 超时或碰撞、本文方法到达的同一任务同一次重复中，每类难度按世界名、任务编号、重复序号取第一个。轨迹待 Codex 导出。',
           ['难度', '世界', '任务编号', '重复', 'BC 结局', '本文方法结局'], [7, 54, 68, 6, 9, 11])
for r in [('稀疏', 'front_offset_obstacle__000003', '00401b423993bfb58b91640f191d5ef429b23647998935a209295a0fb47b49ff', 1, '碰撞', '到达'),
          ('适中', 'front_offset_obstacle__000050', 'cb12db0af4915f3ae45ce465e26e0c7817c7859378794bad3e875d966699221e', 1, '超时', '到达'),
          ('密集', 'front_offset_obstacle__000050', '5b955d1a9431873c12e35966524705919c8893b84ac5448fda08f07a9596086b', 2, '超时', '到达')]:
    ws.append(list(r))
style(ws)
# 9 方法与设置
ws = sheet('9 方法与设置', '表 1、表 2 与 3.6 节使用的设置。', ['模块', '参数', '取值', '用在'], [14, 44, 36, 10])
for r in [('示范数据', '成功回合 / 帧数 / 划分', '988 / 60151 / 9:1', '3.6'), ('观测与动作', '历史帧数 / 每帧点数 / 状态维度 / 轨迹维度', '3 / 4096 / 9 / 16×11', '表 2'),
          ('深度相机', '分辨率 / 水平视场角 / 探测距离', '320×240 / 60° / 0.05—10 m', '3.6'), ('策略网络', '几何特征 / 状态特征 / 条件向量', '128 / 64 / 576', '表 2'),
          ('策略网络', 'U-Net 通道 / 卷积核 / 时间步嵌入', '256、512、1024 / 5 / 128', '表 2'), ('扩散模型', '训练扩散步 / DDIM 采样步', '50 / 10', '表 2'),
          ('预训练', '几何辅助损失权重', '0.5', '表 2'), ('执行', '执行段时长 / 规划窗口 / 执行前缀 / 最大决策次数', '0.3 s / 8 段 / 4 段 / 60', '表 2'),
          ('执行', '到达半径 / 碰撞体半径', '0.5 m / 0.1 m', '表 2'), ('LoRA', '秩 / 缩放 / 可训练参数占比', '8 / 8 / 1.43%', '表 2'),
          ('价值网络', '隐藏层 / 激活', '256、256 / SiLU', '表 2'), ('优化', '策略学习率 / 价值学习率', '2e-5 线性降至 1e-5 / 1e-3', '表 2'),
          ('优化', '折扣 / GAE λ / 去噪折扣', '0.99 / 0.95 / 0.8', '表 2'), ('优化', 'PPO 截断宽度 ε0 / εmax', '1e-3 / 0.1', '表 2'),
          ('优化', '每轮决策转移数 / 样本复用遍数 / 每轮参数更新次数', '1024 / 5 / 20', '表 2'), ('训练', '第一阶段 / 第二阶段轮数', '128 / 128', '表 2'),
          ('行为克隆正则', '成功轨迹库任务数 / 样本数 / 每次抽样数', '47 / 549 / 32', '表 2'), ('行为克隆正则', '正则系数 λ / 标定目标梯度比', '0.0106 / 0.1', '表 2'),
          ('回报', '到达 / 碰撞或触地 / 时间惩罚', '+100 / −50 / −0.05 每周期', '表 1'), ('评价', '去噪截断 / 采样', '±2.0 / 确定性', '4.1')]:
    ws.append(list(r))
style(ws)
# S2
ws = sheet('S2 截断±1.0', '训练世界（420 回合），去噪截断取训练时的 ±1.0。', ['方法', '回合', '到达', '碰撞', '超时', '到达率'], [30, 7, 7, 7, 7, 9])
for p, a, c, t in [('P0', 116, 131, 173), ('P2', 160, 150, 110), ('P4', 182, 157, 81), ('P6', 172, 145, 103)]:
    i = ws.max_row + 1; ws.append([NAME[p], 420, a, c, t, f'=C{i}/B{i}']); blue(ws, i, 'BCDE'); ws[f'F{i}'].number_format = '0.0%'
style(ws)
# S3
ws = sheet('S3 分类界限', '适中与密集之间的界限取正文值 t = 0.04623 的 0.5 倍与 2 倍时，两类的到达次数。', ['界限倍数', '难度', '回合', 'BC 到达', '单阶段 到达', '本文方法 到达', '本文方法 − BC'], [9, 7, 7, 8, 10, 11, 12])
for r in rd(f'{OP}/s3_threshold.csv'):
    i = ws.max_row + 1; ws.append([float(r[0]), r[2], int(r[3]), int(r[4]), int(r[5]), int(r[8]), f'=(F{i}-D{i})/C{i}'])
    blue(ws, i, 'CDEF'); ws[f'G{i}'].number_format = '+0.0%;-0.0%'
style(ws)
# S4b
ws = sheet('S4b 训练与验证世界', '训练世界用于后训练，验证世界参与过开发，都不是训练外世界。', ['世界', '方法', '回合', '到达', '碰撞', '超时', '到达率', '区间（%）'], [10, 30, 7, 7, 7, 7, 9, 15])
for r in rd(G3):
    if r[0] not in ('dev420', 'val20'): continue
    i = ws.max_row + 1
    ws.append(['训练世界' if r[0] == 'dev420' else '验证世界', NAME[r[1]], int(r[2]), int(r[4]), int(r[5]), int(r[6]), f'=D{i}/C{i}', r[8]])
    blue(ws, i, 'CDEFH'); ws[f'G{i}'].number_format = '0.0%'
style(ws)
# S5
ws = sheet('S5 检查点', '本文方法同一训练运行的两个检查点在训练世界（420 回合）上的结局。', ['检查点', '回合', '到达', '碰撞', '超时', '到达率'], [10, 7, 7, 7, 7, 9])
for k, a, c, t in [('第 192 轮', 163, 142, 115), ('第 256 轮', 203, 143, 74)]:
    i = ws.max_row + 1; ws.append([k, 420, a, c, t, f'=C{i}/B{i}']); blue(ws, i, 'BCDE'); ws[f'F{i}'].number_format = '0.0%'
style(ws)
wb.save(OUT); print('saved')
