"""项目仓库整理：把一个运行目录里的大文件转成紧凑形式（只读原文件，输出到新目录）。
用法：python3 -I summarize_run.py <仓库根> <运行目录相对路径> <输出根> <模式: slim|lossless>
处理规则：
  1. 训练逐轮 metrics_update_*.json(.gz)：每个臂输出
     <arm>__updates.csv.gz      每轮一行：formal_training / rollout_audit.episodes / rollout_audit.critic 下的全部标量（扁平化列名）
     <arm>__transitions.csv.gz  每条转移一行：核心字段（见 CORE），reward_terms 展开；不含动作块、梯度诊断等大字段
  2. 评价原迹 traces/*.jsonl(.gz)：
     lossless 模式：原文件 gzip（-n，可 gunzip 还原为逐字节相同的原文件；原 SHA256 记入清单）
     slim 模式：删去 DROP 中的大字段（动作块、点云元数据、观测来源），其余保留，gzip 后输出
  3. 其他文件不动（由调用方决定是否保留）。
  每个被替换的原文件写入 <输出根>/<运行目录>/_整理清单.csv：原路径、原字节数、原 SHA256、处理方式、新路径。"""
import csv, glob, gzip, hashlib, io, json, os, re, sys
repo, run, outroot, mode = sys.argv[1:5]
src = os.path.join(repo, run); dst = os.path.join(outroot, run); os.makedirs(dst, exist_ok=True)
DROP = {'full_action_16x11', 'pointcloud_metadata_before', 'pointcloud_metadata_after', 'policy_action_8x11', 'initial_pointcloud_metadata',
        'observation_provenance', 'observation_provenance_after', 'pointcloud_metadata', 'action_chunk'}
CORE = ['episode_id', 'decision_index', 'task_id', 'world_id', 'role', 'reset_seed', 'task_seed', 'goal_xyz', 'position_before_xyz', 'position_after_xyz',
        'yaw_before', 'yaw_after', 'terminated', 'truncated', 'collection_boundary', 'reward', 'value', 'next_value', 'advantage_raw', 'return_target', 'done_reason']
manifest = []
def sha(b): return hashlib.sha256(b).hexdigest()
def rd(p):
    b = open(p, 'rb').read(); raw = gzip.decompress(b) if p.endswith('.gz') else b; return b, raw
def flat(x, pre, out):
    if isinstance(x, dict):
        for k, v in x.items(): flat(v, pre + '.' + k if pre else k, out)
    elif isinstance(x, (int, float, str, bool)) or x is None:
        out[pre] = x
def wcsv(path, rows):
    cols = sorted({k for r in rows for k in r}, key=lambda c: (c != 'update', c))
    with gzip.open(path, 'wt', newline='') as h:
        w = csv.DictWriter(h, fieldnames=cols); w.writeheader(); [w.writerow(r) for r in rows]
# 1. 训练逐轮记录
arms = {}
for p in glob.glob(os.path.join(src, '**', 'metrics_update_*.json*'), recursive=True):
    arms.setdefault(os.path.dirname(p), []).append(p)
for d, files in sorted(arms.items()):
    rel = os.path.relpath(d, src); tag = rel.replace('/', '__'); U, T = [], []
    for p in sorted(files):
        b, raw = rd(p); m = json.loads(raw); u = int(re.search(r'(\d+)', os.path.basename(p)).group(1))
        row = {'update': u}
        for key in ('formal_training', 'counters', 'r1_plan_probe'):
            if isinstance(m.get(key), dict): flat(m[key], key, row)
        ra = m.get('rollout_audit') or {}
        for key in ('episodes', 'critic', 'reward', 'learning_targets', 'action'):
            if isinstance(ra.get(key), dict): flat(ra[key], 'rollout_audit.' + key, row)
        U.append(row)
        for t in ra.get('transition_records') or []:
            r = {'update': u}
            for k in CORE:
                if k in t:
                    v = t[k]; r[k] = json.dumps(v) if isinstance(v, (list, dict)) else v
            for k, v in (t.get('reward_terms') or {}).items(): r['rt.' + k] = v
            tf = t.get('terminal_facts')
            if isinstance(tf, dict):
                for k in ('kind', 'done_reason', 'physical_done_reason', 'reached', 'collision'):
                    if k in tf: r['tf.' + k] = json.dumps(tf[k]) if isinstance(tf[k], (list, dict)) else tf[k]
            if isinstance(t.get('f7_audit'), dict):
                for k, v in t['f7_audit'].items():
                    if isinstance(v, (int, float, bool)): r['f7.' + k] = v
            T.append(r)
        manifest.append((os.path.relpath(p, repo), len(b), sha(raw), '训练记录汇总', f'{run}/_汇总/训练/{tag}__*.csv.gz'))
    os.makedirs(os.path.join(dst, '_汇总', '训练'), exist_ok=True)
    wcsv(os.path.join(dst, '_汇总', '训练', tag + '__updates.csv.gz'), U)
    if T: wcsv(os.path.join(dst, '_汇总', '训练', tag + '__transitions.csv.gz'), T)
    print('训练', rel, len(files), '轮', len(T), '条转移', flush=True)
# 2. 评价原迹
n = 0
for p in sorted(glob.glob(os.path.join(src, '**', 'traces', '*.jsonl*'), recursive=True)):
    b, raw = rd(p); relp = os.path.relpath(p, repo)
    newrel = relp if relp.endswith('.gz') else relp + '.gz'
    if mode == 'lossless':
        if p.endswith('.gz'): continue
        out = gzip.compress(raw, 9, mtime=0); how = '无损 gzip'
    else:
        lines = []
        for l in raw.decode().splitlines():
            if not l.strip(): continue
            r = json.loads(l); [r.pop(k, None) for k in DROP]; lines.append(json.dumps(r, separators=(',', ':')))
        out = gzip.compress(('\n'.join(lines) + '\n').encode(), 9, mtime=0); how = '精简（删去动作块、点云元数据、观测来源）+ gzip'
    q = os.path.join(outroot, newrel); os.makedirs(os.path.dirname(q), exist_ok=True); open(q, 'wb').write(out)
    manifest.append((relp, len(b), sha(raw), how, newrel)); n += 1
print('原迹', n, '个', flush=True)
with open(os.path.join(dst, '_整理清单.csv'), 'w', newline='') as h:
    w = csv.writer(h); w.writerow(['原路径', '原字节数', '原内容SHA256（gz 文件为解压后内容）', '处理方式', '新位置']); w.writerows(manifest)
print('清单', len(manifest), '项')
