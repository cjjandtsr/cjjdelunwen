"""只读：33 个直线被挡任务按测地路线类型（越顶/侧绕，前置研究②）与"是否被任一策略解决过"交叉。
用法：python3 -I route_type_vs_solved.py <analysis_20261116_f8pre/pre2_rows.json> <e1_blocked_by_policy_output.txt>"""
import json,sys
rows=json.load(open(sys.argv[1]))['A']
txt=open(sys.argv[2]).read().split('从未有策略成功的')[1]
solved={}
for line in txt.splitlines():
    p=line.split()
    if p and '__' in p[0]:
        solved[p[0]]=sum(int(x.split('=')[1]) for x in p[1:])
s={'越顶':[0,0],'侧绕':[0,0]}
for r in rows:
    k='越顶' if r['over'] else '侧绕'
    key=r['task'].split('rl_train__')[1]
    s[k][0]+=1; s[k][1]+= key in solved
    print(k, '已解' if key in solved else '未解', round(r['latxy'],1), round(r['dz'],1), key)
print(s)
