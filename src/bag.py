"""Gusseted paper shopping bag, flat-bottom, 180 x 90 x 240 mm. Panel-tree geometry (same engine as the boxes).
Open-bag model: the gusset is two half panels joined at a 0 deg V-crease (so the crease is on the dieline).
Unvalidated design geometry: no hem, no handle patch, no paper-weight compensation."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '01_CAKE_BOXES', '4-inch', 'src'))
import geom as g
from geom import Panel, rect_edges, art_frame, line, CUT, CREASE
import tuck as T

K = float(os.environ.get('MONA_BAG_K', 1))
L, WD, H, GW = 180.0 * K, 90.0 * K, 240.0 * K, 20.0 * K     # front width, gusset, height, seam glue flap
FD = 58.0 * K                                   # front bottom flap depth (overlaps the back flap)
SD = WD / 2                                 # back + gusset bottom flap depth
HOLE_R, HOLE_DY, HOLE_DX = 4.2 * K, 14.0 * K, 30.0 * K  # cord holes: radius, below top edge, half spacing
xF1 = L
xSm1 = L + WD / 2
xS1 = L + WD
xK1 = xS1 + L
xSm2 = xK1 + WD / 2
xL1 = xK1 + WD
xG1 = xL1 + GW
SW, SH = xG1, H + FD


def circle(cx, cy, r, n=24):
    pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return [line(pts[i], pts[(i + 1) % n], CUT) for i in range(n)]


def build():
    P = {}
    fh = lambda xc: [circle(xc - HOLE_DX, HOLE_DY, HOLE_R), circle(xc + HOLE_DX, HOLE_DY, HOLE_R)]
    full = (0, H)
    P['F'] = Panel('F', rect_edges(0, 0, L, H, right=[full], bottom=[(0, L)]), None, None, 0,
                   art_frame((1, 0), (0, 1), (0, 0), (L, H)), 'front', holes=fh(L / 2))
    P['SRa'] = Panel('SRa', rect_edges(L, 0, xSm1, H, right=[full], bottom=[(L, xSm1)], left=[full]), 'F', ((L, 0), (L, H)), 90,
                     art_frame((1, 0), (0, 1), (L, 0), (WD, H)), 'side')
    P['SRb'] = Panel('SRb', rect_edges(xSm1, 0, xS1, H, right=[full], bottom=[(xSm1, xS1)], left=[full]), 'SRa', ((xSm1, 0), (xSm1, H)), 0,
                     art_frame((1, 0), (0, 1), (L, 0), (WD, H)), 'side')
    P['K'] = Panel('K', rect_edges(xS1, 0, xK1, H, right=[full], bottom=[(xS1, xK1)], left=[full]), 'SRb', ((xS1, 0), (xS1, H)), 90,
                   art_frame((1, 0), (0, 1), (xS1, 0), (L, H)), 'back', holes=fh(xS1 + L / 2))
    P['SLa'] = Panel('SLa', rect_edges(xK1, 0, xSm2, H, right=[full], bottom=[(xK1, xSm2)], left=[full]), 'K', ((xK1, 0), (xK1, H)), 90,
                     art_frame((1, 0), (0, 1), (xK1, 0), (WD, H)), 'side')
    P['SLb'] = Panel('SLb', rect_edges(xSm2, 0, xL1, H, right=[full], bottom=[(xSm2, xL1)], left=[full]), 'SLa', ((xSm2, 0), (xSm2, H)), 0,
                     art_frame((1, 0), (0, 1), (xK1, 0), (WD, H)), 'side')
    gl = [line((xL1, 0), (xL1, H), CREASE), line((xL1, H), (xG1, H - 8), CUT), line((xG1, H - 8), (xG1, 8), CUT), line((xG1, 8), (xL1, 0), CUT)]
    P['G'] = Panel('G', gl, 'SLb', ((xL1, 0), (xL1, H)), 90, None, 'glue')
    # bottom: gusset flaps fold first, then back flap, then the long front flap on top
    def flap(name, parent, x0, x1, depth, ch, role):
        P[name] = Panel(name, T.trap((x0, H), (x1, H), (0, 1), depth, ch, ch), parent, ((x0, H), (x1, H)), 90, None, role)
    flap('BSR', 'SRa', L, xS1, SD, 2.0, 'under2')
    flap('BSL', 'SLa', xK1, xL1, SD, 2.0, 'under2')
    flap('BK', 'K', xS1, xK1, SD, 2.0, 'under')
    flap('BF', 'F', 0, L, FD, 0.0, '')
    for n, p in P.items():
        if p.art is None and p.role != 'glue':
            r = p.ring()
            xs, ys = [q[0] for q in r], [q[1] for q in r]
            p.art = art_frame((1, 0), (0, 1), (min(xs), min(ys)), (max(xs) - min(xs), max(ys) - min(ys)))
    return P
