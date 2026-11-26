# 去掉每个分图顶部的标题行，换成只含分图字母的标签；把图4中的"Stage I only"改为"w/o Stage II"
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
SRC='media/media'; OUT='fig'
BOLD='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
REG='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
def title_end(a):
    dark=(a.min(axis=2)<200).sum(axis=1)
    y=0
    while y<len(dark) and dark[y]==0: y+=1        # 标题前空白
    while y<len(dark) and dark[y]>0: y+=1         # 标题行
    return y
def strip(i,label,newname):
    im=Image.open(f'{SRC}/image{i}.png').convert('RGB'); a=np.asarray(im)
    y=title_end(a); body=im.crop((0,y+6,im.width,im.height))
    band=80 if label else 20
    out=Image.new('RGB',(im.width,body.height+band),'white'); out.paste(body,(0,band))
    if label:
        ImageDraw.Draw(out).text((20,8),label,font=ImageFont.truetype(BOLD,54),fill=(0,0,0))
    out.save(f'{OUT}/{newname}.png',dpi=(600,600)); return out
def replace(img,box,new,align,size,color):
    d=ImageDraw.Draw(img); x0,y0,x1,y1=box
    d.rectangle((x0-4,y0-4,x1+4,y1+8),fill='white')
    f=ImageFont.truetype(REG,size); w=d.textlength(new,font=f)
    x=x1-w if align=='right' else x0
    d.text((x,y1-int(0.22*size)),new,font=f,fill=color,anchor='ls')
plan=[(4,'(a)','fig04a'),(5,'(b)','fig04b'),(6,'(c)','fig04c'),
      (8,'(a)','fig05a'),(10,'(b)','fig05b'),
      (11,'(a)','fig06a'),(12,'(b)','fig06b'),(13,'(c)','fig06c'),
      (7,None,'fig07'),(14,'(a)','fig08a'),(15,'(b)','fig08b'),
      (16,'(a)','fig09a'),(17,'(b)','fig09b'),
      (18,'(a)','fig10a'),(19,'(b)','fig10b'),(20,'(c)','fig10c'),
      (21,'(a)','fig11a'),(22,'(b)','fig11b')]
for i,lab,name in plan:
    im=Image.open(f'{SRC}/image{i}.png').convert('RGB'); y=title_end(np.asarray(im))
    out=strip(i,lab,name)
    if i in (4,5,6):
        # 原图坐标 → 新图坐标：减去标题高度再加标签带
        shift=80-(y+6)
        if i==4: box=(288,363+shift,615,421+shift); align='right'
        elif i==5: box=(288,373+shift,615,431+shift); align='right'
        else: box=(2035,576+shift,2330,629+shift); align='left'
        a=np.asarray(out); px=a[box[1]:box[3],box[0]:box[2]].reshape(-1,3); col=tuple(int(c) for c in px[px.sum(1).argmin()])
        replace(out,box,'w/o Stage II',align,64 if i!=6 else 58,col)
        out.save(f'{OUT}/{name}.png',dpi=(600,600))
    print(name,'title_end',y,out.size)
