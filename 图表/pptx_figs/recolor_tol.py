"""Recolour Figs. 1-4 (slides 1-5) to Paul Tol's *light* colour scheme (Tol 2021, SRON/EPS/TN/09-002),
used as tints for fills and as given for borders/marks:
  light blue  #77AADD  policy / execution (frozen parts carry the lock)
  light yellow #EEDD88 condition and FiLM modulation
  orange      #EE8866  LoRA, trainable parameters, post-training-only signals
  pink        #FFAABB  risk / collision danger
  light cyan  #99DDFF  observations (inputs)
  pale grey   #DDDDDD  steps aligned with history
Role-specific recolouring is decided per shape; remaining colours follow the family maps."""
import sys, re, zipfile
from lxml import etree

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"

BLUE = {"F5F8FC": "F2F7FC", "F7F9FC": "F2F7FC", "F4F7FB": "F2F7FC", "F2F6FB": "F2F7FC",
        "EAF0F8": "E3EEF8", "E3EBF6": "E3EEF8", "E6EDF7": "E3EEF8", "EEF3FA": "E3EEF8",
        "DCE6F3": "D2E3F3", "C9D8EC": "BBD4EE", "B9CCE8": "A9CBEB", "B7C9E5": "A9CBEB",
        "AFC2DE": "A0C4E8", "A9BEDD": "A0C4E8", "A7BEDF": "A0C4E8", "9DB5D8": "A0C4E8", "93AED6": "A0C4E8",
        "9FB4D6": "A0C4E8", "8EA7CF": "77AADD", "7F9CC8": "5590C8", "6E8DBE": "5590C8", "718DBA": "5590C8",
        "6F8BBA": "5590C8", "6A84AE": "4477AA", "4F6FA3": "4477AA", "4C72B0": "4477AA"}
TEAL_TO_BLUE = {"F6FCFA": "F2F7FC", "F3F9F9": "F2F7FC", "F0F6F3": "F2F7FC", "EDF7F3": "E3EEF8", "E8F2EE": "E3EEF8",
                "E6F3F1": "E3EEF8", "D3EBE8": "BBD4EE", "93CEC6": "77AADD", "94C6C0": "5590C8", "8CC0B9": "5590C8",
                "8BAEAC": "5590C8", "74AA9D": "5590C8", "5A9E96": "4477AA", "10301A": "1F3A63", "08303A": "1F3A63"}
TEAL_TO_CYAN = {"F6FCFA": "F3FBFF", "F3F9F9": "F3FBFF", "F0F6F3": "F3FBFF", "EDF7F3": "E6F6FF", "E8F2EE": "E6F6FF",
                "E6F3F1": "E6F6FF", "D3EBE8": "D2F0FF", "93CEC6": "99DDFF", "94C6C0": "5BB8E6", "8CC0B9": "5BB8E6",
                "8BAEAC": "5BB8E6", "74AA9D": "5BB8E6", "5A9E96": "3A9BC9", "10301A": "1E5470", "08303A": "1E5470"}
TRAIN = {"FFFAF3": "FDF5F2", "FCF8F2": "FDF5F2", "FBF6EE": "FDF5F2", "FAF2E6": "FDF0EA", "F6EBDA": "FDF0EA",
         "F4E4CC": "FBE2D8", "E6D8C3": "FBE2D8", "EDD3AF": "F7C9B6", "EDD9BC": "F7C9B6", "D9BC94": "F2AA90",
         "D8C3A0": "F2AA90", "CDB089": "F2AA90", "C9A678": "EE8866", "C49E6C": "EE8866", "B88A52": "D06A48",
         "B08A57": "D06A48", "8E6A3E": "8F3F22", "6B5434": "8F3F22"}
RISK = {"F8ECEE": "FFEEF1", "EDCBD0": "FFD5DD", "E2AEB6": "FFAABB", "8E2C3A": "A33F59"}
FILM = {"F2C3A0": "EEDD88", "F8DCC7": "F6ECC0", "E0A77E": "D6BE4E", "C98A5E": "B59A2E"}
COND = {"DCE6F3": "F6ECC0", "6E8DBE": "B59A2E", "C9D8EC": "F6ECC0", "7F9CC8": "B59A2E"}
LORA = {"C98A5E": "EE8866", "B88A52": "EE8866", "F2C49B": "F7C9B6", "FFFAF5": "FDF2EE", "9A6A45": "B0502C",
        "7A4A22": "8F3F22"}


def sub(el, m):
    for c in el.iter("{%s}srgbClr" % A):
        v = c.get("val").upper()
        if v in m:
            c.set("val", m[v])


def fill_of(el):
    sp = el.find("{%s}spPr" % P)
    if sp is None:
        return None
    sf = sp.find("{%s}solidFill/{%s}srgbClr" % (A, A))
    return sf.get("val").upper() if sf is not None else None


def line_of(el):
    ln = el.find("{%s}spPr/{%s}ln" % (P, A))
    if ln is None:
        return None, False
    c = ln.find("{%s}solidFill/{%s}srgbClr" % (A, A))
    return (c.get("val").upper() if c is not None else None), ln.find("{%s}prstDash" % A) is not None


def text_of(el):
    return "".join(t.text or "" for t in el.iter("{%s}t" % A))


def in_group(el):
    p = el.getparent()
    while p is not None:
        if p.tag == "{%s}grpSp" % P:
            return True
        if p.tag == "{%s}spTree" % P:
            return False
        p = p.getparent()
    return False


SHAPES = ("{%s}sp" % P, "{%s}cxnSp" % P)


def recolor(n, root):
    for el in root.iter(*SHAPES):
        f = fill_of(el); l, dashed = line_of(el); txt = text_of(el)
        if n == 1:
            if f in ("F2C3A0", "C98A5E") or (l == "C98A5E"):
                sub(el, FILM)
            if any(k in etree.tostring(el).decode() for k in TEAL_TO_BLUE):
                sub(el, TEAL_TO_CYAN if in_group(el) else TEAL_TO_BLUE)
        elif n == 2:
            if f in ("F2C3A0", "F8DCC7", "E0A77E"):
                sub(el, FILM)
            elif f in ("F2C49B", "FFFAF5") or (l in ("C98A5E", "B88A52") and (dashed or f is None)) or "LoRA" in txt or "trainable" in txt:
                sub(el, LORA)
            elif f == "DCE6F3" and l == "6E8DBE":
                sub(el, COND)
            elif el.tag == "{%s}cxnSp" % P and l == "6E8DBE":
                sub(el, COND)
            if txt.strip() in ("condition path",) or "condition" in txt and f is None:
                sub(el, {"6E8DBE": "8A7419", "2E4A73": "8A7419"})
        elif n == 3:
            if f == "DCE6F3":
                sub(el, COND)
            elif el.tag == "{%s}cxnSp" % P and l == "6E8DBE":
                sub(el, COND)
    for m in (FILM if n == 1 else LORA if n == 2 else {}, TRAIN, RISK, BLUE):
        sub(root, m)


src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src); zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    m = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", item.filename)
    if m:
        root = etree.fromstring(data); recolor(int(m.group(1)), root)
        data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zout.writestr(item, data)
zout.close(); print("recoloured", dst)
