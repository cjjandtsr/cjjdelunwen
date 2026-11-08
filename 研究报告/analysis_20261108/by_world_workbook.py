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

# 2 按任务
ws = wb.active; ws.title = '按任务'
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
ws.column_dimensions['D'].hidden = True  # 评价集来源不展示，只按难度
nT = ws.max_row
# 3 按世界
ww = wb.create_sheet('按世界', 0)
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
ww.column_dimensions['C'].hidden = True
n = ww.max_row
ww.conditional_formatting.add(f'I2:O{n}', ColorScaleRule(start_type='num', start_value=0, start_color='F8696B', mid_type='num', mid_value=0.5, mid_color='FFEB84', end_type='num', end_value=1, end_color='63BE7B'))
r = n + 2
ww.cell(r, 1, '按本文方法到达率从低到高排序。到达率 = 该世界所有任务、所有重复中安全到达的回合比例；颜色：红低绿高。数据：O′ 逐回合记录（o_prime_analysis.py），直线参考 g12_straight_line.py。').font = Font(name=F, italic=True, color='595959')
wb.save(OUT)
print('saved');
for w in worlds[:10]:
    ts = [t for t in tasks if meta[t][0] == w]
    print(short(w), len(ts), collections.Counter(meta[t][1] for t in ts), {p: round(sum(by[t][p] for t in ts) / (5 * len(ts)), 2) for p in ('P0', 'P2', 'P6')}, sum(G[t] == 'reached' for t in ts))
