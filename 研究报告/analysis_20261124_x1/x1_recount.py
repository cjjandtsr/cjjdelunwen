"""只读：从 X1 原始量独立复算 a、β、ρ、c、D、P6 五种目标的损失与 bootstrap 区间（只需 numpy，不需 torch）。

用法：python3 x1_recount.py <X1 解包目录>
  X1 包：项目仓库分支 f9-pack/run01-20261122（提交 d254692）
        jindu/f9_run01_20261122/x1/routea_f9_x1_20261124.tar.gz（SHA256 前 16 位 4ffa2b58f50813b5），
  解包后的 routea_f9_run01/x1/ 目录。
读取：x1_raw_run甲.pt（P6、P35、P36）、x1_raw_run乙.pt（P6、P28、P29）、x1_states.json。
定义见 研究报告/2026-11-24_F9吸收失败原因核查_代码文献与下一步诊断_v1_1.md 第六节。
"""
import io, json, pickle, sys, zipfile
from pathlib import Path
import numpy as np

D = Path(sys.argv[1])
DT = {'FloatStorage': np.float32, 'DoubleStorage': np.float64, 'LongStorage': np.int64,
      'IntStorage': np.int32, 'BoolStorage': np.bool_, 'HalfStorage': np.float16, 'ByteStorage': np.uint8}


def tload(path):
    """不依赖 torch 读取 torch.save 的 zip 格式。"""
    z = zipfile.ZipFile(path); root = z.namelist()[0].split('/')[0]

    class St:
        def __init__(s, n): s.n = n

    def rebuild(storage, offset, size, stride, *a):
        if len(size) == 0: return storage[offset]
        return np.lib.stride_tricks.as_strided(storage[offset:], shape=size,
                                               strides=[x*storage.itemsize for x in stride]).copy()

    class U(pickle.Unpickler):
        def find_class(s, mod, name):
            if mod == 'torch._utils' and name in ('_rebuild_tensor_v2', '_rebuild_tensor'): return rebuild
            if mod == 'torch' and name.endswith('Storage'): return St(name)
            if mod == 'collections' and name == 'OrderedDict':
                import collections; return collections.OrderedDict
            return super().find_class(mod, name)

        def persistent_load(s, pid):
            _, st, key, loc, numel = pid
            return np.frombuffer(z.read(f'{root}/data/{key}'), dtype=DT[st.n])
    return U(io.BytesIO(z.read(f'{root}/data.pkl'))).load()


r1, r2 = tload(D/'x1_raw_run甲.pt'), tload(D/'x1_raw_run乙.pt')
B, G, DL = {}, {}, {}
for raw in (r1, r2):
    for p in raw['policies']:
        B.setdefault(p, np.stack([np.asarray(v, np.float64) for v in raw['b'][p]]))
        G.setdefault(p, np.stack([np.asarray(v, np.float64) for v in raw['g'][p]]))
        DL.setdefault(p, np.array(raw['delta'][p], float))
print('P6 两棵树 b、g 逐位相同：', np.array_equal(np.stack(r1['b']['P6']), np.stack(r2['b']['P6'])),
      np.array_equal(np.stack(r1['g']['P6']), np.stack(r2['g']['P6'])))
W = np.zeros((16, 11)); W[2:6, [0, 1, 2, 9]] = 1
nrm = lambda x: ((x**2)*W).sum((-1, -2))/16
Dl = G['P6'] - B['P6']; den = nrm(Dl)
states = json.load(open(D/'x1_states.json'))['states']; src = [set(s['sources']) for s in states]
POL = ['P6', 'P29', 'P28', 'P35', 'P36']
print('状态数 %d；mean||Δ||² = %.6f' % (len(den), den.mean()))


def metrics(idx):
    d = den[idx].sum(); out = {}
    for p in POL:
        a = nrm(B[p][idx]-G['P6'][idx]).sum()/d
        beta = ((B[p][idx]-B['P6'][idx])*Dl[idx]*W).sum()/16/d
        rho = nrm(B[p][idx]-B['P6'][idx]).sum()/d
        c = nrm(B[p][idx]-G[p][idx]).sum()/d
        out[p] = dict(a=a, beta=beta, rho=rho, c=c, D=(DL[p][idx] >= .05).mean(), identity_err=abs(a-(1-2*beta+rho)))
    return out


print('== 整体（比值均为对状态求和后相除）')
for p, v in metrics(np.arange(len(den))).items():
    print(p, ' '.join('%s=%.4f' % (k, x) for k, x in v.items()))

print('== P6 五种目标的十步平均损失（两棵树逐位相同：%s）' % all(
    np.array_equal([t['losses'][k] for t in r1['p6']['loss_targets']], [t['losses'][k] for t in r2['p6']['loss_targets']])
    for k in ('original', 'b', 's', 'h', 'g')))
L = {k: np.array([t['losses'][k] for t in r1['p6']['loss_targets']]) for k in ('original', 'b', 's', 'h', 'g')}
print(' '.join('L(%s)=%.5f' % (k, v.mean()) for k, v in L.items()))
lhs, rhs = L['s'].mean()-L['b'].mean(), .5*L['original'].mean()
print('Q1：L(s)−L(b) = %.5f，0.5×L(original) = %.5f → %s' % (lhs, rhs, '满足' if lhs >= rhs else '不满足'))
print('M2：L(g)−L(b) = %.5f；L(h)−L(s) = %.5f' % (L['g'].mean()-L['b'].mean(), L['h'].mean()-L['s'].mean()))
S = np.stack([np.asarray(v, np.float64) for v in r1['p6']['s']]); H = np.stack([np.asarray(v, np.float64) for v in r1['p6']['h']])
Db = (H-S).mean(1); denS = nrm(Db)
print('随机样本相对确定性输出的散布 mean||s_k−b||² = %.6f；mean||Δ̄||² = %.6f（为确定性 Δ 的 %.3f 倍）'
      % (((((S-B['P6'][:, None])**2)*W).sum((-1, -2))/16).mean(), denS.mean(), denS.mean()/den.mean()))
for p in POL[1:]:
    print(p, 'β(随机 Δ̄) = %.4f' % (((B[p]-B['P6'])*Db*W).sum()/16/denS.sum()))

print('== bootstrap（10000 次，种子 2026112401，对状态整体重抽，比值为求和后相除）')
rng = np.random.default_rng(2026112401); n = len(den); boot = {p: [] for p in POL[1:]}
for _ in range(10000):
    m = metrics(rng.integers(0, n, n))
    for p in boot: boot[p].append((m[p]['a'], m[p]['beta'], m[p]['c']))
for p, v in boot.items():
    v = np.array(v); q = lambda j: np.percentile(v[:, j], [2.5, 97.5])
    print(p, 'a [%.3f, %.3f]  β [%.3f, %.3f]  c [%.3f, %.3f]' % (*q(0), *q(1), *q(2)))

print('== 来源子集（a / β / c）')
for name in ('P28', 'P35', 'P36'):
    idx = np.array([i for i, s in enumerate(src) if name in s]); m = metrics(idx)
    print(name, 'n=%d' % len(idx), '  '.join('%s %.3f/%.3f/%.3f' % (p, m[p]['a'], m[p]['beta'], m[p]['c']) for p in POL[1:]))

T = ['P28', 'P35', 'P36']; m = metrics(np.arange(len(den)))
q2a = all(m[p]['a'] <= .7 and m[p]['a'] <= m['P29']['a']-.15 for p in T)
q2b = all(m[p]['a'] > .85 and m[p]['beta'] < .3 for p in T)
print('Q2a %s；Q2b %s；→ %s' % (q2a, q2b, 'Q2a' if q2a else 'Q2b' if q2b else 'Q2c'))
