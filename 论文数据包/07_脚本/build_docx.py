"""由论文 Markdown 生成 Word 初稿（公式转为 Word 原生公式，图片嵌入，表格三线表）。
运行（论文仓库根目录）：python3 研究报告/analysis_20261108/build_docx.py 论文大稿_v4.md 输出.docx
处理：去掉“工作稿说明”与“图表与数据说明（不进入正文）”；行内 $$x$$ 改为 $x$；\\tag{n} 改为 \\qquad(n)；
图片宽 16 cm、居中；“图n／表n”标题段居中；正文宋体/Times New Roman 五号、1.5 倍行距，标题黑体。"""
import re, subprocess, sys, os, tempfile
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC, OUT = sys.argv[1:3]
txt = open(SRC, encoding='utf-8').read()
if '### 图表与数据说明' in txt:
    a = txt.index('### 图表与数据说明'); b = txt.index('## 参考文献')
    txt = txt[:a].rstrip().rstrip('-').rstrip() + '\n\n' + txt[b:]
lines, out, inblock = txt.split('\n'), [], False
for l in lines:
    if l.startswith('> 工作稿说明'):
        continue
    if l.strip() == '$$':
        inblock = not inblock; out.append(l); continue
    if inblock:
        out.append(re.sub(r'\\tag\{(\d+)\}', r'\\qquad(\1)', l)); continue
    l = re.sub(r'\$\$(.+?)\$\$', lambda m: '$' + m.group(1).strip() + '$', l)
    l = re.sub(r'^(!\[[^\]]*\]\([^)]*\))\s*$', r'\1{width=16cm}', l)
    out.append(l)
md = '\n'.join(out)
md = re.sub(r'\{\\rm\s+([A-Za-z]+)\}', r'\\mathrm{\1}', md)  # texmath 不支持 {\rm X}
os.makedirs('/tmp/docx_build', exist_ok=True)
mdp = '/tmp/docx_build/in.md'; open(mdp, 'w', encoding='utf-8').write(md)

# 参考样式
ref = '/tmp/docx_build/ref.docx'
subprocess.run(['pandoc', '-o', ref, '--print-default-data-file', 'reference.docx'], check=True, stdout=open(ref, 'wb'))
d = Document(ref)
SN = {s.name.lower(): s for s in d.styles}
def setfont(st, size, east='宋体', west='Times New Roman', bold=None):
    st.font.name = west; st.font.size = Pt(size)
    if bold is not None: st.font.bold = bold
    st.font.color.rgb = None
    rpr = st.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for k in ('w:ascii', 'w:hAnsi', 'w:cs'): rf.set(qn(k), west)
    rf.set(qn('w:eastAsia'), east)
    for k in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rf.get(qn(k)) is not None: del rf.attrib[qn(k)]
for name in ['Normal', 'Body Text', 'First Paragraph', 'Compact']:
    if name.lower() in SN:
        st = SN[name.lower()]; setfont(st, 10.5)
        pf = st.paragraph_format; pf.line_spacing = 1.5; pf.space_before = Pt(0); pf.space_after = Pt(0)
        if name in ('Body Text', 'First Paragraph'): pf.first_line_indent = Pt(21)
for name, size in [('Title', 16), ('Heading 1', 14), ('Heading 2', 12), ('Heading 3', 10.5), ('Heading 4', 10.5)]:
    st = SN[name.lower()]; setfont(st, size, east='黑体', west='Times New Roman', bold=True)
    pf = st.paragraph_format; pf.space_before = Pt(12 if name != 'Heading 4' else 6); pf.space_after = Pt(6); pf.keep_with_next = True
    if name == 'Title': pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
d.save(ref)

tmp = '/tmp/docx_build/raw.docx'
subprocess.run(['pandoc', mdp, '-f', 'markdown-implicit_figures+tex_math_dollars+pipe_tables', '-t', 'docx',
                '--reference-doc', ref, '--resource-path', os.getcwd(), '-o', tmp], check=True)

doc = Document(tmp)
for sec in doc.sections:
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.5); sec.top_margin = sec.bottom_margin = Cm(2.5)
cap = re.compile(r'^(图|表|算法)\s*S?\d+')
for p in doc.paragraphs:
    t = p.text.strip()
    if p._p.xpath('.//pic:pic'):
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.keep_with_next = True
    elif cap.match(t) and len(t) < 400 and any(r.bold for r in p.runs[:1]):
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if t.startswith('表') or t.startswith('算法') or len(t) < 40 else WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Pt(0)
        for r in p.runs: r.font.size = Pt(9)
        if t.startswith('表') or t.startswith('算法'): p.paragraph_format.keep_with_next = True
    elif t.startswith('表注'):
        p.paragraph_format.first_line_indent = Pt(0)
        for r in p.runs: r.font.size = Pt(9)
    elif re.match(r'^\[\d+\]', t):
        p.paragraph_format.first_line_indent = Pt(0); p.paragraph_format.line_spacing = 1.15
        for r in p.runs: r.font.size = Pt(9)

def border(el, tag, sz):
    b = OxmlElement(f'w:{tag}'); b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), str(sz)); b.set(qn('w:space'), '0'); b.set(qn('w:color'), '000000'); el.append(b)
for tb in doc.tables:
    tbl = tb._tbl; tblPr = tbl.tblPr
    for old in tblPr.findall(qn('w:tblBorders')): tblPr.remove(old)
    bs = OxmlElement('w:tblBorders'); border(bs, 'top', 12); border(bs, 'bottom', 12); tblPr.append(bs)
    jc = OxmlElement('w:jc'); jc.set(qn('w:val'), 'center'); tblPr.append(jc)
    for c in tb.rows[0].cells:
        tcPr = c._tc.get_or_add_tcPr(); tb_ = OxmlElement('w:tcBorders'); border(tb_, 'bottom', 6); tcPr.append(tb_)
    for row in tb.rows:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.first_line_indent = Pt(0); p.paragraph_format.line_spacing = 1.0
                for r in p.runs: r.font.size = Pt(9)
# 列宽：按各列最长文字估算（中文按 2 计），总宽 16 cm，首列至少 18%
def tlen(t): return sum(2 if ord(ch) > 0x2E80 else 1 for ch in t)
for tb in doc.tables:
    ncol = len(tb.columns); L = [max(6, max(min(tlen(r.cells[j].text), 40) for r in tb.rows)) for j in range(ncol)]
    tot = sum(L); W = [max(l / tot, 0.18 if j == 0 else 0.06) for j, l in enumerate(L)]; sw = sum(W)
    tb.autofit = False
    grid = tb._tbl.tblGrid
    for j, gc in enumerate(grid.findall(qn('w:gridCol'))): gc.set(qn('w:w'), str(int(16 / 2.54 * 1440 * W[j] / sw)))
    for r in tb.rows:
        for j, c in enumerate(r.cells): c.width = Cm(16 * W[j] / sw)
    tblW = tb._tbl.tblPr.find(qn('w:tblW'))
    if tblW is not None: tblW.set(qn('w:type'), 'dxa'); tblW.set(qn('w:w'), str(int(16 / 2.54 * 1440)))
doc.save(OUT); print('saved', OUT)
