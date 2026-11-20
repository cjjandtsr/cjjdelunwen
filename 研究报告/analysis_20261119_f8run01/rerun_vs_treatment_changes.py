"""只读：dev420 上逐条件（任务×重复）结局改变数，比较“处理对对照”“同 seed 重跑”“不同 seed”三类配对。
用法：python3 -I rerun_vs_treatment_changes.py <F8 核验导出目录> <f7_episodes.json>
P18/P22 同为 seed 202611081、P19/P23 同为 202611082（Codex 11-19 核对 YAML 确认），均为 P6→u320 同配方。
配对键 = (task_id, repeat)；同时核对两边初始观测 hash 一致。结局为 1 m 互斥口径（S/C/T）。"""
import csv, json, sys, collections
D, F7 = sys.argv[1:3]
M = {'reached': 'S', 'collision': 'C', 'time_limit': 'T'}
O = collections.defaultdict(dict); H = collections.defaultdict(dict)
for r in csv.DictReader(open(f'{D}/evaluation_conditions.csv', encoding='utf-8-sig')):
    if r['split'] == 'dev': O[r['arm']][(r['task_id'], int(r['repeat']))] = M[r['outcome']]; H[r['arm']][(r['task_id'], int(r['repeat']))] = r['initial_hash']
for r in json.load(open(F7)):
    if r['split'] == 'dev' and r['pol'] in ('P6', 'P18', 'P19'): O[r['pol']][(r['task'], int(r['rep']))] = r['out']; H[r['pol']][(r['task'], int(r['rep']))] = r['init']
def cmp(a, b):
    K = set(O[a]) & set(O[b]); ch = sum(O[a][k] != O[b][k] for k in K)
    sa = sum(O[a][k] == 'S' for k in K); sb = sum(O[b][k] == 'S' for k in K)
    gain = sum(O[a][k] == 'S' and O[b][k] != 'S' for k in K); loss = sum(O[b][k] == 'S' and O[a][k] != 'S' for k in K)
    hm = sum(H[a][k] != H[b][k] for k in K)
    print(f'  {a:4s} 对 {b:4s}：配对 {len(K)}，初始 hash 不一致 {hm}，三类结局改变 {ch}，到达与否改变 {gain + loss}，到达 {sa} 对 {sb}（新增 {gain} / 流失 {loss}）')
print('== 处理对对照（同 seed）'); cmp('P20', 'P22'); cmp('P21', 'P23')
print('== 同 seed、同配方重跑'); cmp('P22', 'P18'); cmp('P23', 'P19')
print('== 同配方、不同 seed'); cmp('P18', 'P19'); cmp('P22', 'P23')
print('== 处理臂之间（不同 seed）'); cmp('P20', 'P21')
