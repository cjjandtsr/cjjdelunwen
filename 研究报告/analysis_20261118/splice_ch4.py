import re, shutil, os, sys
U='ux'; C='c4'
doc=open(f'{U}/word/document.xml',encoding='utf-8').read()
new=open(f'{C}/word/document.xml',encoding='utf-8').read()
# 1 新内容 body 子元素
nb=new[new.index('<w:body>')+8:new.rindex('<w:sectPr')]
# 2 样式映射（按名称）
def ids(path):
    s=open(path,encoding='utf-8').read(); return {m.group(1):m.group(2) for m in re.finditer(r'<w:style [^>]*w:styleId="([^"]*)"[^>]*>.*?<w:name w:val="([^"]*)"',s,flags=re.S)}
mine=ids(f'{C}/word/styles.xml'); theirs={v.lower():k for k,v in ids(f'{U}/word/styles.xml').items()}
def mp(m):
    sid=m.group(2); name=mine.get(sid,sid).lower(); return f'{m.group(1)}="{theirs.get(name,sid)}"'
nb=re.sub(r'(w:pStyle w:val|w:tblStyle w:val|w:rStyle w:val)="([^"]*)"',mp,nb)
print('unmapped:',set(re.findall(r'w:(?:pStyle|tblStyle) w:val="([A-Za-z][^"]*)"',nb)))
# 3 图片关系
nrels=open(f'{C}/word/_rels/document.xml.rels',encoding='utf-8').read()
urels_p=f'{U}/word/_rels/document.xml.rels'; urels=open(urels_p,encoding='utf-8').read()
add=''
for rid in set(re.findall(r'r:embed="([^"]*)"',nb)):
    tgt=re.search(r'Id="%s"[^>]*Target="([^"]*)"'%rid,nrels) or re.search(r'Target="([^"]*)"[^>]*Id="%s"'%rid,nrels)
    tgt=tgt.group(1); newname=f'media/v13_{os.path.basename(tgt)}'
    shutil.copy(f'{C}/word/{tgt}',f'{U}/word/{newname}')
    nid=f'rIdV13{rid}'
    add+=f'<Relationship Id="{nid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{newname}"/>'
    nb=nb.replace(f'r:embed="{rid}"',f'r:embed="{nid}"')
urels=urels.replace('</Relationships>',add+'</Relationships>'); open(urels_p,'w',encoding='utf-8').write(urels)
# docPr id 去重
nb=re.sub(r'(<wp:docPr id=")(\d+)',lambda m:m.group(1)+str(9000+int(m.group(2))),nb)
# 4 定位替换范围：用户稿“4 实验与结果分析”标题段 → “参考文献”标题段之前
body_start=doc.index('<w:body>')+8
els=[(m.start(),m.end()) for m in re.finditer(r'<w:(p|tbl)[ >].*?</w:\1>',doc[body_start:],flags=re.S)]
def txt(a,b): return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>',doc[body_start+a:body_start+b]))
i0=next(i for i,(a,b) in enumerate(els) if txt(a,b).strip()=='4 实验与结果分析')
i1=next(i for i,(a,b) in enumerate(els) if txt(a,b).strip()=='参考文献')
a=body_start+els[i0][0]; b=body_start+els[i1][0]
print('replace elements',i0,i1)
doc=doc[:a]+nb+doc[b:]
# 命名空间检查
for ns in set(re.findall(r'<(\w+):',nb)):
    if f'xmlns:{ns}=' not in doc[:3000]: print('missing ns',ns)
open(f'{U}/word/document.xml','w',encoding='utf-8').write(doc)
