"""Slide 1 (Fig. 1): FiLM layers and condition arrows from orange to the condition purple used in Figs. 2 and 4."""
import sys, zipfile, shutil
src, dst = sys.argv[1], sys.argv[2]
MAP = {'val="F2C3A0"': 'val="DCD3F0"', 'val="C98A5E"': 'val="8E7CC3"'}
zin = zipfile.ZipFile(src)
zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename == "ppt/slides/slide1.xml":
        t = data.decode("utf-8")
        for a, b in MAP.items():
            print(a, "->", b, t.count(a)); t = t.replace(a, b)
        data = t.encode("utf-8")
    zout.writestr(item, data)
zout.close()
