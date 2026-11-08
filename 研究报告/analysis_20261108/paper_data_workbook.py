"""论文数据表（唯一版本，1 m 主终点，研究任务书 D10、D11）。每个数字只出现一次；训练外结果只按难度展示。
运行：python3 -I paper_data_workbook.py <oprime/rows.json> <oprime 目录> <g12_summary.csv> <g3 table_main.csv> <out.xlsx>
成功 = 碰撞前进入目标 1 m（arrival_1m.py 的判据）；碰撞 = 进入 1 m 之前碰撞；超时 = 其余。
路径效率待成功回合执行轨迹补齐后按 1 m 重算（C侧_2026-11-08 导出），本版不列。"""
import json, sys, csv, collections, random
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L

rows_p, OP, G12, G3, OUT = sys.argv[1:6]
R = json.load(open(rows_p))
rd = lambda p: list(csv.reader(open(p, encoding='utf-8-sig')))[1:]
NAME = {'P0': 'BC策略', 'P2': '单阶段后训练', 'P6': '本文方法', 'P3': '两阶段后训练（不中断，不加正则）',
        'P4': '两阶段后训练（分叉，不加正则）', 'P14': '单阶段后训练（第二次运行）', 'P15': '本文方法（第二次运行）'}
DIFF = ['总体', '稀疏', '适中', '密集']
F = 'Arial'; H = PatternFill('solid', start_color='DCE6F3'); th = Side(style='thin', color='BFBFBF'); B = Border(left=th, right=th, top=th, bottom=th)
BLUE = '0000FF'
ok = lambda r: r['out'] == 'reached' or r['near'] < 1.0
def out1m(r): return '成功' if ok(r) else ('碰撞' if r['out'] == 'collision' else '超时')
idx = {(r['policy'], r['task'], r['rep']): r for r in R}
sel = lambda p, d: [r for r in R if r['policy'] == p and (d == '总体' or r['cat'] == d)]
def boot(items):
    by = collections.defaultdict(lambda: [0, 0])
    for w, a in items: by[w][0] += a; by[w][1] += 1
    ws = sorted(by); rng = random.Random(2026102601); v = []
    for _ in range(20000):
        s = n = 0
        for _ in ws: x = by[rng.choice(ws)]; s += x[0]; n += x[1]
        v.append(s / n)
    v.sort(); return f'[{100*v[500]:.1f}, {100*v[19499]:.1f}]'

wb = Workbook()
def sheet(title, note, cols, widths):
    ws = wb.create_sheet(title)
    ws.append([note]); ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cols))
    ws['A1'].font = Font(name=F, italic=True, color='404040'); ws['A1'].alignment = Alignment(wrap_text=True, vertical='top'); ws.row_dimensions[1].height = 45
    ws.append(cols)
    for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w
    for c in ws[2]: c.font = Font(name=F, bold=True); c.fill = H; c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = B
    ws.freeze_panes = 'A3'; return ws
def style(ws):
    for row in ws.iter_rows(min_row=3):
        for c in row: c.font = Font(name=F, color=c.font.color, bold=c.font.bold); c.border = B; c.alignment = Alignment(vertical='top', wrap_text=True)
def blue(ws, r, cols):
    for col in cols: ws[f'{col}{r}'].font = Font(name=F, color=BLUE)
def outcome_rows(ws, pols, use):
    for p in pols:
        for d in DIFF:
            rs = sel(p, d); c = collections.Counter(map(out1m, rs)); i = ws.max_row + 1
            ws.append([NAME[p], d, len(rs), c['成功'], c['碰撞'], c['超时'], f'=D{i}/C{i}', f'=E{i}/C{i}', f'=F{i}/C{i}', use])
            blue(ws, i, 'CDEF')
            for col in 'GHI': ws[f'{col}{i}'].number_format = '0.0%'

# 说明
ws = wb.active; ws.title = '说明'
for i, t in enumerate([
    '论文数据表（唯一版本，2026-11-08，1 m 主终点）',
    '成功：飞行中未碰撞且进入目标 1 m 范围。结局分成功、碰撞、超时三类。训练外评价集 42 个世界、199 个任务（稀疏 59 / 适中 70 / 密集 70），每种方法 995 回合。',
    '蓝字为原始记录计数，黑字为公式。区间只给主比较（按世界聚类 bootstrap，20000 次）。路径效率待成功回合执行轨迹补齐后列入。'], 1):
    ws.cell(i, 1, t).font = Font(name=F, bold=(i == 1)); ws.cell(i, 1).alignment = Alignment(wrap_text=True)
ws.column_dimensions['A'].width = 120
ws.append([]); ws.append(['页 — 用在论文哪里 — 支撑什么结论'])
for t in ['表3 主结果 — 表 3、图 6、图 7、摘要 — 后训练提高成功率，三类难度都提高，碰撞不增加',
          '主比较 — 摘要、贡献、4.2 — 本文方法相对 BC 的提升及区间（图 6 误差线）',
          '表4 消融 — 表 4、4.2 消融 — 第一阶段贡献主体；第二阶段加正则继续提高，不加正则不提高',
          '训练过程 — 图 8 — 加正则时第二阶段平稳',
          '直线参考 — 4.1 — 难度分类有效',
          '图9选例 — 图 9 — 三类难度各一例',
          '方法与设置 — 表 1、表 2、3.6',
          'S2 0.5m — 补充 S2 — 原 0.5 m 标准下的结果',
          'S3 第二次运行 — 补充 S3、局限一句 — 训练随机性',
          '（待实验）Gazebo — 4.3、表 5']:
    ws.append([t]); ws.cell(ws.max_row, 1).font = Font(name=F)

ws = sheet('表3 主结果', '1 m 标准；比例由计数公式计算。', ['方法', '难度', '回合', '成功', '碰撞', '超时', '成功率', '碰撞率', '超时率', '用在'], [30, 7, 7, 7, 7, 7, 9, 9, 9, 16])
outcome_rows(ws, ['P0', 'P2', 'P6'], '表 3、图 6、图 7'); style(ws)

ws = sheet('主比较', '同一任务同一次重复配对的成功率差（1 m 标准）及按世界聚类的 95% 区间。', ['比较', '难度', '回合', '差值（百分点）', '95% 区间'], [30, 7, 7, 14, 16])
for d in DIFF:
    rs = sel('P6', d); it = [(r['world'], ok(r) - ok(idx[('P0', r['task'], r['rep'])])) for r in rs]
    ws.append(['本文方法 − BC策略', d, len(rs), round(100 * sum(x for _, x in it) / len(rs), 1), boot(it)]); blue(ws, ws.max_row, 'CDE')
style(ws)

ws = sheet('表4 消融', '1 m 标准。正文 5 行；第二次运行见 S4。', ['方法', '难度', '回合', '成功', '碰撞', '超时', '成功率', '碰撞率', '超时率', '用在'], [30, 7, 7, 7, 7, 7, 9, 9, 9, 10])
outcome_rows(ws, ['P0', 'P2', 'P3', 'P4', 'P6'], '表 4'); style(ws)

RUN = {'P2_P3': '第一阶段 + 不中断续训（同一运行）', 'P6': '本文方法第二阶段', 'P4': '分叉不加正则（第二阶段）'}
ws = sheet('训练过程', '训练中每 16 轮的采集到达率与近似 KL 中位数（图 8）。', ['运行', '轮次', '采集到达率', '近似 KL'], [34, 12, 12, 12])
for r in rd(f'{OP}/curve_blocks.csv'):
    if r[0] not in RUN: continue
    ws.append([RUN[r[0]], r[1], float(r[2]) / 100, float(r[3])]); i = ws.max_row
    ws[f'C{i}'].number_format = '0.0%'; ws[f'D{i}'].number_format = '0.0E+00'; blue(ws, i, 'CD')
style(ws)

ws = sheet('直线参考', '沿起点到目标直线飞行，按任务计。', ['难度', '任务数', '直线到达任务数', '直线成功率'], [8, 8, 14, 12])
g = collections.Counter(); n = collections.Counter(); CN = {'Sparse': '稀疏', 'Moderate': '适中', 'Dense': '密集', 'All': '总体'}
for r in rd(G12):
    if r[0] in ('test12', 'extv2'): n[CN[r[1]]] += int(r[2]); g[CN[r[1]]] += int(r[4])
for d in DIFF:
    i = ws.max_row + 1; ws.append([d, n[d], g[d], f'=C{i}/B{i}']); blue(ws, i, 'BC'); ws[f'D{i}'].number_format = '0.0%'
style(ws)

ws = sheet('图9选例', '1 m 标准：BC 失败、本文方法成功的同一任务同一次重复，每类取世界名、任务编号、重复序号最小者（fig10_select_1m.py）。', ['难度', '世界', '任务编号', '重复'], [7, 34, 68, 6])
for r in [('稀疏', 'front_offset_obstacle__000003', '00401b423993bfb58b91640f191d5ef429b23647998935a209295a0fb47b49ff', 1),
          ('适中', 'front_offset_obstacle__000052', 'b9e88976c05a3a70cdd204fde78b6deefad46cbf386ead9bd306e753a8255c2c', 2),
          ('密集', 'front_offset_obstacle__000050', '5b955d1a9431873c12e35966524705919c8893b84ac5448fda08f07a9596086b', 3)]:
    ws.append(list(r))
style(ws)

ws = sheet('方法与设置', '表 1、表 2 与 3.6 节。', ['模块', '参数', '取值', '用在'], [14, 44, 36, 10])
for r in [('示范数据', '成功回合 / 帧数 / 划分', '988 / 60151 / 9:1', '3.6'), ('观测与动作', '历史帧数 / 每帧点数 / 状态维度 / 轨迹维度', '3 / 4096 / 9 / 16×11', '表 2'),
          ('深度相机', '分辨率 / 水平视场角 / 探测距离', '320×240 / 60° / 0.05—10 m', '3.6'), ('策略网络', '几何特征 / 状态特征 / 条件向量', '128 / 64 / 576', '表 2'),
          ('策略网络', 'U-Net 通道 / 卷积核 / 时间步嵌入', '256、512、1024 / 5 / 128', '表 2'), ('扩散模型', '训练扩散步 / DDIM 采样步', '50 / 10', '表 2'),
          ('预训练', '几何辅助损失权重', '0.5', '表 2'), ('执行', '执行段时长 / 规划窗口 / 执行前缀 / 最大决策次数', '0.3 s / 8 段 / 4 段 / 60', '表 2'),
          ('训练', '到达奖励半径 / 碰撞体半径', '0.5 m / 0.1 m', '表 2'), ('LoRA', '秩 / 缩放 / 可训练参数占比', '8 / 8 / 1.43%', '表 2'),
          ('价值网络', '隐藏层 / 激活', '256、256 / SiLU', '表 2'), ('优化', '策略学习率 / 价值学习率', '2e-5 线性降至 1e-5 / 1e-3', '表 2'),
          ('优化', '折扣 / GAE λ / 去噪折扣', '0.99 / 0.95 / 0.8', '表 2'), ('优化', 'PPO 截断宽度 ε0 / εmax', '1e-3 / 0.1', '表 2'),
          ('优化', '每轮决策转移数 / 样本复用遍数 / 每轮参数更新次数', '1024 / 5 / 20', '表 2'), ('训练', '第一阶段 / 第二阶段轮数', '128 / 128', '表 2'),
          ('行为克隆正则', '成功轨迹库任务数 / 样本数 / 每次抽样数', '47 / 549 / 32', '表 2'), ('行为克隆正则', '正则系数 λ / 标定目标梯度比', '0.0106 / 0.1', '表 2'),
          ('回报', '到达 / 碰撞或触地 / 时间惩罚', '+100 / −50 / −0.05 每周期', '表 1'), ('评价', '采样 / 去噪截断 / 成功范围', '确定性 / ±2.0 / 目标 1 m', '表 2、4.1')]:
    ws.append(list(r))
style(ws)

ws = sheet('S2 0.5m', '原 0.5 m 到达标准下的结局（补充材料 S2）。', ['方法', '难度', '回合', '到达', '碰撞', '超时', '到达率', '用在'], [30, 7, 7, 7, 7, 7, 9, 10])
MAIN = {(r[2], r[1]): r for r in rd(f'{OP}/main.csv') if r[0] == 'O′'}
for p in ['P0', 'P2', 'P3', 'P4', 'P6']:
    for d in DIFF:
        m = MAIN[(p, d)]; i = ws.max_row + 1
        ws.append([NAME[p], d, int(m[3]), int(m[5]), int(m[6]), int(m[7]), f'=D{i}/C{i}', '补充 S2']); blue(ws, i, 'CDEF'); ws[f'G{i}'].number_format = '0.0%'
style(ws)

ws = sheet('S3 第二次运行', '1 m 标准；第二次运行的单阶段与本文方法（补充材料 S3；正文局限一句）。', ['方法', '难度', '回合', '成功', '碰撞', '超时', '成功率', '碰撞率', '超时率', '用在'], [30, 7, 7, 7, 7, 7, 9, 9, 9, 10])
outcome_rows(ws, ['P14', 'P15'], '补充 S3'); style(ws)
wb.save(OUT); print('saved')
