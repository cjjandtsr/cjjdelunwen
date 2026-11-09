"""Absolute geometry (canvas px, 96 px/in) of every shape on a slide, including shapes inside groups."""
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
PX = 9525


def _gi(g):
    x = g._element.grpSpPr.find('.//' + A + 'xfrm')
    o = x.find(A + 'off'); e = x.find(A + 'ext'); co = x.find(A + 'chOff'); ce = x.find(A + 'chExt')
    return [int(v) for v in (o.get('x'), o.get('y'), e.get('cx'), e.get('cy'), co.get('x'), co.get('y'), ce.get('cx'), ce.get('cy'))]


def boxes(slide):
    """List of (shape, x, y, w, h, depth) in px; groups themselves are listed too."""
    out = []

    def walk(shapes, T=lambda x, y: (x, y), S=(1.0, 1.0), d=0):
        for sh in shapes:
            if sh.shape_type == 6:
                ox, oy, ex, ey, cx, cy, cex, cey = _gi(sh)
                x, y = T(ox, oy)
                out.append((sh, x / PX, y / PX, ex * S[0] / PX, ey * S[1] / PX, d))
                sx, sy = ex / cex if cex else 1, ey / cey if cey else 1
                def T2(a, b, T=T, ox=ox, oy=oy, cx=cx, cy=cy, sx=sx, sy=sy):
                    return T(ox + (a - cx) * sx, oy + (b - cy) * sy)
                walk(sh.shapes, T2, (S[0] * sx, S[1] * sy), d + 1)
                continue
            x, y = T(sh.left or 0, sh.top or 0)
            out.append((sh, x / PX, y / PX, (sh.width or 0) * S[0] / PX, (sh.height or 0) * S[1] / PX, d))
    walk(slide.shapes)
    return out


def inside(b, rect, tol=1.0):
    _, x, y, w, h, _ = b
    X0, Y0, X1, Y1 = rect
    return x >= X0 - tol and y >= Y0 - tol and x + w <= X1 + tol and y + h <= Y1 + tol


def remove(sh):
    el = sh._element
    el.getparent().remove(el)
