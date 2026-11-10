"""汇编论文数据包（只读，不改任何分析结果）：把论文正文与补充材料用到的全部数据整理到 论文数据包/，
供审稿人索取原始数据、其他智能体复核时使用。
运行（论文仓库根目录）：python3 -I 研究报告/analysis_20261108/build_data_package.py <rows.json> <论文数据包目录> [Codex几何包目录] [Codex图6包目录]
rows.json 为 o_prime_analysis.py 的逐回合输出（7 个策略 × 995 回合）。输出均为 UTF-8（带 BOM）CSV，可直接用 Excel 打开。"""
import json, csv, os, sys, shutil, hashlib, collections
ROWS, OUT = sys.argv[1:3]
GEO = sys.argv[3] if len(sys.argv) > 3 else None
FIG = sys.argv[4] if len(sys.argv) > 4 else None
A = '研究报告/analysis_20261108'
os.makedirs(OUT, exist_ok=True)
def d(*p):
    q = os.path.join(OUT, *p); os.makedirs(os.path.dirname(q), exist_ok=True); return q
def wcsv(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
def cp(src, *dst):
    if os.path.exists(src): shutil.copy2(src, d(*dst)); return True
    print('缺少', src); return False

NAME = {'P0': 'UAV-iDP3', 'P2': 'Reg-DPPO w/o Stage II', 'P3': 'Single-stage DPPO', 'P4': 'Reg-DPPO w/o BC reg.',
        'P6': '本文方法', 'P14': 'Reg-DPPO w/o Stage II（第二次运行）', 'P15': '本文方法（第二次运行）'}
R = json.load(open(ROWS))
EXC = json.load(open(f'{A}/oprime/exclusions.json'))
exc = set(EXC['tasks'])
reason = {}
for r in R:
    if r['task'] in exc:
        reason[r['task']] = ('几何与训练场景相同（用户 11-10）' if 'initial_yaw_offset_corridor__000015' in r['world']
                             else 'cul_de_sac_trap 类、两方法 5 次均失败（用户 11-09，结果后决定）')

# 1 运动学逐回合
def ep15(r): return '成功' if (r['out'] == 'reached' or r['near'] < 1.5) else ('碰撞' if r['out'] == 'collision' else '超时')
def ep05(r): return '成功' if (r['out'] == 'reached' or r['near'] < 0.5) else ('碰撞' if r['out'] == 'collision' else '超时')
rows = []
for r in sorted(R, key=lambda x: (x['policy'], x['world'], x['task'], int(x['rep']))):
    rows.append([r['policy'], NAME[r['policy']], r['task'], r['world'], r['cat'], r['rep'], r['out'], r['near'], r['t'],
                 ep15(r), ep05(r), r.get('rho', ''), '否' if r['task'] in exc else '是', reason.get(r['task'], '')])
wcsv(d('01_运动学逐回合', 'kinematic_episodes.csv'),
     ['策略编号', '方法名', '任务ID', '场景ID', '难度', '重复', '原始终止类型', '最小目标距离m', '终止时刻', '结局_1.5m', '结局_0.5m', '航线障碍体积比rho', '计入正文统计', '去除原因'], rows)
cp(f'{A}/oprime/exclusions.json', '01_运动学逐回合', 'exclusions.json')
cp(ROWS, '01_运动学逐回合', 'rows.json')
cp(f'{A}/codex_details/tasks_199.csv', '01_运动学逐回合', 'tasks_199_起终点.csv')
cp(f'{A}/codex_details/worlds_63.csv', '01_运动学逐回合', 'worlds_63_场景几何统计.csv')
if GEO:
    cp(f'{GEO}/geometry/worlds_40.csv', '01_运动学逐回合', 'worlds_40_测试场景.csv')
    cp(f'{GEO}/geometry/tasks_186.csv', '01_运动学逐回合', 'tasks_186_测试任务.csv')
    cp(f'{GEO}/geometry/summary.json', '01_运动学逐回合', '几何核对_summary.json')
    cp(f'{GEO}/geometry/near_geometry_matches.csv', '01_运动学逐回合', '几何近重复.csv')
    cp(f'{GEO}/geometry/geometry_matches.csv', '01_运动学逐回合', '几何完全重合.csv')

# 2 运动学汇总（正文表2、表4，4.2/4.3 数字，补充表 S1—S3）
for f in ['main.csv', 'main_05m.csv', 'second_run.csv', 'pairs.csv', 'table3.csv', 'text_numbers.json', 'full199_episode_05m.csv']:
    cp(f'{A}/oprime_task/{f}', '02_运动学汇总', f)
cp(f'{A}/path_eff_main/path_eff_episodes.csv', '02_运动学汇总', 'path_eff_episodes.csv')
cp(f'{A}/path_eff_main/path_eff.csv', '02_运动学汇总', 'path_eff.csv')

# 3 Gazebo
G = json.load(open(f'{A}/gazebo/gazebo_rows.json')); GE = json.load(open(f'{A}/gazebo/exclusions.json'))
def gin(r): return not (any(r['world'].endswith(w) for w in GE['worlds']) or any(r['task'].startswith(t) for t in GE['tasks']))
wcsv(d('03_Gazebo', 'gazebo_flights.csv'),
     ['方法', '任务ID前12位', '重复', '场景ID', '难度', '监控终止状态', '最小目标距离m', '结局_1.5m', '结局_1m', '结局_0.5m', '计入正文统计'],
     [[r['method'], r['task'], r['rep'], r['world'], r['cat'], r['monitor'], r['min3d'], r['out_main'], r['out1m'], r['out05'], '是' if gin(r) else '否']
      for r in sorted(G, key=lambda x: (x['method'], x['world'], x['task'], x['rep']))])
for f in ['exclusions.json', 'table5_task.csv', 'full48_task.csv', 'table5_episode.csv', 'full48_table_episode.csv', 'pairs.csv', 'checks.json']:
    cp(f'{A}/gazebo/{f}', '03_Gazebo', f)

# 4 训练过程（图7、图S1）
cp(f'{A}/oprime/curve_blocks.csv', '04_训练过程', 'curve_blocks.csv')
if GEO: cp(f'{GEO}/supplement/training_blocks.csv', '04_训练过程', 'training_blocks_Codex独立重算.csv')

# 5 图6 示例轨迹
if FIG:
    for f in ['figure_06_verification.json', 'selected_trajectories.json']:
        if os.path.exists(f'{FIG}/{f}'): cp(f'{FIG}/{f}', '05_图6轨迹', f)

# 6 数据表、台账、脚本
cp('研究报告/2026-11-08_论文数据表.xlsx', '06_数据表与台账', '论文数据表.xlsx')
for f in os.listdir('台账'): cp(f'台账/{f}', '06_数据表与台账', '台账', f)
for f in ['o_prime_analysis.py', 'kin_task_level.py', 'path_eff_1m.py', 'gazebo_analysis.py', 'fig10_select_1m.py',
          'paper_data_workbook.py', 'build_docx.py', 'build_data_package.py', 'renumber_refs.py', 'kin_task_lists.py']:
    cp(f'{A}/{f}', '07_脚本', f)

# 校验：正文表4 计数可由逐回合文件重算
lab = collections.defaultdict(list)
for r in rows:
    if r[12] == '是': lab[(r[0], r[2])].append(r[9])
cnt = collections.Counter()
for (p, t), v in lab.items():
    c = collections.Counter(v); cnt[(p, '成功' if c['成功'] >= 3 else ('碰撞' if c['碰撞'] >= c['超时'] else '超时'))] += 1
main = {r['方法']: r for r in csv.DictReader(open(f'{A}/oprime_task/main.csv', encoding='utf-8-sig'))}
for p in ['P0', 'P2', 'P3', 'P4', 'P6']:
    m = main[NAME[p]]
    assert (cnt[(p, '成功')], cnt[(p, '碰撞')], cnt[(p, '超时')]) == (int(m['成功']), int(m['碰撞']), int(m['超时'])), p
print('表4 计数由逐回合文件重算一致')

with open(d('sha256sums.txt'), 'w') as f:
    for root, _, fs in os.walk(OUT):
        for x in sorted(fs):
            if x == 'sha256sums.txt': continue
            q = os.path.join(root, x); f.write(f'{hashlib.sha256(open(q, "rb").read()).hexdigest()}  {os.path.relpath(q, OUT)}\n')
print('完成', OUT)
