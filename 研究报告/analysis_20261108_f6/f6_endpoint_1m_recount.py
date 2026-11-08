"""Recount F3/F5 dev420 #E2 outcomes under the 1 m primary endpoint (project line, not for the paper).
1 m success = executed path (truncated at the first physical event) comes within 1.0 m of the goal centre.
Usage: python3 -I f6_endpoint_1m_recount.py <project-repo>/jindu/routea_f5_run01/results/eval_dev/full P6 P8 P9 P10 P11"""
import json, sys, os, ast, math
root = sys.argv[1]
for p in sys.argv[2:]:
    d = os.path.join(root, p, 'traces'); c = dict(n=0, r05=0, tl1=0, co1=0, col=0, tlfar=0)
    for f in os.listdir(d):
        L = [json.loads(l) for l in open(os.path.join(d, f))]
        task = L[0]['task'] if isinstance(L[0]['task'], dict) else ast.literal_eval(L[0]['task'])
        g = task['goal_pos']; out = L[-1]['done_reason']
        mind = min(math.dist(q, g) for t in L[1:] if t.get('type') == 'transition' for q in t['executed_path'])
        c['n'] += 1; c['r05'] += out == 'reached'
        c['tl1'] += out == 'time_limit' and mind < 1.0; c['tlfar'] += out == 'time_limit' and mind >= 1.0
        c['co1'] += out == 'collision' and mind < 1.0; c['col'] += out == 'collision'
    print('%s n=%d | 0.5m reached %d | 1m success %d (= +%d timeouts, +%d collisions after entering 1 m) | '
          'remaining failures: collision %d, far timeout %d' % (p, c['n'], c['r05'], c['r05'] + c['tl1'] + c['co1'],
          c['tl1'], c['co1'], c['col'] - c['co1'], c['tlfar']))
