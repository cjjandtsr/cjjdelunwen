"""由 P15 扩展集 trace 头重建扩展集 v2 的任务表（冻结 bank 未回传时用于 G12 直线参考与 S3），只读。
运行：python3 -I make_extv2_bank.py <P15 ext traces 目录> <extv2_review_tasks.json> <out bank.json>"""
import json, sys, glob, os
d, tasks_p, out = sys.argv[1:4]
cat = {t['task_id']: t['w1'] for t in json.load(open(tasks_p))}
tasks, worlds, eps = {}, {}, []
for f in sorted(glob.glob(os.path.join(d, '*.jsonl'))):
    h = json.loads(open(f).readline())
    eps.append(dict(task_id=h['task_id'], repeat=h['repeat']))
    worlds.setdefault(h['world_id'], dict(geometry=h['geometry']))
    tasks.setdefault(h['task_id'], dict(task_id=h['task_id'], world_id=h['world_id'], role=h['role'], payload=h['task'], category=cat[h['task_id']]))
json.dump(dict(split='rl_test_ext_v2_rebuilt', tasks=list(tasks.values()), worlds=worlds, episodes=eps), open(out, 'w'))
print(len(tasks), len(worlds), len(eps))
