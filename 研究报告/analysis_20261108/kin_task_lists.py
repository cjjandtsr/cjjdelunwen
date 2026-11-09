"""运动学 O′（42 个世界、199 个任务、每任务 5 次）按任务列名单，供用户整理数据（只读）。
运行：python3 -I kin_task_lists.py <rows.json> <out.xlsx>
成功 = 碰撞前进入目标 1 m。每个任务给出五种方法的成功次数（/5）与 UAV-iDP3、本文方法的失败方式。"""
import json, sys, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
R = json.load(open(sys.argv[1])); OUT = sys.argv[2]
ok = lambda r: r['out'] == 'reached' or r['near'] < 1
P = ['P0', 'P2', 'P3', 'P4', 'P6']; NM = ['UAV-iDP3', 'w/o Stage II', 'Single-stage DPPO', 'w/o BC reg.', '本文方法']
S = collections.defaultdict(collections.Counter); F = collections.defaultdict(collections.Counter); cat, wd = {}, {}
for r in R:
    if r['policy'] not in P: continue
    S[r['task']][r['policy']] += ok(r); cat[r['task']] = r['cat']; wd[r['task']] = r['world'].replace('routeA_rl_v1__', '')
    if not ok(r): F[(r['task'], r['policy'])]['碰撞' if r['out'] == 'collision' else '超时'] += 1
wc = collections.Counter(wd.values())
typ = lambda t: wd[t].split('__rl_test__')[-1].rsplit('__', 1)[0]
fm = lambda t, p: '、'.join(f'{k}{v}' for k, v in F[(t, p)].items()) or '—'
H = ['任务', '世界', '任务类型', '难度', '该世界任务数'] + [f'{n} 成功/5' for n in NM] + ['UAV-iDP3 失败', '本文方法 失败']
wb = Workbook(); wb.remove(wb.active)
def sheet(name, note, ts):
    ws = wb.create_sheet(name); ws.append([note]); ws['A1'].font = Font(name='Arial', italic=True); ws.append(H)
    for c in ws[2]: c.font = Font(name='Arial', bold=True); c.fill = PatternFill('solid', start_color='DCE6F3')
    for t in sorted(ts, key=lambda t: (typ(t), wd[t], t)):
        ws.append([t[:12], wd[t], typ(t), cat[t], wc[wd[t]]] + [S[t][p] for p in P] + [fm(t, 'P0'), fm(t, 'P6')])
    for i, w in enumerate([14, 52, 28, 6, 8] + [10] * 5 + [12, 12]): ws.column_dimensions[chr(65 + i)].width = w
    ws.freeze_panes = 'A3'
T = sorted(S)
sheet('本文方法少于UAV-iDP3', '本文方法成功次数少于 UAV-iDP3 的任务', [t for t in T if S[t]['P6'] < S[t]['P0']])
sheet('两者都0', 'UAV-iDP3 与本文方法 5 次都失败的任务', [t for t in T if S[t]['P6'] == 0 and S[t]['P0'] == 0])
sheet('本文方法0', '本文方法 5 次都失败的任务（含 UAV-iDP3 有成功的）', [t for t in T if S[t]['P6'] == 0])
sheet('全部任务', '全部 199 个任务', T)
ws = wb.create_sheet('按世界'); ws.append(['世界', '任务类型', '任务数'] + [f'{n} 成功/回合' for n in NM]); 
for w in sorted(wc):
    ts = [t for t in T if wd[t] == w]; ws.append([w, typ(ts[0]), len(ts)] + [f'{sum(S[t][p] for t in ts)}/{5*len(ts)}' for p in P])
ws.column_dimensions['A'].width = 52; ws.column_dimensions['B'].width = 28
wb.save(OUT); print('saved')
