"""Parametric straight-tuck carton (same panel-tree engine) with optional window holes in the front panel or the lid flap.
Used for the cupcake window box and the bento carton. Unvalidated design geometry."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '01_CAKE_BOXES', '4-inch', 'src'))
import geom as g
from geom import Panel, rect_edges, art_frame, line, CUT, CREASE
import tuck as T


def rrect(x0, y0, x1, y1, r=6.0, n=5):
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return [line(pts[i], pts[(i + 1) % len(pts)], CUT) for i in range(len(pts))]


def build(L, Wd, Hh, GW=15.0, front_win=None, lid_win=None):
    """front_win = (mx, top, bottom) margins; lid_win = (mx, my) margins on the lid flap."""
    TD, TL, DD, CH = Wd - 1.5, 16.0, Wd / 2 - 2.0, 6.0
    YB0 = TD + TL + 1
    SW, SH = GW + 2 * L + 2 * Wd, YB0 + Hh + TD + TL + 1
    P = {}
    xF0, xF1 = 0.0, L
    xS0, xS1 = xF1, xF1 + Wd
    xK0, xK1 = xS1, xS1 + L
    xL0, xL1 = xK1, xK1 + Wd
    xG0, xG1 = xL1, xL1 + GW
    y0, y1 = YB0, YB0 + Hh
    fh = [rrect(xF0 + front_win[0], y0 + front_win[1], xF1 - front_win[0], y1 - front_win[2])] if front_win else None
    P['F'] = Panel('F', rect_edges(xF0, y0, xF1, y1, right=[(y0, y1)]), None, None, 0, art_frame((1, 0), (0, 1), (xF0, y0), (L, Hh)), 'front', holes=fh)
    P['SR'] = Panel('SR', rect_edges(xS0, y0, xS1, y1, top=[(xS0 + 0.5, xS1 - 0.5)], right=[(y0, y1)], bottom=[(xS0 + 0.5, xS1 - 0.5)], left=[(y0, y1)]),
                    'F', ((xF1, y0), (xF1, y1)), 90, art_frame((1, 0), (0, 1), (xS0, y0), (Wd, Hh)), 'side')
    P['K'] = Panel('K', rect_edges(xK0, y0, xK1, y1, top=[(xK0 + 0.5, xK1 - 0.5)], right=[(y0, y1)], bottom=[(xK0 + 0.5, xK1 - 0.5)], left=[(y0, y1)]),
                   'SR', ((xS1, y0), (xS1, y1)), 90, art_frame((1, 0), (0, 1), (xK0, y0), (L, Hh)), 'back')
    P['SL'] = Panel('SL', rect_edges(xL0, y0, xL1, y1, top=[(xL0 + 0.5, xL1 - 0.5)], right=[(y0, y1)], bottom=[(xL0 + 0.5, xL1 - 0.5)], left=[(y0, y1)]),
                    'K', ((xK1, y0), (xK1, y1)), 90, art_frame((1, 0), (0, 1), (xL0, y0), (Wd, Hh)), 'side')
    gl = [line((xG0, y0), (xG0, y1), CREASE), line((xG0, y1), (xG1, y1 - 8), CUT), line((xG1, y1 - 8), (xG1, y0 + 8), CUT), line((xG1, y0 + 8), (xG0, y0), CUT)]
    P['G'] = Panel('G', gl, 'SL', ((xG0, y0), (xG0, y1)), 90, None, 'glue')
    for tag, yy, d in (('T', y0, -1), ('B', y1, +1)):
        ya, yb = yy, yy + d * TD
        tt = [line((xK0 + 0.5, ya), (xK1 - 0.5, ya), CREASE), line((xK1 - 0.5, ya), (xK1 - 0.5, yb), CUT),
              line((xK1 - 0.5, yb), (xK0 + 0.5, yb), CREASE), line((xK0 + 0.5, yb), (xK0 + 0.5, ya), CUT)]
        fr = art_frame((-1, 0), (0, -1), (xK1 - 0.5, ya), (L - 1, TD)) if d < 0 else art_frame((1, 0), (0, 1), (xK0 + 0.5, ya), (L - 1, TD))
        hl = None
        if tag == 'T' and lid_win:
            mx, my = lid_win
            hl = [rrect(xK0 + 0.5 + mx, yb + my, xK1 - 0.5 - mx, ya - my, 8.0)]
        P['TT' + tag] = Panel('TT' + tag, tt, 'K', ((xK0 + 0.5, ya), (xK1 - 0.5, ya)), 90, fr, 'tuck', holes=hl)
        yc = yb + d * TL
        tx0, tx1 = xK0 + 6, xK1 - 6
        tg = [line((tx0, yb), (tx1, yb), CREASE), line((tx1, yb), (tx1 - 2, yc - d * 5), CUT), line((tx1 - 2, yc - d * 5), (tx1 - 8, yc), CUT),
              line((tx1 - 8, yc), (tx0 + 8, yc), CUT), line((tx0 + 8, yc), (tx0 + 2, yc - d * 5), CUT), line((tx0 + 2, yc - d * 5), (tx0, yb), CUT)]
        P['TG' + tag] = Panel('TG' + tag, tg, 'TT' + tag, ((tx0, yb), (tx1, yb)), 90, None, 'tongue')
        for nm, xa, xb in (('SR', xS0 + 0.5, xS1 - 0.5), ('SL', xL0 + 0.5, xL1 - 0.5)):
            P['D' + nm + tag] = Panel('D' + nm + tag, T.trap((xa, yy), (xb, yy), (0, d), DD, 2.0, CH), nm, ((xa, yy), (xb, yy)), 90, None, 'dust')
    for n, p in P.items():
        if p.art is None and p.role in ('dust', 'tongue'):
            r = p.ring()
            xs, ys = [q[0] for q in r], [q[1] for q in r]
            p.art = art_frame((1, 0), (0, 1), (min(xs), min(ys)), (max(xs) - min(xs), max(ys) - min(ys)))
    info = dict(SW=SW, SH=SH, YB0=YB0, TD=TD, GW=GW, L=L, Wd=Wd, Hh=Hh, xS0=xS0, xK0=xK0, xL0=xL0)
    return P, info
