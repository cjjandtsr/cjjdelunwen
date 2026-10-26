"""Draw the manuscript's navigation loop and separate training updates.
Original schematic drawn from the documented implementation; no external artwork.
"""
from pathlib import Path
from math import atan2, cos, sin, pi
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib.colors import HexColor
import pypdfium2 as pdfium

OUT=Path(__file__).resolve().parent
d=Drawing(780,390)
ink=HexColor('#233747')
def label(x,y,text,size=10,anchor='middle'):
    d.add(String(x,y,text,fontName='Helvetica',fontSize=size,textAnchor=anchor,fillColor=ink))
def box(x,y,w,h,lines,fill='#edf3f6'):
    d.add(Rect(x,y,w,h,rx=4,ry=4,fillColor=HexColor(fill),strokeColor=HexColor('#7e949e'),strokeWidth=.8))
    for i,t in enumerate(lines):label(x+w/2,y+h/2+(len(lines)-1)*7-i*14,t)
def arrow(points,color='#39586c'):
    for a,b in zip(points[:-1],points[1:]):d.add(Line(*a,*b,strokeColor=HexColor(color),strokeWidth=1))
    a,b=points[-2:];angle=atan2(b[1]-a[1],b[0]-a[0]);v=[b[0],b[1]]
    for q in [angle+pi-.45,angle+pi+.45]:v += [b[0]+6*cos(q),b[1]+6*sin(q)]
    d.add(Polygon(v,fillColor=HexColor(color),strokeColor=None))
label(20,373,'Navigation: repeated observation, generation and execution',12,'start')
box(20,290,130,65,['Local point cloud','+ state history','3 frames'])
box(175,290,120,65,['Point / state','encoding','Condition: 576D'])
box(320,290,145,65,['Conditional diffusion','H16 trajectory','Frozen base + LoRA'])
box(490,290,120,65,['Select H8','Execute H4','0.3 s per segment'])
box(635,290,125,65,['Kinematic','environment','State + geometry'])
for a,b in [(150,175),(295,320),(465,490),(610,635)]:arrow([(a,322),(b,322)])
arrow([(698,290),(698,258),(85,258),(85,290)])
label(360,264,'New observations after executed segments; replan after H4',10)
label(20,226,'Post-training only: frozen encoder / base weights; separate policy and value updates',12,'start')
box(20,137,180,62,['Environment reward','+ critic value estimates'], '#fff3df')
box(245,137,165,62,['GAE advantages','+ value targets'], '#fff3df')
box(510,137,250,62,['PPO surrogate','H8 denoising probability proxy'], '#edf3f6')
arrow([(200,168),(245,168)])
arrow([(410,178),(510,178)]);label(460,185,'Advantages',9)
arrow([(698,290),(775,290),(775,210),(110,210),(110,199)])
arrow([(392,290),(392,240),(632,240),(632,199)]);label(633,246,'Denoising log-probabilities',9)
box(245,35,165,66,['Value regression loss','Update critic'], '#edf3f6')
arrow([(327,137),(327,101)]);label(331,113,'Value targets',9,'start')
box(550,35,170,66,['Policy loss','Update LoRA'], '#edf3f6')
arrow([(635,137),(635,101)])
arrow([(245,68),(220,68),(220,120),(110,120),(110,137)])
label(20,13,'BC initialization: demonstration reconstruction + geometry auxiliary learning. Evaluation uses the navigation loop only.',10,'start')
name='figure_01_method_corrected'
renderPDF.drawToFile(d,str(OUT/(name+'.pdf')))
renderSVG.drawToFile(d,str(OUT/(name+'.svg')))
pdf=pdfium.PdfDocument(str(OUT/(name+'.pdf')))
pdf[0].render(scale=2).to_pil().save(OUT/(name+'.png'));pdf.close()
print('Figure 1: same drawing exported to SVG / PDF / PNG.')
