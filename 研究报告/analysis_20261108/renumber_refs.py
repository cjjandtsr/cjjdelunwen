"""按正文首次引用、继以补充材料的顺序重排参考文献编号（就地改写两份稿件）。
运行：python3 -I renumber_refs.py 论文大稿_v3.md 补充材料.md"""
import re, sys
P, S = sys.argv[1:3]
d = open(P).read(); sp = open(S).read()
k = d.index('## 参考文献'); body, refs = d[:k], d[k:]
CIT = re.compile(r'\[(\d+(?:[,，]\d+)*)\]')
order = []
for txt in (body, sp):
    for m in CIT.finditer(txt):
        for n in re.split('[,，]', m.group(1)):
            if int(n) not in order: order.append(int(n))
entries = dict((int(m.group(1)), m.group(0)) for m in re.finditer(r'^\[(\d+)\] .*$', refs, re.M))
unused = sorted(set(entries) - set(order)); assert not unused, f'未引用: {unused}'
missing = set(order) - set(entries); assert not missing, missing
new = {o: i + 1 for i, o in enumerate(order)}
sub = lambda t: CIT.sub(lambda m: '[' + ','.join(str(new[int(n)]) for n in re.split('[,，]', m.group(1))) + ']', t)
head = refs[:refs.index('[', refs.index('\n'))]
lst = '\n\n'.join(re.sub(r'^\[\d+\]', f'[{new[o]}]', entries[o]) for o in order)
tail_i = refs.index(entries[max(entries, key=lambda o: refs.index(entries[o]))]) + len(entries[max(entries, key=lambda o: refs.index(entries[o]))])
open(P, 'w').write(sub(body) + head + lst + refs[tail_i:])
open(S, 'w').write(sub(sp))
print('旧→新', {o: n for o, n in new.items() if o != n})
