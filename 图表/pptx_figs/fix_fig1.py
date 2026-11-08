import sys, copy
from pptx import Presentation
from pptx.util import Pt, Emu
from lxml import etree as E
A='http://schemas.openxmlformats.org/drawingml/2006/main'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
src,dst=sys.argv[1],sys.argv[2]
prs=Presentation(src); s=prs.slides[0]
log=[]
def all_shapes(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type==6: yield from all_shapes(sh.shapes)
S={sh.shape_id:sh for sh in all_shapes(s.shapes)}
def runs(sid): return [r for pa in S[sid].text_frame.paragraphs for r in pa.runs]
def settext(sid,i,old,new):
    r=runs(sid)[i]; assert r.text==old,(sid,i,r.text); r.text=new; log.append(f'{sid}: {old!r} -> {new!r}')
# 1 critic input
settext(128,0,'β','e')
# 2 execution wording
settext(322,0,'execute the first 4','execute steps 3–6')
# 3 condition box
rs=runs(444)
settext(444,0,'FiLM(','condition [')
settext(444,3,' ','')
settext(444,6,')',']')
rs[2].font.size=Pt(6); log.append('444: subscript t 8pt -> 6pt')
# 4 full-width parentheses
settext(138,0,'（','('); settext(138,2,'）',')')
settext(141,0,'（','(')
# 5 spacing
settext(153,0,'value loss → update','value loss → update ')
rs=runs(108)
settext(108,2,'· progress · risk · time',' · progress · risk · time')
settext(108,3,'· ',' · ')
for r in rs[3:]:
    r.font.size=Pt(6); r.font.name='Times New Roman'
# 6 lambda L_keep: Times italic, move left of arrow, right aligned
sh=S[151]
for i,r in enumerate(runs(151)):
    r.font.name='Times New Roman'
    rp=r._r.get_or_add_rPr()
    for tag in ('cs',):
        el=rp.find(f'{{{A}}}{tag}')
        if el is not None: el.set('typeface','Times New Roman'); el.attrib.pop('panose',None); el.attrib.pop('charset',None)
    r.font.italic = (i<2)
sh.left=Emu(int(104.6*36000)); sh.width=Emu(int(10.8*36000)); sh.top=Emu(int(82.8*36000))
tf=sh.text_frame; tf.margin_left=tf.margin_right=0
from pptx.enum.text import PP_ALIGN
tf.paragraphs[0].alignment=PP_ALIGN.RIGHT
log.append('151: font -> Times New Roman, moved left of arrow, right-aligned')
# 7 sentence-case subtitles
settext(674,0,'Local Point Cloud','Local point cloud')
settext(675,0,'UAV State','UAV state')
# 8 subscripts < 6 pt -> 6 pt
n=0
for sh in all_shapes(s.shapes):
    if sh.has_text_frame:
        for pa in sh.text_frame.paragraphs:
            for r in pa.runs:
                if r.font.size is not None and r.font.size.pt<6: r.font.size=Pt(6); n+=1
log.append(f'{n} runs <6pt -> 6pt')
# 9 delete unlabeled up-arrow in Relative goal (line 605 + head 606)
for sid in (605,606):
    e=S[sid]._element; e.getparent().remove(e)
log.append('removed 605,606 (unlabeled blue up-arrow in Relative goal)')
# 10 replace raster labels with native text, same frame
def textbox_like(pic, text_runs, size, bold=False, italic=False, widen=1.0, color='000000'):
    xf=pic._element.spPr.find(f'{{{A}}}xfrm')
    off=xf.find(f'{{{A}}}off'); ext=xf.find(f'{{{A}}}ext')
    x,y,cx,cy=int(off.get('x')),int(off.get('y')),int(ext.get('cx')),int(ext.get('cy'))
    ncx=int(cx*widen); x-= (ncx-cx)//2
    nid=max(S)+1+len(log)
    rr=''.join(f'<a:r><a:rPr lang="en-US" sz="{int(sz*100)}" b="{1 if bold else 0}" i="{1 if it else 0}"{(" baseline=%s"%bl) if bl else ""}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Times New Roman"/><a:cs typeface="Times New Roman"/></a:rPr><a:t>{t}</a:t></a:r>' for t,sz,it,bl in text_runs)
    xml=f'''<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{nid}" name="label-{nid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{ncx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="ctr"/>{rr}</a:p></p:txBody></p:sp>'''
    el=E.fromstring(xml)
    pic._element.addnext(el); pic._element.getparent().remove(pic._element)
    log.append(f'pic {pic.shape_id} -> text {"".join(t for t,*_ in text_runs)!r}')
textbox_like(S[351],[('Observation Space',9,False,None)],9,bold=True)
# title must be bold: set b=1
el=[e for e in s.shapes._spTree.iter(f'{{{P}}}sp') if e.find(f'.//{{{A}}}t') is not None and e.find(f'.//{{{A}}}t').text=='Observation Space'][0]
el.find(f'.//{{{A}}}rPr').set('b','1')
textbox_like(S[384],[('τ',6,True,None),('−2',6,False,None)],6,widen=1.6)
textbox_like(S[387],[('τ',6,True,None),('−1',6,False,None)],6,widen=1.6)
textbox_like(S[388],[('τ',6,True,None)],6,widen=1.0)
# 11 add c_t label above concat -> U-Net arrow (top level)
nid=max(S)+100
xml=f'''<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{nid}" name="label-ct"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{int(130.4*36000)}" y="{int(39.6*36000)}"/><a:ext cx="{int(5.0*36000)}" cy="{int(3.2*36000)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="ctr"/>
<a:r><a:rPr lang="en-US" sz="800" b="1" i="1"><a:solidFill><a:srgbClr val="2E4A73"/></a:solidFill><a:latin typeface="Times New Roman"/></a:rPr><a:t>c</a:t></a:r>
<a:r><a:rPr lang="en-US" sz="600" b="1" i="1" baseline="-25000"><a:solidFill><a:srgbClr val="2E4A73"/></a:solidFill><a:latin typeface="Times New Roman"/></a:rPr><a:t>t</a:t></a:r></a:p></p:txBody></p:sp>'''
s.shapes._spTree.append(E.fromstring(xml)); log.append('added c_t label under 3-frame concat')
prs.save(dst)
print('\n'.join(log))
