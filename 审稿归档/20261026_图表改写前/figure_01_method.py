"""Compose the actual UAV inputs, a sourced U-Net topology, and DPPO's two MDPs.

No new environment interaction, policy evaluation or training is performed.
"""
from pathlib import Path
import json
import math
import shutil
import numpy as np
from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Circle, Line, String
from reportlab.lib import colors
import pypdfium2 as pdfium
import figure_01_reference_composite as c
from pypdf import PdfWriter

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
BANK=PROJECT/'wsl_snapshot/diagnostics/routea_bc_a0_r1_paired_dev_20261010_py38fix_run02/bank'
KEY='1724b2984332060ba3316455'
OBS=BANK/'initial'/(KEY+'.npz')
WORLD=BANK/'worlds/routeA_rl_v1__dense_recovery__rl_train__bottleneck_corridor__000026.world.obstacles.json'
z=np.load(OBS,allow_pickle=False)
PC=z['point_cloud'][-3:]
STATE=z['agent_pos'][-3:]
PLOT=ROOT/'参考图核对'


def asset(name,d):
    pdf=PLOT/(name+'.pdf');png=PLOT/(name+'.png')
    renderPDF.drawToFile(d,str(pdf))
    p=pdfium.PdfDocument(str(pdf));p[0].render(scale=2).to_pil().save(png)
    return png


def cloud_asset(points,name):
    d=Drawing(420,260)
    # A fixed orthographic display of the saved body-frame XYZ points.
    # Color denotes body-frame height only; no semantic labels are inferred.
    rot=np.array([[.74,-.67,0],[.25,.28,.93],[0,0,1]])
    projected=points@rot.T
    lo=projected[:,:2].min(0);hi=projected[:,:2].max(0)
    xy=(projected[:,:2]-lo)/(hi-lo)*np.array([345,187])+[38,32]
    for i in np.argsort(points[:,2]):
        a=float(np.clip((points[i,2]+1.4)/4,0,1))
        color=colors.Color(.18+.55*a,.48+.22*a,.69-.30*a)
        d.add(Circle(float(xy[i,0]),float(xy[i,1]),.85,fillColor=color,strokeColor=None))
    for endpoint,label in [((100,20),'x_b'),((28,76),'y_b'),((26,124),'z_b')]:
        d.add(Line(26,20,*endpoint,strokeColor=colors.HexColor('#586c7a'),strokeWidth=1.2))
        d.add(String(endpoint[0]+3,endpoint[1]+1,label,fontSize=12))
    return asset(name,d)


clouds=[cloud_asset(p,'project_cloud_'+str(i)) for i,p in enumerate(PC)]
world=json.loads(WORLD.read_text(encoding='utf-8'))
scene=Drawing(430,270)
def wp(x,y):return (float(x)+11)*10+40,(float(y)+14)*7+25
for ob in world['obstacles']:
    x,y=wp(ob['x'],ob['y'])
    scene.add(Circle(x,y,float(ob.get('radius',.3))*9,
                     fillColor=colors.HexColor('#a2b7c6'),strokeColor=colors.HexColor('#65839a')))
bank=json.loads((BANK/'bank.json').read_text(encoding='utf-8'))
task=next(t['payload'] for t in bank['tasks'] if '000026__dev20261009__cfg01' in t['task_id'])
for p,label,col in [(task['start_pos'],'Start',colors.HexColor('#247b8d')),
                    (task['goal_pos'],'Goal',colors.HexColor('#c26c32'))]:
    x,y=wp(p[0],p[1]);scene.add(Circle(x,y,5,fillColor=col,strokeColor=None))
    scene.add(String(x+7,y,label,fontSize=15,fillColor=col))
scene.add(String(40,253,'Project obstacle layout (top view)',fontSize=17))
scene_asset=asset('project_world',scene)

# Import the externally sourced U-Net diagram and adapt the three-level core.
# Original 2D image / mask labels and pooling nomenclature are removed.
source=PILImage.open(c.REF/'Fig1_UNet_Yazdani_original.png').convert('RGB')
net=source.crop((110,0,590,300)).resize((960,600),PILImage.Resampling.LANCZOS)
draw=ImageDraw.Draw(net)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
def relabel(cx,cy,w,h,txt):
    x=(cx-110)*2;y=cy*2
    draw.rectangle((x-w,y-h,x+w,y+h),fill='white')
    draw.rectangle((x-40,y-28,x+40,y+28),fill='#f2f6fb',outline='#48627d',width=2)
    draw.text((x,y),txt,fill='#20364c',font=font,anchor='mm',align='center')
for cx,cy,txt in [(140,30,'Res1D'),(182,150,'Res1D'),(222,270,'Mid'),
                   (560,30,'Output'),(500,150,'Res1D'),(443,270,'Res1D'),
                   (140,94,'Down'),(182,214,'Down'),(500,94,'Up'),(443,214,'Up')]:
    relabel(cx,cy,50,45,txt)
# Restore the vertical upsampling arrows interrupted by label replacement.
for cx,a,b in [(780,272,216),(666,512,456)]:
    draw.rectangle((cx-17,b+1,cx+17,a-1),fill='white')
    draw.line((cx,a,cx,b),fill='#334e68',width=2)
    draw.polygon([(cx,b),(cx-5,b+8),(cx+5,b+8)],fill='#334e68')
# Crop truncates the original fourth level; close the two dangling stubs.
draw.rectangle((200,583,250,599),fill='white')
draw.rectangle((650,583,700,599),fill='white')
net.save(PLOT/'unet_temporal_adapted.png')

# Keep the approved four-region organization, with more room for two-layer DPPO.
c.H=1150;c.D=Drawing(1900,1150)
text,lines,frame,arrow,block,picture,module=c.text,c.lines,c.frame,c.arrow,c.block,c.picture,c.module
text(950,-4,'Point-cloud-conditioned UAV trajectory policy with DPPO post-training',29,True)
frame(5,90,378,532);text(194,132,'Observation Space',31,True)
picture(clouds[-1],27,175,157,126)
lines(103,330,['Local XYZ','point cloud'],25)

# Relative goal in body coordinates, using the saved actual state vector.
gb=STATE[-1,3:6];ang=math.atan2(float(gb[1]),float(gb[0]))
arrow([(244,277),(244+98*math.cos(ang),277-98*math.sin(ang))],c.BLUE,5)
text(270,197,'g_b',34);text(285,239,'d = %.2f m'%float(STATE[-1,6]),19)
lines(285,330,['Relative goal','and distance'],25)

# Own-state components are drawn as coordinates, not a vehicle photograph.
for end,label in [((121,433),'x'),((26,410),'y'),((65,376),'z')]:
    arrow([(65,460),end],colors.HexColor('#617b94'),3)
    text(end[0]+9,end[1],label,17)
yaw=math.atan2(float(STATE[-1,7]),float(STATE[-1,8]))
arrow([(91,430),(91+48*math.cos(yaw),430-48*math.sin(yaw))],colors.HexColor('#cb8745'),5)
text(110,490,'p, sin(yaw), cos(yaw)',17)
lines(105,550,['Position and','heading'],25)
for i in (2,1,0):picture(clouds[i],220+i*10,386+i*12,128,90)
text(284,502,'o(tau-2), o(tau-1), o(tau)',15)
lines(284,550,['Three-frame','observations'],25)

picture(scene_asset,430,5,283,183)
text(575,220,'Environment',30)
arrow([(558,276),(558,239)]);arrow([(590,239),(590,276)])
c.svg_icon(c.REF/'Fig1_asset_quadcopter.svg',495,302,155,118)
text(575,460,'Local Navigation',31,True)
text(575,507,'Observe - plan - execute',27)
arrow([(398,342),(436,342)]);arrow([(436,377),(398,377)])
arrow([(727,342),(765,342)]);arrow([(765,377),(727,377)])

frame(785,90,1110,532);text(1335,132,'Conditional Diffusion Policy',31,True)
lines(874,225,['9-D state','history'],25)
module(973,174,171,121,['State MLP','64-D'],c.GREEN,26)
lines(874,430,['XYZ point','cloud history'],25)
module(973,377,171,121,['PointNet','128-D'],c.TEAL,26)
arrow([(941,236),(968,236)]);arrow([(941,439),(968,439)])
block(1180,253,156,163,['Feature','concatenation','+ time order','c(t): 576-D'],colors.HexColor('#dbefea'),23)
arrow([(1149,237),(1165,237),(1165,291),(1178,291)],c.BLUE,5)
arrow([(1149,439),(1165,439),(1165,381),(1178,381)],c.BLUE,5)

frame(1367,263,490,291,18,colors.white,c.EDGE)
picture(PLOT/'unet_temporal_adapted.png',1377,292,470,239)
text(1612,286,'Conditional 1D U-Net',24,True)
text(1612,545,'FiLM: concat[c(t), emb(k)]',20)
arrow([(1338,335),(1364,335)],c.BLUE,5)
block(1393,166,190,63,['Noisy trajectory Z(k)'],colors.HexColor('#e6edf6'),21)
block(1620,166,214,63,['Diffusion step k'],colors.HexColor('#fff0dd'),23)
arrow([(1488,230),(1488,260)],c.BLUE,5)
arrow([(1727,230),(1727,260)],c.BLUE,5)
text(1865,249,'Time embedding',17,anchor='end')
text(1614,582,'x0 prediction -> DDIM transition -> repeat',21)
arrow([(1855,545),(1874,545),(1874,683)],c.BLUE,5)

# DPPO: sampled denoising transitions nested inside environment interaction.
frame(10,646,1589,397);text(794,682,'DPPO: Environment MDP + Denoising MDP',31,True)
text(445,719,'Environment step t',23,True)
text(940,719,'Environment step t+1',23,True)
for x,t in [(52,'t'),(647,'t+1')]:
    block(x,748,127,66,['c('+t+')','3-frame'],colors.HexColor('#e2edf8'),22)
    block(x+166,748,167,66,['Z('+t+', K)','N(0,I)'],colors.HexColor('#e2edf8'),22)
    block(x+166,842,167,66,['Z('+t+', j)'],colors.HexColor('#c9daf6'),25)
    block(x+166,936,167,66,['Z('+t+', 0)'],colors.HexColor('#ecc5b4'),25)
    cond_color=colors.HexColor('#418d86')
    c.D.add(Line(x+129,c.y(781),x+145,c.y(781),strokeColor=cond_color,strokeWidth=3))
    c.D.add(Line(x+145,c.y(781),x+145,c.y(923),strokeColor=cond_color,strokeWidth=3))
    arrow([(x+145,829),(x+249,829)],cond_color,3,True)
    arrow([(x+145,923),(x+249,923)],cond_color,3,True)
    text(x+63,853,'Condition',17,color=cond_color)
    arrow([(x+249,817),(x+249,838)],c.BLUE,5)
    arrow([(x+249,911),(x+249,932)],c.BLUE,5)
    text(x+370,809,'...',26)
    text(x+380,859,'Gaussian',19)
    text(x+380,884,'transitions',19)
    text(x+380,952,'Execute H4',19)
arrow([(389,969),(581,969),(581,781),(642,781)],c.BLUE,5)
text(488,938,'r(t)',26)
text(304,1024,'Inner process: iterative trajectory denoising',20)
arrow([(975,969),(1020,969),(1020,781),(1050,781)],c.BLUE,5)

# Actual update path: rollout quantities, environment advantages and per-step ratio.
block(1054,743,221,77,['Environment reward','Critic / GAE / discount'],colors.HexColor('#fff0cf'),20)
block(1315,743,244,77,['Denoising transition','log-probabilities'],colors.HexColor('#e4edfa'),23)
block(1130,867,350,71,['Clipped PPO surrogate objective','Denoising-step ratio'],colors.HexColor('#e4efd5'),22)
arrow([(982,875),(1009,875),(1009,833),(1437,833),(1437,823)],colors.HexColor('#6a9c98'),3,True)
arrow([(1164,822),(1164,864)],c.BLUE,5)
arrow([(1437,822),(1437,864)],c.BLUE,5)
block(1055,971,217,56,['Update LoRA'],colors.HexColor('#f7d4ad'),23)
block(1314,971,244,56,['Update critic'],colors.HexColor('#f7d4ad'),23)
arrow([(1200,940),(1200,966)],c.BLUE,4)
arrow([(1277,760),(1290,760),(1290,727),(1578,727),(1578,950),(1437,950),(1437,967)],colors.HexColor('#bb874f'),4)
text(1510,943,'Value loss',17)
text(1294,1038,'Encoder and pretrained backbone remain frozen',18)

lines(1750,700,['Receding-horizon','execution'],25)
for i in range(16):
    shade=colors.HexColor('#d8d8d8') if i<2 else (c.TEAL if i<6 else (colors.HexColor('#b9cce9') if i<10 else colors.white))
    frame(1632+(i%8)*29,773+(i//8)*49,23,32,0,shade,c.EDGE)
lines(1751,901,['16 predicted elements','2 for alignment','Plan 8 / execute 4'],22,pitch=28)
arrow([(1750,966),(1623,966),(1623,632),(575,632),(575,621)],c.BLUE,4)
text(1751,1001,'Update observations',20)
text(1751,1029,'and replan',20)
text(950,1081,'U-Net graphic adapted from Yazdani (CC BY-SA 4.0). Inputs/layout: project records. DPPO concept: Ren et al. (2024).',20,color=colors.HexColor('#555555'))

c.export('figure_01_composite_candidate')
for ext in ['svg','pdf','png']:
    shutil.copyfile(ROOT/('figure_01_composite_candidate.'+ext),ROOT/('figure_01_method.'+ext))
writer=PdfWriter()
for name in ['enhancing_fig1_layout_replica','figure_01_composite_candidate']:
    writer.append(str(ROOT/(name+'.pdf')))
with (ROOT/'fig1_reference_and_candidate.pdf').open('wb') as f:writer.write(f)
print('Rendered project inputs, sourced temporal U-Net schematic, and two-layer DPPO')
