"""论文用数据清单 + 按世界 / 按任务的到达率（O′，995 回合/策略）。只读。
运行：python3 -I by_world_workbook.py <oprime/rows.json> <g12/g12_tasks.csv> <out.xlsx>
rows.json 由 o_prime_analysis.py 生成；g12_tasks.csv 为直线参考逐任务结果。"""
import json, sys, csv, collections
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter as L

rows_p, g12_p, OUT = sys.argv[1:4]
R = json.load(open(rows_p))
G = {r['task_id']: r['outcome'] for r in csv.DictReader(open(g12_p)) if r['split'] in ('test12', 'extv2')}
POL = [('P0', 'BC策略'), ('P2', '单阶段后训练'), ('P6', '本文方法'), ('P3', '两阶段·不中断·不加正则'), ('P4', '两阶段·分叉·不加正则'),
       ('P14', '单阶段（第二次运行）'), ('P15', '本文方法（第二次运行）')]
F = 'Arial'; H = PatternFill('solid', start_color='DCE6F3'); th = Side(style='thin', color='BFBFBF'); B = Border(left=th, right=th, top=th, bottom=th)
short = lambda w: w.split('__rl_test__')[-1]
fam = lambda w: short(w).rsplit('__', 1)[0]
SET = {'test': '训练外I', 'r02': '训练外II', 'add': '训练外II'}

wb = Workbook()
def hdr(ws, cols, widths):
    ws.append(cols)
    for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w
    for c in ws[1]: c.font = Font(name=F, bold=True); c.fill = H; c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = B
    ws.freeze_panes = 'B2'
def style(ws):
    for row in ws.iter_rows(min_row=2):
        for c in row: c.font = Font(name=F, color=c.font.color, bold=c.font.bold); c.border = B; c.alignment = Alignment(vertical='top', wrap_text=True)

# 1 论文用数据
ws = wb.active; ws.title = '论文用数据'
hdr(ws, ['序号', '数据', '数值', '用在论文哪里'], [5, 30, 70, 26])
for r in [
 ('示范数据', 'EGO-Planner 示范 988 个成功回合、60151 帧', '3.6 实现细节'),
 ('超参数与回报', '见论文表 1、表 2（LoRA 秩 8，可训练参数占 1.43%；正则系数 0.0106）', '表 1、表 2'),
 ('训练外评价集', '42 个世界，199 个任务（稀疏 59 / 适中 70 / 密集 70），每种方法 995 回合', '4.1'),
 ('总体到达率', 'BC 27.2%；单阶段后训练 40.6%；本文方法 45.7%', '摘要、表 3、4.2'),
 ('本文方法 − BC', '+18.5 个百分点 [12.9, 24.1]；稀疏 +27.1、适中 +18.3、密集 +11.4', '摘要、贡献 3、4.2'),
 ('结局构成', '超时 341 → 189 次；碰撞 383 → 351 次（不增加）；本文方法的超时 155 次在目标 1 m 内', '4.2、图 9'),
 ('消融（表 4）', '单阶段 − BC +13.4；第二阶段加正则 +5.1；不加正则继续训练 −0.5（分叉）/ −5.4（不中断）；本文方法 − 不中断不加正则 +10.6', '4.2 消融、表 4'),
 ('第二次运行（表 4）', '单阶段 11.4%；本文方法 26.1%（第二阶段 +14.8）', '表 4、局限一句'),
 ('路径与行为', '路径效率 本文方法 0.996，分叉不加正则 0.873（密集 0.594）；横向偏离 1.18 m 对 2.17 m', '表 5、图 7'),
 ('训练过程', '第二阶段采集到达率：本文方法 36.6%—43.3%；不加正则最低 21.1%；不中断续训 43.7% → 25.6%', '图 8'),
 ('安全余量', '密集类最小障碍距离中位数：本文方法 0.24 m，BC 0.41 m', '表 3'),
 ('直线参考', '直飞到达：稀疏 100%、适中 44.3%、密集 8.6%', '4.1 / 图 6'),
 ('典型轨迹', '三类各 1 个 BC 失败、本文方法到达的例子', '图 10'),
 ('补充材料', '训练/验证世界结果（S4b）、截断 ±1.0（S2）、分类界限（S3）、配对统计（S4）、检查点（S5）', '补充材料'),
 ('Gazebo（待实验）', 'BC、本文方法、EGO-Planner，48 个任务 × 2 次', '4.3、图 11、表 6')]:
    ws.append([ws.max_row] + list(r))
style(ws)

# 2 按任务
ws = wb.create_sheet('按任务')
by = collections.defaultdict(lambda: collections.Counter()); meta = {}
for r in R:
    by[r['task']][r['policy']] += r['out'] == 'reached'
    meta[r['task']] = (r['world'], r['cat'], SET[r['part']])
tasks = sorted(meta, key=lambda t: (short(meta[t][0]), t))
cols = ['世界', '任务', '类别', '评价集', '重复次数'] + [f'{n} 到达次数' for _, n in POL] + ['直线直飞'] + [f'{n} 到达率' for _, n in POL]
hdr(ws, cols, [34, 12, 6, 9, 6] + [9] * 7 + [8] + [9] * 7)
for i, t in enumerate(tasks, 2):
    w, c, s = meta[t]
    ws.append([short(w), t[:10], c, s, 5] + [by[t][p] for p, _ in POL] + ['到达' if G[t] == 'reached' else '碰撞'] +
              [f'={L(6 + k)}{i}/$E{i}' for k in range(7)])
    for k in range(7):
        ws.cell(i, 6 + k).font = Font(name=F, color='0000FF'); ws.cell(i, 14 + k).number_format = '0%'
style(ws)
nT = ws.max_row
# 3 按世界
ww = wb.create_sheet('按世界', 1)
worlds = sorted({meta[t][0] for t in tasks})
rate = {w: sum(by[t]['P6'] for t in tasks if meta[t][0] == w) / (5 * sum(meta[t][0] == w for t in tasks)) for w in worlds}
worlds.sort(key=lambda w: (rate[w], short(w)))
cols = ['世界', '场景类型', '评价集', '任务数', '稀疏', '适中', '密集', '回合'] + [f'{n}' for _, n in POL] + ['直线直飞到达率', '本文方法 − BC']
hdr(ww, cols, [34, 24, 9, 6, 6, 6, 6, 6] + [10] * 7 + [10, 10])
T = "按任务"
for i, w in enumerate(worlds, 2):
    s = sorted({meta[t][2] for t in tasks if meta[t][0] == w})[0]
    rng = lambda col: f"{T}!${col}$2:${col}${nT}"
    ww.append([short(w), fam(w), s,
               f'=COUNTIFS({rng("A")},$A{i})', f'=COUNTIFS({rng("A")},$A{i},{rng("C")},"稀疏")',
               f'=COUNTIFS({rng("A")},$A{i},{rng("C")},"适中")', f'=COUNTIFS({rng("A")},$A{i},{rng("C")},"密集")',
               f'=SUMIFS({rng("E")},{rng("A")},$A{i})'] +
              [f'=SUMIFS({rng(L(6 + k))},{rng("A")},$A{i})/$H{i}' for k in range(7)] +
              [f'=COUNTIFS({rng("A")},$A{i},{rng("M")},"到达")/$D{i}', f'=K{i}-I{i}'])
    for k in range(9, 18): ww.cell(i, k).number_format = '0%'
    ww.cell(i, 17).number_format = '+0%;-0%;0%'
style(ww)
n = ww.max_row
ww.conditional_formatting.add(f'I2:O{n}', ColorScaleRule(start_type='num', start_value=0, start_color='F8696B', mid_type='num', mid_value=0.5, mid_color='FFEB84', end_type='num', end_value=1, end_color='63BE7B'))
r = n + 2
ww.cell(r, 1, '按本文方法到达率从低到高排序。到达率 = 该世界所有任务、所有重复中安全到达的回合比例；颜色：红低绿高。数据：O′ 逐回合记录（o_prime_analysis.py），直线参考 g12_straight_line.py。').font = Font(name=F, italic=True, color='595959')
wb.save(OUT)
print('saved');
for w in worlds[:10]:
    ts = [t for t in tasks if meta[t][0] == w]
    print(short(w), len(ts), collections.Counter(meta[t][1] for t in ts), {p: round(sum(by[t][p] for t in ts) / (5 * len(ts)), 2) for p in ('P0', 'P2', 'P6')}, sum(G[t] == 'reached' for t in ts))
