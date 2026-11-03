"""Near-goal timeout distribution (read-only). Usage: python3 -I prelim_timeouts.py <jindu_root>"""
import json, glob, sys, os
root = sys.argv[1]
for name, d in [('P0 dev','routea_f5_run01/results/eval_dev/full/bc'),('P6 dev','routea_f5_run01/results/eval_dev/full/P6'),('P6 val','routea_f5_run01/results/eval_val/full/P6')]:
    v = []
    for f in glob.glob(os.path.join(root, d, 'commits', '*')):
        s = json.load(open(f))['summary']
        if s['done_reason'] == 'time_limit': v.append(s['trajectory_metrics']['min_goal_distance_m'])
    v.sort(); n = len(v)
    q = lambda p: v[min(n-1, int(p*n))]
    print(name, 'n', n, 'min %.3f q25 %.3f median %.3f q75 %.3f max %.3f' % (v[0], q(.25), q(.5), q(.75), v[-1]),
          '<1m', sum(x < 1 for x in v), '<0.6m', sum(x < .6 for x in v))
