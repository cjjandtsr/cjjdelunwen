"""补充材料 S3（O′）：分类界限敏感性。rho = 0 为稀疏；0 < rho ≤ t 为适中；rho > t 为密集；正文 t = 0.04623，另取 0.5t、2t。
运行：python3 -I s3_oprime.py oprime/rows.json > oprime/s3_threshold.csv"""
import json, sys, collections
R = json.load(open(sys.argv[1])); T0 = 0.04623
CAT = {'zero': '稀疏', 'low': '适中', 'high': '密集'}
for r in R:
    assert r['rho'] is not None
    c = '稀疏' if r['rho'] == 0 else ('适中' if r['rho'] <= T0 else '密集')
    assert c == r['cat'], (r['policy'], r['task'])
P = ['P0', 'P2', 'P3', 'P4', 'P6']
print('界限倍数,界限,类别,回合,' + ','.join(f'{p}到达' for p in P) + ',P6−P0(百分点)')
for k in (0.5, 1.0, 2.0):
    t = T0 * k
    for cls in ('适中', '密集'):
        sel = lambda r: (0 < r['rho'] <= t) if cls == '适中' else (r['rho'] > t)
        n = {p: [r for r in R if r['policy'] == p and sel(r)] for p in P}
        a = {p: sum(r['out'] == 'reached' for r in n[p]) for p in P}
        N = len(n['P0'])
        print(f"{k},{t:.5f},{cls},{N}," + ','.join(str(a[p]) for p in P) + f",{100*(a['P6']-a['P0'])/N:+.1f}")
