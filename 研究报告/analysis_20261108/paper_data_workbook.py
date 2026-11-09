"""论文数据表（唯一版本）：正文与补充材料中每一张图表、每一个实验数字的数据，按论文顺序，一页对应一个图表。
运行：python3 -I paper_data_workbook.py <rows.json> <analysis_20261108 目录> <g3 table_main.csv（未用，保留位置）> <论文大稿_v3.md> <out.xlsx>
rows.json 由 o_prime_analysis.py 生成（O′ 7 个策略各 995 回合）。成功 = 碰撞前进入目标 1.5 m（用户 11-09；任务书 v3.7）。
蓝字为原始计数或原始值，黑字为公式。区间：按世界聚类 bootstrap，20000 次，seed 2026102601（工程阈值，非显著性检验）。"""
import json, sys, csv, collections, random, re, statistics as stt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L

rows_p, A, _G3, DRAFT, OUT = sys.argv[1:6]
R = json.load(open(rows_p))
rd = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))
NAME = {'P0': 'UAV-iDP3', 'P2': 'Reg-DPPO w/o Stage II', 'P3': 'Single-stage DPPO', 'P4': 'Reg-DPPO w/o BC reg.', 'P6': '本文方法',
        'P14': 'Reg-DPPO w/o Stage II（第二次运行）', 'P15': '本文方法（第二次运行）'}
DIFF = ['总体', '稀疏', '适中', '密集']
F = 'Arial'; H = PatternFill('solid', start_color='DCE6F3'); th = Side(style='thin', color='BFBFBF'); B = Border(left=th, right=th, top=th, bottom=th); BLUE = '0000FF'
ok = lambda r: r['out'] == 'reached' or r['near'] < 1.5
out1m = lambda r: '成功' if ok(r) else ('碰撞' if r['out'] == 'collision' else '超时')
sel = lambda p, d: [r for r in R if r['policy'] == p and (d == '总体' or r['cat'] == d)]
idx = {(r['policy'], r['task'], r['rep']): r for r in R}
def boot(items):
    by = collections.defaultdict(lambda: [0, 0])
    for w, a in items: by[w][0] += a; by[w][1] += 1
    ws = sorted(by); rng = random.Random(2026102601); v = []
    for _ in range(20000):
        s = n = 0
        for _ in ws: x = by[rng.choice(ws)]; s += x[0]; n += x[1]
        v.append(s / n)
    v.sort(); return f'[{100*v[500]:.1f}, {100*v[19499]:.1f}]'

wb = Workbook(); INDEX = []
def sheet(title, where, claim, cols, widths):
    INDEX.append((title, where, claim))
    ws = wb.create_sheet(title)
    ws.append([f'{where}｜{claim}']); ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cols))
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
def md_table(title):
    s = open(DRAFT).read(); i = s.index(f'**{title}'); lines = s[i:].split('\n')[2:]
    out = []
    for l in lines:
        if not l.startswith('|'): break
        if l.startswith('| ---'): continue
        out.append([c.strip() for c in l.strip('|').split('|')])
    return out

# ---- 表1、表2：取自正文
for t, where, claim in [('表1　回报组成', '表1（3.4节）', '回报各项的取值与设计依据'), ('表2　主要超参数', '表2（3.6节）', '实现与训练设置')]:
    T = md_table(t); ws = sheet(t.split('　')[0] + ' ' + t.split('　')[1][:6], where, claim, T[0], [22, 44, 60][:len(T[0])])
    for r in T[1:]: ws.append(r)
    style(ws)

# ---- 表3 评价任务
ws = sheet('表3 评价任务', '表3（4.1节）', '三类难度的任务规模；直线飞行成功比例随难度下降（去除 oprime/exclusions.json 中 9 个任务后）',
           ['难度', '任务数', '世界数', '直线距离中位数 m', '最小 m', '最大 m', '直线飞行成功任务数', '直线飞行成功比例', 'Gazebo 任务数'], [7, 8, 8, 12, 8, 8, 12, 12, 10])
for r in rd(f'{A}/oprime_task/table3.csv'):
    i = ws.max_row + 1
    ws.append([r['难度'], int(r['任务数']), int(r['世界数']), float(r['直线距离中位数']), float(r['最小']), float(r['最大']), int(r['直线飞行成功任务数']), f'=G{i}/B{i}', int(r['Gazebo任务数'])])
    blue(ws, i, 'BCDEFGI'); ws[f'H{i}'].number_format = '0.0%'
style(ws)

# ---- 表4 主要结果
ws = sheet('表4 主要结果', '表4（4.2节总体性能、消融分析）；摘要、贡献3、结论', '按任务统计（5 次中至少 3 次成功）：后训练提高成功率且三类难度都提高；第一阶段贡献主体，加正则的第二阶段继续提高；碰撞率不增加，超时显著减少', ['方法', '任务', '成功', '稀疏任务', '稀疏成功', '适中任务', '适中成功', '密集任务', '密集成功', '碰撞', '超时', '成功率 总体', '稀疏', '适中', '密集', '碰撞率', '超时率', '路径效率（成功任务的成功飞行中位数）'], [24] + [7] * 10 + [9] * 6 + [12])
for r in rd(f'{A}/oprime_task/main.csv'):
    i = ws.max_row + 1
    ws.append([r['方法']] + [int(r[k]) for k in ['任务', '成功', '稀疏任务', '稀疏成功', '适中任务', '适中成功', '密集任务', '密集成功', '碰撞', '超时']] + [f'=C{i}/B{i}', f'=E{i}/D{i}', f'=G{i}/F{i}', f'=I{i}/H{i}', f'=J{i}/B{i}', f'=K{i}/B{i}'] + [float(r['路径效率'])])
    blue(ws, i, 'BCDEFGHIJKR')
    for col in 'LMNOPQ': ws[f'{col}{i}'].number_format = '0.0%'
style(ws)

# ---- 图5 训练过程
RUN = {'P2_P3': None, 'P6': '本文方法（第二阶段）', 'P4': 'Reg-DPPO w/o BC reg.'}
ws = sheet('图5 训练过程', '图5（4.2节两阶段训练的作用）', '加正则时第二阶段采集成功率与 KL 平稳；不加正则时成功率下降、KL 突增',
           ['曲线', '轮次', '采集成功率（训练到达奖励口径）', '近似 KL 中位数'], [30, 12, 16, 14])
for r in rd(f'{A}/oprime/curve_blocks.csv'):
    k = r['策略']
    if k not in RUN: continue
    u = int(r['轮'].split('-')[0][1:])
    name = RUN[k] or ('第一阶段' if u <= 128 else 'Single-stage DPPO')
    i = ws.max_row + 1; ws.append([name, r['轮'], float(r['采集到达率%']) / 100, float(r['KL中位数'])]); blue(ws, i, 'CD')
    ws[f'C{i}'].number_format = '0.0%'; ws[f'D{i}'].number_format = '0.00E+00'
style(ws)

# ---- 图6 典型轨迹
ws = sheet('图6 典型轨迹', '图6（4.2节避障行为）', '三类难度各一例：UAV-iDP3 失败、本文方法成功（1.5 m；同一任务同一次重复，按世界名、任务编号、重复序号取最小者；fig10_select_1m.py）',
           ['难度', '世界', '任务编号', '重复', 'UAV-iDP3 结局', '本文方法结局'], [7, 34, 30, 6, 12, 12])
for d, w, t, rp in [('稀疏', 'front_offset_obstacle__000003', '00401b423993', 1), ('适中', 'front_offset_obstacle__000053', '056f74e9a874', 1), ('密集', 'front_offset_obstacle__000050', '5b955d1a9431', 3)]:
    a = [r for r in R if r['task'].startswith(t) and r['rep'] == rp]
    ws.append([d, w, t, rp] + [out1m(next(r for r in a if r['policy'] == p)) for p in ('P0', 'P6')])
style(ws)

# ---- 表5 Gazebo
ws = sheet('表5 Gazebo', '表5（4.3节）；摘要、贡献3、结论', '按任务统计：成功率提高、超时大幅减少、碰撞率相同；EGO-Planner 总体更高，稀疏与适中类与本文方法相当',
           ['难度', '方法', '任务', '成功', '碰撞', '超时', '成功率', '碰撞率', '超时率'], [7, 14, 7, 7, 7, 7, 9, 9, 9])
for r in rd(f'{A}/gazebo/table5_task.csv'):
    i = ws.max_row + 1; ws.append([r['难度'], r['方法'], int(r['任务']), int(r['成功']), int(r['碰撞']), int(r['超时']), f'=D{i}/C{i}', f'=E{i}/C{i}', f'=F{i}/C{i}']); blue(ws, i, 'CDEF')
    for col in 'GHI': ws[f'{col}{i}'].number_format = '0.0%'
style(ws)

# ---- 正文数字（不在任何图表中的实验数字）
ws = sheet('正文数字', '4.2、4.3 节正文', '只列正文中出现、但不在任何图表里的实验数字', ['位置', '内容', '值', '来源'], [12, 60, 22, 30])
pr = rd(f'{A}/oprime_task/pairs.csv')[0]
ws.append(['4.2 节', '本文方法 − UAV-iDP3 任务成功率配对差（百分点）与 95% 区间', f"{pr['差%']} [{pr['区间下%']}, {pr['区间上%']}]", 'oprime_task/pairs.csv'])
for k, v in json.load(open(f'{A}/oprime_task/text_numbers.json')).items():
    if '完成数' in k or '保持' in k or '失败任务数' in k: ws.append(['4.2 节、4.3 节、摘要、贡献 3、结论', k, v, 'oprime_task/text_numbers.json'])
style(ws)

# ---- 表S1 0.5 m
ws = sheet('表S1 0.5m', '补充材料 S1 表S1', '0.5 m 标准、按任务统计下本文方法仍为最高', ['方法', '任务', '成功', '稀疏任务', '稀疏成功', '适中任务', '适中成功', '密集任务', '密集成功', '碰撞', '超时', '成功率 总体', '稀疏', '适中', '密集', '碰撞率', '超时率'], [24] + [7] * 10 + [9] * 6)
for r in rd(f'{A}/oprime_task/main_05m.csv'):
    i = ws.max_row + 1
    ws.append([r['方法']] + [int(r[k]) for k in ['任务', '成功', '稀疏任务', '稀疏成功', '适中任务', '适中成功', '密集任务', '密集成功', '碰撞', '超时']] + [f'=C{i}/B{i}', f'=E{i}/D{i}', f'=G{i}/F{i}', f'=I{i}/H{i}', f'=J{i}/B{i}', f'=K{i}/B{i}'])
    blue(ws, i, 'BCDEFGHIJK')
    for col in 'LMNOPQ': ws[f'{col}{i}'].number_format = '0.0%'
style(ws)

# ---- 表S2 第二次运行
ws = sheet('表S2 第二次运行', '补充材料 S2 表S2；第5章局限一句', '后训练结果对训练随机性敏感（预先登记 R4、R2 判为本预算下不符合采纳标准，判定在 0.5 m、按每次评价下作出）', ['方法', '任务', '成功', '稀疏任务', '稀疏成功', '适中任务', '适中成功', '密集任务', '密集成功', '碰撞', '超时', '成功率 总体', '稀疏', '适中', '密集', '碰撞率', '超时率'], [24] + [7] * 10 + [9] * 6)
for r in rd(f'{A}/oprime_task/second_run.csv'):
    i = ws.max_row + 1
    ws.append([r['方法']] + [int(r[k]) for k in ['任务', '成功', '稀疏任务', '稀疏成功', '适中任务', '适中成功', '密集任务', '密集成功', '碰撞', '超时']] + [f'=C{i}/B{i}', f'=E{i}/D{i}', f'=G{i}/F{i}', f'=I{i}/H{i}', f'=J{i}/B{i}', f'=K{i}/B{i}'])
    blue(ws, i, 'BCDEFGHIJK')
    for col in 'LMNOPQ': ws[f'{col}{i}'].number_format = '0.0%'
style(ws)

# ---- 图S1
ws = sheet('图S1 第二次运行训练', '补充材料 S2 图S1', '第二次运行的训练过程', ['曲线', '轮次', '采集成功率（训练到达奖励口径）', '近似 KL 中位数'], [30, 12, 16, 14])
for r in rd(f'{A}/oprime/curve_blocks.csv'):
    if r['策略'] in ('P14', 'P15'):
        i = ws.max_row + 1; ws.append([NAME[r['策略']], r['轮'], float(r['采集到达率%']) / 100, float(r['KL中位数'])]); blue(ws, i, 'CD')
        ws[f'C{i}'].number_format = '0.0%'; ws[f'D{i}'].number_format = '0.00E+00'
style(ws)

# ---- 表S3 运动学全部 199 个任务（按每次评价）
ws = sheet('表S3 运动学全部任务', '补充材料 S3 表S3', '评价前确定的标准：全部 199 个任务、每次评价单独统计、0.5 m（预先登记判定所用标准）', ['方法', '回合', '成功', '稀疏回合', '稀疏成功', '适中回合', '适中成功', '密集回合', '密集成功', '碰撞', '超时', '成功率 总体', '稀疏', '适中', '密集', '碰撞率', '超时率'], [24] + [7] * 10 + [9] * 6)
for r in rd(f'{A}/oprime_task/full199_episode_05m.csv'):
    i = ws.max_row + 1
    ws.append([r['方法']] + [int(r[k]) for k in ['回合', '成功', '稀疏回合', '稀疏成功', '适中回合', '适中成功', '密集回合', '密集成功', '碰撞', '超时']] + [f'=C{i}/B{i}', f'=E{i}/D{i}', f'=G{i}/F{i}', f'=I{i}/H{i}', f'=J{i}/B{i}', f'=K{i}/B{i}'])
    blue(ws, i, 'BCDEFGHIJK')
    for col in 'LMNOPQ': ws[f'{col}{i}'].number_format = '0.0%'
style(ws)

# ---- 表S4 Gazebo 全部 48 个任务
ws = sheet('表S4 Gazebo全部任务', '补充材料 S4 表S4', '全部 48 个任务按任务统计（正文表5 去除 8 个任务，清单 gazebo/exclusions.json）', ['难度', '方法', '任务', '成功', '碰撞', '超时', '成功率', '碰撞率', '超时率'], [7, 14, 7, 7, 7, 7, 9, 9, 9])
for r in rd(f'{A}/gazebo/full48_task.csv'):
    i = ws.max_row + 1; ws.append([r['难度'], r['方法'], int(r['任务']), int(r['成功']), int(r['碰撞']), int(r['超时']), f'=D{i}/C{i}', f'=E{i}/C{i}', f'=F{i}/C{i}']); blue(ws, i, 'CDEF')
    for col in 'GHI': ws[f'{col}{i}'].number_format = '0.0%'
style(ws)
ws = sheet('表S5 Gazebo按次', '补充材料 S4 表S5', '正文 40 个任务按每次飞行统计（改口径前的结果）', ['难度', '方法', '回合', '成功', '碰撞', '超时', '成功率', '碰撞率', '超时率'], [7, 14, 7, 7, 7, 7, 9, 9, 9])
for r in rd(f'{A}/gazebo/table5_episode.csv'):
    i = ws.max_row + 1; ws.append([r['难度'], r['方法'], int(r['回合']), int(r['成功']), int(r['碰撞']), int(r['超时']), f'=D{i}/C{i}', f'=E{i}/C{i}', f'=F{i}/C{i}']); blue(ws, i, 'CDEF')
    for col in 'GHI': ws[f'{col}{i}'].number_format = '0.0%'
style(ws)

# ---- 说明
ws = wb.active; ws.title = '说明'; ws.column_dimensions['A'].width = 22; ws.column_dimensions['B'].width = 46; ws.column_dimensions['C'].width = 90
for t in ['论文数据表（2026-11-08）：论文正文与补充材料中全部图表及正文实验数字的数据，一页一个图表，按论文顺序。',
          '成功 = 碰撞前进入目标 1.5 m；结局分成功、碰撞、超时。运动学评价：41 个世界、190 个任务，每任务 5 次，按任务统计（至少 3 次成功即成功；否则按失败较多的一类，相同记碰撞）；全部 199 个任务按评价前标准（每次评价、0.5 m）见表S3 页；Gazebo：正文 40 个任务 × 2 次，按任务统计（至少一次成功即成功；两次均失败时任一次碰撞记碰撞，否则超时）；全部 48 个任务见表S4 页，按每次飞行见表S5 页。',
          '图1—图4 为方法示意图，不含实验数据。蓝字为原始计数或原始值，黑字为公式。', '']:
    ws.append([t]); ws.cell(ws.max_row, 1).font = Font(name=F, bold=(ws.max_row == 1))
ws.append(['页', '用在论文哪里', '支撑什么结论'])
for c in ws[ws.max_row]: c.font = Font(name=F, bold=True); c.fill = H
for t in INDEX: ws.append(list(t))
for row in ws.iter_rows(min_row=5):
    for c in row: c.font = Font(name=F, bold=c.font.bold); c.alignment = Alignment(wrap_text=True, vertical='top')
wb.save(OUT); print('saved')
