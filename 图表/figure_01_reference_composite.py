"""Reconstruct the supplied Fig. 1 layout and compose a separate UAV candidate.

Raster illustrations are imported, not synthesized. Vector text, modules and
arrows remain editable. Original-paper crops are used only in the reference.
"""
from pathlib import Path
import base64
import math
import re
import xml.etree.ElementTree as ET
from PIL import Image as PILImage
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium
from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Drawing, Rect, String, Polygon, Line, Image, Path as RPath, Group
from reportlab.lib import colors

ROOT=Path(__file__).resolve().parent
REF=ROOT.parent/'被参考'
TMP=ROOT/'参考图核对'
TMP.mkdir(exist_ok=True)
ORIGINAL=PdfReader(str(REF/'Liu_2026_GRPO-MDP_Alexandria_Engineering_Journal.pdf')).pages[2].images[0].image
ORIGINAL.save(TMP/'enhancing_fig1_original.png')
GREY=colors.HexColor('#f1f1f1')
EDGE=colors.HexColor('#929292')
BLUE=colors.HexColor('#91b1e3')
INK=colors.HexColor('#171717')
GOLD=colors.HexColor('#82702b')
GREEN=colors.HexColor('#b9d78e')
TEAL=colors.HexColor('#55c6c3')
ORANGE=colors.HexColor('#efb783')
H=1040
OFFSET=40
D=None


def y(top):return H-OFFSET-top


def text(x,top,value,size=29,bold=False,anchor='middle',color=INK):
    D.add(String(x,y(top),value,fontName='Times-Bold' if bold else 'Times-Roman',fontSize=size,textAnchor=anchor,fillColor=color))


def frame(x,top,w,h,r=56,fill=GREY,stroke=EDGE):
    D.add(Rect(x,y(top+h),w,h,rx=r,ry=r,fillColor=fill,strokeColor=stroke,strokeWidth=2))


def lines(x,top,items,size=28,bold=False,pitch=30):
    for i,s in enumerate(items):text(x,top+i*pitch,s,size,bold)


def arrow(points,color=BLUE,width=9,dashed=False):
    pts=[(x,y(v)) for x,v in points]
    for a,b in zip(pts[:-1],pts[1:]):
        ln=Line(*a,*b,strokeColor=color,strokeWidth=width)
        if dashed:ln.strokeDashArray=[5,4]
        D.add(ln)
    (x0,y0),(x1,y1)=pts[-2:]
    z=math.hypot(x1-x0,y1-y0);u,v=(x1-x0)/z,(y1-y0)/z
    D.add(Polygon([x1,y1,x1-17*u-10*v,y1-17*v+10*u,x1-17*u+10*v,y1-17*v-10*u],fillColor=color,strokeColor=None))


def picture(p,x,top,w,h,crop=None):
    im=PILImage.open(p) if isinstance(p,(str,Path)) else p
    if crop:im=im.crop(crop)
    # Preserve source proportions; cropping is explicit, never a new scene render.
    im=im.copy();im.thumbnail((int(w*2),int(h*2)),PILImage.Resampling.LANCZOS)
    ratio=min(w/im.width,h/im.height);iw,ih=im.width*ratio,im.height*ratio
    name=TMP/('asset_'+str(picture.counter)+'.png');picture.counter+=1
    im.save(name)
    D.add(Image(x+(w-iw)/2,y(top+(h+ih)/2),iw,ih,str(name)))
picture.counter=0


def original_crop(name,rect):
    p=TMP/(name+'.png');ORIGINAL.crop(rect).save(p);return p


def module(x,top,w,h,labels,fill,fontsize=28):
    # Tapered network block, following the source figure's visual grammar.
    D.add(Polygon([x,y(top),x+w,y(top+35),x+w,y(top+h-35),x,y(top+h)],fillColor=fill,strokeColor=colors.HexColor('#70ad71'),strokeWidth=2))
    lines(x+w/2,top+h/2-(len(labels)-1)*15+8,labels,fontsize)


def block(x,top,w,h,labels,fill=colors.white,size=28):
    frame(x,top,w,h,14,fill,GOLD)
    lines(x+w/2,top+h/2-(len(labels)-1)*15+9,labels,size)


def unet(x,top,w=265):
    for i,hh in enumerate([122,114,103,94,94,103,114,122]):
        xx=x+i*34
        frame(xx,top+(122-hh)/2,25,hh,0,colors.HexColor('#8a9fbe'),colors.HexColor('#b8c8dd'))
    text(x+w/2,top-21,'Denoising U-Net',28)
    for i in range(3):frame(x-65+i*21,top+142,15,45,0,ORANGE,colors.HexColor('#a26e3f'))
    for i in range(8):arrow([(x-4,top+164),(x+i*34+12,top+164),(x+i*34+12,top+126)],INK,2,True)
    text(x+w/2-2,top+213,'FiLM conditioning',27)


def svg_icon(path,x,top,w,h):
    # Import the downloaded SVG path as vector geometry (absolute M/L/C/Z).
    xml=ET.parse(path).getroot();g=Group()
    for node in xml.iter():
        if not node.tag.endswith('path'):continue
        tokens=re.findall(r'[MLCZmlcz]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',node.attrib['d'])
        p=RPath(fillColor=colors.HexColor('#214c61'),strokeColor=None)
        i=0;cmd=None
        while i<len(tokens):
            if tokens[i] in ('M','L','C','Z'):
                cmd=tokens[i];i+=1
            if cmd=='Z':p.closePath();cmd=None;continue
            count=6 if cmd=='C' else 2
            vals=list(map(float,tokens[i:i+count]));i+=count
            if cmd=='M':p.moveTo(*vals);cmd='L'
            elif cmd=='L':p.lineTo(*vals)
            elif cmd=='C':p.curveTo(*vals)
            else:raise ValueError('Unsupported asset path')
        g.add(p)
    g.scale(w/15,-h/15);g.translate(x*15/w,-(y(top))*15/h)
    D.add(g)


def export(name):
    svg=ROOT/(name+'.svg');pdf=ROOT/(name+'.pdf')
    renderSVG.drawToFile(D,str(svg))
    # Make the SVG self-contained so it can be moved into an illustration editor.
    content=svg.read_text(encoding='utf-8')
    def embed(m):
        source=Path(m.group(2))
        if source.exists():
            return m.group(1)+'data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode()+m.group(3)
        return m.group(0)
    content=re.sub(r'((?:xlink:)?href=")([^"]+)(")',embed,content)
    svg.write_text(content,encoding='utf-8')
    renderPDF.drawToFile(D,str(pdf))
    doc=pdfium.PdfDocument(str(pdf));doc[0].render(scale=1.4).to_pil().save(ROOT/(name+'.png'))


ASSETS={
    'state':original_crop('ref_state',(27,174,165,300)),
    'goal':original_crop('ref_goal',(221,181,345,300)),
    'pc':original_crop('ref_pointcloud',(39,386,166,507)),
    'history':original_crop('ref_history',(213,387,345,507)),
    'env':original_crop('ref_environment',(428,0,715,182)),
    'drone':original_crop('ref_drone',(451,302,703,420)),
    'fusion':original_crop('ref_fusion',(1333,167,1455,287)),
    'noise':original_crop('ref_noise',(1467,167,1586,289)),
    'noise_feature':original_crop('ref_noise_feature',(1399,402,1517,524)),
    'action':original_crop('ref_action',(1662,171,1799,288)),
}


def compose(replica):
    global D
    D=Drawing(1900,H)
    text(950,-4,'Reference reconstruction - Liu et al., Fig. 1 (p. 35)' if replica else 'UAV policy architecture - image-composite candidate',26,bold=True)
    frame(5,90,378,532);text(194,133,'State Space' if replica else 'Observation Space',31,True)
    picture(ASSETS['state'] if replica else REF/'Fig1_asset_lidar_street.png',29,176,138,120)
    if replica:picture(ASSETS['goal'],220,181,124,120)
    else:
        text(284,229,'g - p',36);arrow([(245,270),(324,198)],BLUE,5)
    lines(97,333,['Ontology','State'] if replica else ['Local point','cloud'],27)
    lines(283,333,['Relative','Target'] if replica else ['Relative','goal'],27)
    if replica:picture(ASSETS['pc'],40,388,126,120)
    else:
        for offset in (16,8,0):picture(REF/'Fig1_asset_lidar_street.png',40+offset,388+offset,110,91)
    if replica:picture(ASSETS['history'],215,388,130,120)
    else:svg_icon(REF/'Fig1_asset_quadcopter.svg',239,400,90,90)
    lines(99,546,['Obstacle','Point Cloud'] if replica else ['Three-frame','history'],26)
    lines(283,546,['Historical','Trajectory'] if replica else ['Position /','heading'],26)
    if replica:picture(ASSETS['env'],430,0,283,183)
    else:picture(REF/'Fig1_asset_terrain_perspective.jpg',431,12,281,167)
    text(575,222,'Environment',30)
    arrow([(558,277),(558,240)]);arrow([(590,240),(590,277)])
    if replica:picture(ASSETS['drone'],452,303,250,118)
    else:svg_icon(REF/'Fig1_asset_quadcopter.svg',495,302,155,118)
    text(575,460,'MDP Modeling' if replica else 'Local Navigation',31,True)
    text(575,508,'M = (S, A, P, r, gamma)' if replica else 'Observe - plan - execute',27)
    arrow([(398,342),(436,342)]);arrow([(436,377),(398,377)])
    arrow([(727,342),(765,342)]);arrow([(765,377),(727,377)])
    arrow([(558,597),(558,559)]);arrow([(591,559),(591,597)])
    frame(785,90,1110,532);text(1335,130,'Action Space' if replica else 'Point-cloud-conditioned Diffusion Policy',31,True)
    for yy,ll in [(190,['Ontology','State'] if replica else ['UAV','state']),
                  (288,['Historical','Trajectory'] if replica else ['Relative','goal']),
                  (390,['Relative','Target'] if replica else ['State','history'])]:
        lines(877,yy,ll,27);arrow([(947,yy+8),(980,yy+8)])
    module(984,138,176,272,['Transformer','Encoder'] if replica else ['State','MLP'],GREEN)
    lines(878,493,['Point','Cloud'],28);arrow([(948,488),(980,488)])
    module(984,419,176,132,['PointNet++'] if replica else ['PointNet'],TEAL,29)
    frame(1215,168,64,365,15,colors.HexColor('#2abcaa'),colors.HexColor('#7acda5'))
    # Rotated vertical labels make the fusion operator a single visual element.
    gg=Group();gg.add(String(0,0,'Cross Attention' if replica else 'Feature + temporal concat.',fontName='Times-Roman',fontSize=30,fillColor=INK))
    gg.transform=(0,1,-1,0,1256,y(495));D.add(gg)
    for yy in [202,284,351,488]:arrow([(1167,yy),(1205,yy)])
    arrow([(1289,202),(1325,202)])
    if replica:
        picture(ASSETS['fusion'],1334,168,120,118)
        picture(ASSETS['noise'],1470,168,116,118)
        picture(ASSETS['noise_feature'],1400,404,119,118)
    else:
        for i in range(7):frame(1336+i*16,178,12,97,1,colors.HexColor(['#537cad','#6e99c4','#8ab4d2'][i%3]),colors.white)
        block(1469,173,119,108,['N(0,I)'],colors.HexColor('#dddfe3'),25)
        block(1372,413,145,106,['Condition','+ time'],colors.HexColor('#e2e9f6'),25)
    lines(1394,319,['Fusion','Feature'] if replica else ['Condition','features'],27)
    lines(1529,319,['Random','Noise'],27)
    arrow([(1415,360),(1415,397)])
    if replica:arrow([(1500,360),(1500,397)])
    else:arrow([(1588,225),(1592,225),(1592,410),(1598,410)],BLUE,5)
    if replica:picture(ASSETS['action'],1664,171,137,118)
    else:
        for i in range(6):frame(1656+i*21,183+(i%2)*10,16,85,0,colors.HexColor('#a1b7d4'),EDGE)
    text(1731,320,'Action' if replica else 'Trajectory',28)
    arrow([(1725,358),(1725,324)] if replica else [(1848,358),(1848,324)])
    unet(1598,405)
    arrow([(1538,468),(1584,468)])
    if not replica:text(1725,355,'DDIM sampling',22)
    # Bottom strip retains the original compact, grouped visual organization.
    frame(10,635,1589,321);text(796,671,'GPRO' if replica else 'DPPO Post-training',31,True)
    block(33,768,145,90,['Policy','Model'] if replica else ['BC +','LoRA'],colors.HexColor('#e0e8f8'),29)
    arrow([(184,810),(221,810)])
    for yy,ss in [(699,'1'),(773,'2'),(862,'n')]:
        block(232,yy,239,65,['Observation '+ss] if replica else ['Transition '+ss],size=28)
    text(352,852,'...',33)
    block(534,715,180,90,['Reference','Model'] if replica else ['Task','Reward'],colors.HexColor('#fff2cb'),29)
    block(534,819,180,90,['Reward','Model'] if replica else ['Value','Network'],colors.HexColor('#fff2cb'),29)
    arrow([(489,760),(529,760)]);arrow([(489,865),(529,865)])
    for yy,ss in [(699,'1'),(773,'2'),(862,'n')]:
        block(777,yy,202,65,['Reward '+ss] if replica else ['GAE '+ss],size=27)
    text(878,852,'...',33);arrow([(728,865),(770,865)])
    if not replica:arrow([(713,760),(744,760),(744,724),(774,724)],BLUE,6)
    arrow([(990,803),(1032,803)])
    block(1046,761,207,89,['Group','Computation'] if replica else ['PPO','Optimization'],colors.HexColor('#e6efd3'),29)
    arrow([(1265,803),(1302,803)])
    for yy,ss in [(699,'1'),(773,'2'),(862,'n')]:
        block(1315,yy,239,65,['Action '+ss] if replica else ['LoRA / value' if ss=='1' else ('parameter update' if ss=='2' else 'next rollout')],size=27)
    text(1435,852,'...',33)
    if replica:
        picture(ASSETS['action'],1687,696,143,140)
        lines(1757,879,['Trajectory','Relabeling'],28)
        arrow([(1665,783),(1628,783)])
    else:
        text(1740,731,'Receding-horizon',27)
        text(1740,770,'execution',27)
        for i in range(8):frame(1638+i*25,803,21,33,0,TEAL if i<4 else colors.HexColor('#d4deee'),EDGE)
        lines(1740,880,['Plan 8 / execute 4','Reobserve and replan'],24)
        arrow([(1650,935),(1618,935),(1618,630),(575,630),(575,618)],BLUE,4)
    footer=('Reconstruction of supplied artwork for visual study; source: Liu et al., AEJ 140 (2026), Fig. 1.' if replica else
            'Illustrative assets: Daniel L. Lu (CC BY 4.0); Kbh3rd (CC BY-SA 2.0); Health Icons (CC0). Candidate artwork: CC BY-SA 4.0.')
    text(950,986,footer,20,color=colors.HexColor('#555555'))
    export('enhancing_fig1_layout_replica' if replica else 'figure_01_composite_candidate')


if __name__ == '__main__':
    compose(True)
    # The current project candidate is produced by figure_01_method.py.
    writer=PdfWriter()
    for name in ['enhancing_fig1_layout_replica','figure_01_composite_candidate']:
        writer.append(str(ROOT/(name+'.pdf')))
    with (ROOT/'fig1_reference_and_candidate.pdf').open('wb') as f:writer.write(f)
    print('Rendered reference reconstruction; reused the existing project candidate')
