"""扩展集 v2：trace 记录声明的类别与 ρ 是否等于 extv2_review.py 的独立复算。
运行：python3 -I extv2_category_check.py <extv2_review_tasks.json> <P15 ext package json>；期望输出 mismatches 0"""
import json, sys
T = {t['task_id']: t for t in json.load(open(sys.argv[1]))}
R = json.load(open(sys.argv[2]))['records']
bad = [r['task_id'] for r in R if T[r['task_id']]['w1'] != r['category'] or abs(T[r['task_id']]['rho_1'] - r['rho_1_0']) > 1e-9]
print('records', len(R), 'mismatches', len(bad))
