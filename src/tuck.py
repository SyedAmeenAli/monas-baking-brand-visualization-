"""Straight-tuck-end brownie box (4-piece, 5.5 x 5.5 x 2.5 in internal, from the approved concept sheet).
Panel-tree geometry reusing the 4-inch engine primitives. Unvalidated design geometry - see spec."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '01_CAKE_BOXES', '4-inch', 'src'))
import geom as g
from geom import Edge, line, poly, Panel, rect_edges, art_frame, CUT, CREASE, GLUE

IN = 25.4
L = 5.5 * IN        # front/back width
Wd = 5.5 * IN       # side width
Hh = 2.5 * IN       # height
GW = 15.0           # glue flap
TD = Wd - 1.5       # tuck flap depth
TL = 16.0           # tuck tongue
DD = Wd / 2 - 2.0   # dust flap depth
CH = 6.0
YB0 = TD + TL + 1
SHEET_W = GW + 2 * L + 2 * Wd
SHEET_H = YB0 + Hh + TD + TL + 1


def trap(p0, p1, out, depth, c0=0.0, c1=0.0, kind_h=CREASE):
    (x0, y0), (x1, y1) = p0, p1
    Ln = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / Ln, (y1 - y0) / Ln
    q1 = (x1 + out[0] * depth - ux * c1, y1 + out[1] * depth - uy * c1)
    q0 = (x0 + out[0] * depth + ux * c0, y0 + out[1] * depth + uy * c0)
    return [line(p0, p1, kind_h), line(p1, q1, CUT), line(q1, q0, CUT), line(q0, p0, CUT)]


def build():
    P = {}
    x0 = 0.0
    xF0, xF1 = x0, x0 + L
    xS0, xS1 = xF1, xF1 + Wd
    xK0, xK1 = xS1, xS1 + L
    xL0, xL1 = xK1, xK1 + Wd
    xG0, xG1 = xL1, xL1 + GW
    y0, y1 = YB0, YB0 + Hh
    full = lambda a, b: [(a, b)]
    P['F'] = Panel('F', rect_edges(xF0, y0, xF1, y1, right=[(y0, y1)]), None, None, 0, art_frame((1, 0), (0, 1), (xF0, y0), (L, Hh)), 'front')
    P['SR'] = Panel('SR', rect_edges(xS0, y0, xS1, y1, top=[(xS0 + 0.5, xS1 - 0.5)], right=[(y0, y1)], bottom=[(xS0 + 0.5, xS1 - 0.5)], left=[(y0, y1)]),
                    'F', ((xF1, y0), (xF1, y1)), 90, art_frame((1, 0), (0, 1), (xS0, y0), (Wd, Hh)), 'side')
    P['K'] = Panel('K', rect_edges(xK0, y0, xK1, y1, top=[(xK0 + 0.5, xK1 - 0.5)], right=[(y0, y1)], bottom=[(xK0 + 0.5, xK1 - 0.5)], left=[(y0, y1)]),
                   'SR', ((xS1, y0), (xS1, y1)), 90, art_frame((1, 0), (0, 1), (xK0, y0), (L, Hh)), 'back')
    P['SL'] = Panel('SL', rect_edges(xL0, y0, xL1, y1, top=[(xL0 + 0.5, xL1 - 0.5)], right=[(y0, y1)], bottom=[(xL0 + 0.5, xL1 - 0.5)], left=[(y0, y1)]),
                    'K', ((xK1, y0), (xK1, y1)), 90, art_frame((1, 0), (0, 1), (xL0, y0), (Wd, Hh)), 'side')
    gl = [line((xG0, y0 + 0.0), (xG0, y1), CREASE), line((xG0, y1), (xG1, y1 - 8), CUT), line((xG1, y1 - 8), (xG1, y0 + 8), CUT), line((xG1, y0 + 8), (xG0, y0), CUT)]
    P['G'] = Panel('G', gl, 'SL', ((xG0, y0), (xG0, y1)), 90, None, 'glue')
    # fix: glue flap hinge along SL right edge; polygon order consistent
    # top / bottom tuck flaps on K, dust flaps on sides
    for tag, yy, d in (('T', y0, -1), ('B', y1, +1)):
        # tuck flap
        ya, yb = yy, yy + d * TD
        tt = [line((xK0 + 0.5, ya), (xK1 - 0.5, ya), CREASE), line((xK1 - 0.5, ya), (xK1 - 0.5, yb), CUT),
              line((xK1 - 0.5, yb), (xK0 + 0.5, yb), CREASE), line((xK0 + 0.5, yb), (xK0 + 0.5, ya), CUT)]
        fr = art_frame((-1, 0), (0, -1), (xK1 - 0.5, ya), (L - 1, TD)) if d < 0 else art_frame((1, 0), (0, 1), (xK0 + 0.5, ya), (L - 1, TD))   # art-up toward the hinge (back)
        P['TT' + tag] = Panel('TT' + tag, tt, 'K', ((xK0 + 0.5, ya), (xK1 - 0.5, ya)), 90, fr, 'tuck')
        yc = yb + d * TL
        tx0, tx1 = xK0 + 6, xK1 - 6
        tg = [line((tx0, yb), (tx1, yb), CREASE), line((tx1, yb), (tx1 - 2, yc - d * 5), CUT), line((tx1 - 2, yc - d * 5), (tx1 - 8, yc), CUT),
              line((tx1 - 8, yc), (tx0 + 8, yc), CUT), line((tx0 + 8, yc), (tx0 + 2, yc - d * 5), CUT), line((tx0 + 2, yc - d * 5), (tx0, yb), CUT)]
        P['TG' + tag] = Panel('TG' + tag, tg, 'TT' + tag, ((tx0, yb), (tx1, yb)), 90, None, 'tongue')
        # dust flaps (one per side panel)
        for nm, xa, xb in (('SR', xS0 + 0.5, xS1 - 0.5), ('SL', xL0 + 0.5, xL1 - 0.5)):
            ds = trap((xa, yy), (xb, yy), (0, d), DD, 2.0, CH)
            P['D' + nm + tag] = Panel('D' + nm + tag, ds, nm, ((xa, yy), (xb, yy)), 90, None, 'dust')
    # print art frames for flaps (flat pink so nothing is left white)
    for n, p in P.items():
        if p.art is None and p.role in ('dust', 'tongue'):
            r = p.ring()
            xs, ys = [q[0] for q in r], [q[1] for q in r]
            p.art = art_frame((1, 0), (0, 1), (min(xs), min(ys)), (max(xs) - min(xs), max(ys) - min(ys)))
    return P


def exportable():
    return build()
