"""只读：从 X2 原始量复算 a、β、ρ 曲线；并用冻结条件特征做探针，估计"引导修正能从策略的条件特征里推广到未见状态多少"。只需 numpy。

用法：python3 x2_recount.py <X2 解包目录> <X1 解包目录> <F9 留出记录 records.pt 1> [<records.pt 2> ...]
  X2 包：项目仓库分支 f9-pack/run01-20261122（提交 3bd644c）jindu/f9_run01_20261122/x2/routea_f9_x2_20261124.tar.gz
        （SHA256 前 16 位 1c61ffa00a29e240），解包后的 routea_f9_run01/x2/
  X1 包：同分支 jindu/f9_run01_20261122/x1/routea_f9_x1_20261124.tar.gz，解包后的 routea_f9_run01/x1/
  留出记录：同分支 stageA、stageA2、stageA2_restart 三个包中 measure/offline/records.pt（取 U 中各状态的条件向量）
"""
import collections, io, json, pickle, sys, zipfile
from pathlib import Path
import numpy as np

X2, X1 = Path(sys.argv[1]), Path(sys.argv[2]); RECS = sys.argv[3:]
DT = {'FloatStorage': np.float32, 'DoubleStorage': np.float64, 'LongStorage': np.int64, 'IntStorage': np.int32,
      'BoolStorage': np.bool_, 'HalfStorage': np.float16, 'ByteStorage': np.uint8}


def tload(path):
    z = zipfile.ZipFile(path); root = z.namelist()[0].split('/')[0]

    class St:
        def __init__(s, n): s.n = n

    def rebuild(st, off, size, stride, *a):
        if len(size) == 0: return st[off]
        return np.lib.stride_tricks.as_strided(st[off:], shape=size, strides=[x*st.itemsize for x in stride]).copy()

    class U(pickle.Unpickler):
        def find_class(s, m, n):
            if m == 'torch._utils' and n in ('_rebuild_tensor_v2', '_rebuild_tensor'): return rebuild
            if m == 'torch' and n.endswith('Storage'): return St(n)
            if m == 'collections' and n == 'OrderedDict': return collections.OrderedDict
            return super().find_class(m, n)

        def persistent_load(s, pid):
            _, st, key, loc, numel = pid
            return np.frombuffer(z.read(f'{root}/data/{key}'), dtype=DT[st.n])
    return U(io.BytesIO(z.read(f'{root}/data.pkl'))).load()


W = np.zeros((16, 11)); W[2:6, [0, 1, 2, 9]] = 1; SEL = W.astype(bool)
nrm = lambda x: ((x**2)*W).sum((-1, -2))/16
x1 = tload(X1/'x1_raw_run甲.pt')
bP6 = np.stack([np.asarray(v, np.float64) for v in x1['b']['P6']]); gP6 = np.stack([np.asarray(v, np.float64) for v in x1['g']['P6']])
Dl = gP6 - bP6; den = nrm(Dl).sum()

print('== 1. X2 曲线（U = X1 的 83 个状态；mean||Δ||² = %.6f）' % (den/len(Dl)))
for arm in ('P37', 'P38'):
    r = tload(X2/('x2_raw_%s.pt' % arm))['measurements']
    print(arm, '第 0 步与 X1 的 b_P6 逐位相同：', np.array_equal(np.asarray(r[0]), np.stack(x1['b']['P6'])))
    for step, b in r.items():
        b = np.asarray(b, np.float64)
        a = nrm(b-gP6).sum()/den; beta = ((b-bP6)*Dl*W).sum()/16/den; rho = nrm(b-bP6).sum()/den
        print('  步 %4d  a %.4f  β %.4f  ρ %.4f' % (step, a, beta, rho))
for arm in ('P37', 'P38'):
    c = json.load(open(X2/('x2_curve_%s.json' % arm)))
    print(arm, '曲线文件键：', sorted(c.keys()))

print('== 2. 探针：只用冻结条件特征（576 维）预测引导修正 Δ，在 U 上评价')
tg = tload(X2/'x2_targets.pt')
CT = np.asarray(tg['cond'], np.float64); DTf = (np.asarray(tg['y'], np.float64) - np.asarray(tg['b0'], np.float64))[..., SEL]
cmap = {}
for p in RECS:
    for rec in tload(p):
        cmap.setdefault(rec['observation_sha256'], np.asarray(rec['condition'], np.float64).ravel())
states = json.load(open(X1/'x1_states.json'))['states']
CU = np.stack([cmap[s['observation_sha256']] for s in states]); DUf = Dl[..., SEL]
ep = np.array([sid.split('_')[0] + '|' + str(src) for sid, src in zip(tg['sample_ids'], tg['sources'])])
ueps = np.array(sorted(set(ep)))
print('训练状态 %d（%d 个回合），U 状态 %d；训练集 mean||Δ||² = %.6f' % (len(CT), len(ueps), len(CU), nrm(np.asarray(tg['y'], np.float64)-np.asarray(tg['b0'], np.float64)).mean()))
score = lambda P, D: ((P*D).sum()/(D**2).sum(), ((D-P)**2).sum()/(D**2).sum())   # (β, a)，W/16 两边约掉


def ridge(X, Y, lam):
    mu, sd = X.mean(0), X.std(0)+1e-8; Xs = (X-mu)/sd; ym = Y.mean(0)
    Wt = np.linalg.solve(Xs.T@Xs+lam*np.eye(X.shape[1]), Xs.T@(Y-ym))
    return lambda Z: ((Z-mu)/sd)@Wt+ym


def krr(X, Y, lam, gamma):
    mu, sd = X.mean(0), X.std(0)+1e-8; Xs = (X-mu)/sd; ym = Y.mean(0)
    K = lambda A, B: np.exp(-gamma*((A**2).sum(1)[:, None]+(B**2).sum(1)[None]-2*A@B.T)/X.shape[1])
    al = np.linalg.solve(K(Xs, Xs)+lam*np.eye(len(Xs)), Y-ym)
    return lambda Z: K((Z-mu)/sd, Xs)@al+ym


rng = np.random.default_rng(0); fold = {e: i % 5 for i, e in enumerate(rng.permutation(ueps))}; f = np.array([fold[e] for e in ep])


def cv(make):
    P = np.zeros_like(DTf)
    for k in range(5):
        tr = f != k; P[~tr] = make(CT[tr], DTf[tr])(CT[~tr])
    return score(P, DTf)


best_r = min(((lam,) + cv(lambda X, Y: ridge(X, Y, lam)) for lam in [1, 10, 100, 1e3, 1e4, 1e5]), key=lambda t: t[2])
best_k = min(((lam, g) + cv(lambda X, Y: krr(X, Y, lam, g)) for lam in [0.1, 1, 10] for g in [0.1, 0.3, 1, 3]), key=lambda t: t[3])
fr = ridge(CT, DTf, best_r[0]); fk = krr(CT, DTf, *best_k[:2])
print('岭回归 λ=%g：按回合 5 折交叉验证 β %.3f a %.3f；训练集内 β %.3f；U β %.3f a %.3f'
      % (best_r[0], best_r[1], best_r[2], score(fr(CT), DTf)[0], *score(fr(CU), DUf)))
print('核岭回归 λ=%g γ=%g：交叉验证 β %.3f a %.3f；训练集内 β %.3f；U β %.3f a %.3f'
      % (best_k[0], best_k[1], best_k[2], best_k[3], score(fk(CT), DTf)[0], *score(fk(CU), DUf)))
for k in (1, 5, 20):
    idx = np.argsort(((CU[:, None, :]-CT[None])**2).sum(-1), 1)[:, :k]
    print('最近邻 k=%d：U β %.3f a %.3f' % (k, *score(DTf[idx].mean(1), DUf)))
print('常数（训练集平均修正）：U β %.3f a %.3f' % score(np.repeat(DTf.mean(0, keepdims=True), len(DUf), 0), DUf))

print('== 3. 学习曲线（按回合抽子集，每档 20 次，U 上评价）')
rng = np.random.default_rng(1)
for frac in (0.125, 0.25, 0.5, 0.75, 1.0):
    rr, kk, ns = [], [], []
    for _ in range(20 if frac < 1 else 1):
        keep = set(rng.choice(ueps, int(round(frac*len(ueps))), replace=False)) if frac < 1 else set(ueps)
        m = np.array([e in keep for e in ep]); ns.append(m.sum())
        rr.append(score(ridge(CT[m], DTf[m], best_r[0])(CU), DUf)); kk.append(score(krr(CT[m], DTf[m], *best_k[:2])(CU), DUf))
    rr, kk = np.array(rr), np.array(kk)
    print('回合比例 %.3f（约 %d 个状态）：岭 β %.3f a %.3f ｜ 核岭 β %.3f a %.3f'
          % (frac, int(np.mean(ns)), rr[:, 0].mean(), rr[:, 1].mean(), kk[:, 0].mean(), kk[:, 1].mean()))
