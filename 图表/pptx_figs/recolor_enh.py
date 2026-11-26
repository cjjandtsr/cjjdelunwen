"""Recolour Figs. 1-4 (slides 1-5) to the low-saturation palette of Liu et al. 2026 (Enhancing, AEJ 140), Fig. 1,
sampled from the published PDF at 300 dpi:
  grey panels        #F5F5F5 / #A9AEB5
  slate blue-grey    #DBE3EF / #95A9CE / #899DBE   policy, U-Net, execution (frozen parts carry the lock)
  soft orange        #FBE3D2 / #F6C7A6 / #C9773F   condition and FiLM (Enhancing draws FiLM in orange)
  cream / olive-brown #FEF1CB / #817153            LoRA, trainable parameters, post-training-only signals
  pale green         #E7F3DF / #8DB580             observations (state-space inputs)
  muted rose         #EDD3D3 / #A65D61             risk / collision danger
Role-specific recolouring is decided per shape; remaining colours follow the family maps."""
import sys, re, zipfile
from lxml import etree

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"

BLUE = {"F5F8FC": "F5F5F5", "F7F9FC": "F5F5F5", "F4F7FB": "F5F5F5", "F2F6FB": "F5F5F5",
        "EAF0F8": "EEF2F8", "E3EBF6": "EEF2F8", "E6EDF7": "EEF2F8", "EEF3FA": "EEF2F8",
        "DCE6F3": "DBE3EF", "C9D8EC": "DBE3EF", "B9CCE8": "BFCBE0", "B7C9E5": "BFCBE0",
        "A9BEDD": "A9AEB5", "AFC2DE": "B2C0D8", "A7BEDF": "B2C0D8", "9DB5D8": "B2C0D8", "93AED6": "B2C0D8",
        "9FB4D6": "B2C0D8", "8EA7CF": "95A9CE", "7F9CC8": "899DBE", "6E8DBE": "899DBE", "718DBA": "899DBE",
        "6F8BBA": "899DBE", "6A84AE": "6F82A8", "4F6FA3": "6F82A8", "4C72B0": "6F82A8"}
TEAL_TO_BLUE = {"F6FCFA": "F5F5F5", "F3F9F9": "F5F5F5", "F0F6F3": "F5F5F5", "EDF7F3": "EEF2F8", "E8F2EE": "EEF2F8",
                "E6F3F1": "EEF2F8", "D3EBE8": "DBE3EF", "93CEC6": "95A9CE", "94C6C0": "899DBE", "8CC0B9": "899DBE",
                "8BAEAC": "A9AEB5", "74AA9D": "899DBE", "5A9E96": "6F82A8", "10301A": "2F3E5C", "08303A": "2F3E5C"}
TEAL_TO_CYAN = {"F6FCFA": "F4F9F1", "F3F9F9": "F4F9F1", "F0F6F3": "F4F9F1", "EDF7F3": "E7F3DF", "E8F2EE": "E7F3DF",
                "E6F3F1": "E7F3DF", "D3EBE8": "D5E8CC", "93CEC6": "A9CF9A", "94C6C0": "8DB580", "8CC0B9": "8DB580",
                "8BAEAC": "A9AEB5", "74AA9D": "8DB580", "5A9E96": "6E9A61", "10301A": "3E5A35", "08303A": "3E5A35"}
TRAIN = {"FFFAF3": "FFFBED", "FCF8F2": "FFFBED", "FBF6EE": "FFFBED", "FAF2E6": "FEF6DC", "F6EBDA": "FEF6DC",
         "F4E4CC": "FEF1CB", "E6D8C3": "FEF1CB", "EDD3AF": "F7E3A8", "EDD9BC": "F7E3A8", "D9BC94": "CDBB8A",
         "D8C3A0": "CDBB8A", "CDB089": "CDBB8A", "C9A678": "AC9A6A", "C49E6C": "AC9A6A", "B88A52": "817153",
         "B08A57": "817153", "8E6A3E": "5E5236", "6B5434": "5E5236"}
RISK = {"F8ECEE": "F7ECEC", "EDCBD0": "EDD3D3", "E2AEB6": "E2B7B7", "8E2C3A": "A65D61"}
FILM = {"F2C3A0": "F6C7A6", "F8DCC7": "FBE3D2", "E0A77E": "E3A47A", "C98A5E": "C9773F"}
COND = {"DCE6F3": "FBE3D2", "6E8DBE": "D9925E", "C9D8EC": "FBE3D2", "7F9CC8": "D9925E"}
LORA = {"C98A5E": "817153", "B88A52": "817153", "F2C49B": "F7E3A8", "FFFAF5": "FFFBED", "9A6A45": "5E5236",
        "7A4A22": "5E5236"}


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
    """True when the shape sits in the top-level group that holds the observation panel."""
    p, top = el.getparent(), None
    while p is not None and p.tag != "{%s}spTree" % P:
        if p.tag == "{%s}grpSp" % P:
            top = p
        p = p.getparent()
    return top is not None and any(k in text_of(top) for k in ("Observation", "Local point cloud", "Relative goal"))


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
                sub(el, {"6E8DBE": "8A4B22", "2E4A73": "8A4B22"})
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
