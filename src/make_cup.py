"""Dessert cup sleeve: a cone blank (annular sector) with radial awning stripes. Computes the real cone development from
top/bottom diameter and height, writes dieline + art + PDFs + textures + scene.json (cone block) for the viewer."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
import render as R
from ink import *
import scenes as S
import pymupdf as fz

RT, RB, HC = float(os.environ.get('MONA_CUP_RT', 45)), float(os.environ.get('MONA_CUP_RB', 30)), float(os.environ.get('MONA_CUP_H', 75))          # top radius, bottom radius, height (mm)
SL = math.hypot(HC, RT - RB)           # slant height
RO = RT * SL / (RT - RB)               # outer arc radius of the blank
RI = RO - SL
TH = 2 * math.pi * RT / RO             # sector angle
TAB = math.radians(3.2)                # glue tab angle
GLUE_W = 0.0
BASE_R = 36.0                          # base disc blank radius (30 + 6 flange)
GAP = 14.0


def pt(r, a):
    return (r * math.sin(a), r * math.cos(a))


def sector_pts(a0, a1, n=70):
    outer = [pt(RO, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    inner = [pt(RI, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return outer + inner


body = sector_pts(-TH / 2, TH / 2)
tabp = sector_pts(TH / 2, TH / 2 + TAB, 6)
allp = body + tabp
xmin, xmax = min(p[0] for p in allp), max(p[0] for p in allp)
ymin, ymax = min(p[1] for p in allp), max(p[1] for p in allp)
OX, OY = -xmin, -ymin                  # apex position in sheet coords
SWS = xmax - xmin
SW = SWS + GAP + 2 * BASE_R
SH = max(ymax - ymin, 2 * BASE_R)
BCX, BCY = SWS + GAP + BASE_R, SH / 2


def sh(p):
    return (p[0] + OX, p[1] + OY)


def path_d(pts, close=True):
    q = [sh(p) for p in pts]
    return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in q) + (' Z' if close else '')


def art():
    cid = 'cupclip'
    o = f'<defs><clipPath id="{cid}"><path d="{path_d(body)}"/></clipPath></defs><g clip-path="url(#{cid})">'
    o += f'<path d="{path_d(body)}" fill="{CREAM}"/>'
    N = 14
    for i in range(N):
        a0, a1 = -TH / 2 + TH * i / N, -TH / 2 + TH * (i + 1) / N
        w = [sh(p) for p in sector_pts(a0, a1, 4)]
        o += shape(w, BLUSH if i % 2 == 0 else CREAM, 0.35, dx=0.4, dy=0.3)
    rm = (RI + RO) / 2 + 2
    cx, cy = sh(pt(rm, 0))
    g = shape(ellipse_pts(cx, cy, 25, 18, 30), CREAM, 0.7)
    g += line(ellipse_pts(cx, cy, 21.5, 14.8, 30), 0.3, closed=True, double=False, dash='1.2 1.1')
    lw = 40
    g += f'<image x="{cx-lw/2:.2f}" y="{cy-lw*0.333-2.5:.2f}" width="{lw}" height="{lw*640/960:.2f}" xlink:href="{R.logo_uri}" href="{R.logo_uri}"/>'
    g += hand('with love', cx, cy + 12, 5.4, CAVEAT, COCOA)
    o += f'<g transform="rotate(180 {cx:.2f} {cy:.2f})">{g}</g>'
    for s in (-1, 1):
        px, py = sh(pt(rm - 3, s * TH * 0.33))
        c = cherry(px, py + 2, 3.0) if s < 0 else strawberry(px, py, 3.6)
        o += f'<g transform="rotate(180 {px:.2f} {py:.2f})">{c}</g>'
    for k in range(34):                               # scalloped rim (rim is the outer arc)
        a = -TH / 2 + TH * (k + 0.5) / 34
        x, y = sh(pt(RO - 1.0, a))
        o += shape(ellipse_pts(x, y, 3.3, 3.3, 10), CREAM, 0.4, dx=0.2, dy=0.15)
    o += grain(SW, SH) + '</g>'
    return o


def dieline():
    cut = f'<path d="{path_d(body[:71] + body[71:] + [])}"/>'
    ring = path_d(body + tabp[:0])
    tabd = path_d(tabp)
    outline = f'<path d="{path_d(body)}"/><path d="{tabd}"/><circle cx="{BCX:.2f}" cy="{BCY:.2f}" r="{BASE_R}"/>'
    a = TH / 2
    x0, y0 = sh(pt(RI, a)); x1, y1 = sh(pt(RO, a))
    crease = f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}"/><circle cx="{BCX:.2f}" cy="{BCY:.2f}" r="{BASE_R-6}"/>'
    glue = f'<path d="{tabd}"/>'
    o = f'<g id="GLUE" fill="{R.C_GLUE}" fill-opacity=".38" stroke="none">{glue}</g>'
    o += f'<g id="CREASE" fill="none" stroke="{R.C_CREASE}" stroke-width="0.24" stroke-dasharray="2.2 1.2">{crease}</g>'
    o += f'<g id="CUT" fill="none" stroke="{R.C_CUT}" stroke-width="0.3" stroke-linejoin="round">{outline}</g>'
    return o


def dims():
    o = ''
    arc_o = RO * TH
    arc_i = RI * TH
    # slant dimension, parallel to the left radial edge
    a = -TH / 2
    ux, uy = math.sin(a), math.cos(a)
    nx, ny = -uy, ux                      # normal pointing outward-left
    ax, ay = sh((RI * ux - 6 * nx * -1 * -1, RI * uy))
    p0 = sh((RI * ux + nx * -9 * -1, RI * uy + ny * -9 * -1))
    p1 = sh((RO * ux + nx * -9 * -1, RO * uy + ny * -9 * -1))
    o += (f'<g class="d"><path d="M{p0[0]:.2f},{p0[1]:.2f} L{p1[0]:.2f},{p1[1]:.2f}"/>'
          f'<text x="{(p0[0]+p1[0])/2 - 3:.2f}" y="{(p0[1]+p1[1])/2:.2f}" data-mm="{SL:.2f}" text-anchor="middle" '
          f'transform="rotate({math.degrees(math.atan2(p1[1]-p0[1], p1[0]-p0[0])):.2f} {(p0[0]+p1[0])/2 - 3:.2f} {(p0[1]+p1[1])/2:.2f})">{SL:.1f}</text></g>')
    bx, by = sh(pt(RO, 0))
    o += f'<g class="d"><text x="{bx:.2f}" y="{by+8:.2f}" data-mm="{arc_o:.2f}" text-anchor="middle">{arc_o:.1f}</text></g>'
    ix, iy = sh(pt(RI, 0))
    o += f'<g class="d"><text x="{ix:.2f}" y="{iy-3:.2f}" data-mm="{arc_i:.2f}" text-anchor="middle">{arc_i:.1f}</text></g>'
    o += f'<g class="d"><path d="M{BCX-BASE_R:.2f},{BCY+BASE_R+4:.2f} H{BCX+BASE_R:.2f}"/><text x="{BCX:.2f}" y="{BCY+BASE_R+2.4:.2f}" data-mm="{2*BASE_R}" text-anchor="middle">{2*BASE_R:.1f}</text></g>'
    o += R.dim_h(0, SW, -8, 0, SW) + R.dim_v(-4, 0, SH, -6, SH)
    return o


if __name__ == '__main__':
    KEY = os.environ.get('MONA_CUP_KEY', 'cup')
    pr = R.Product(KEY, os.environ.get('MONA_CUP_TITLE', 'Dessert cup sleeve, 90 mm top, 75 mm tall'), {}, SW, SH, None, None, 'tube', '')
    A = art()
    D = dieline()
    pages = {'art_outside': R.svg_page(pr, A), 'dieline': R.svg_page(pr, D), 'proof_outside': R.svg_page(pr, A + D)}
    for k, v in pages.items():
        open(os.path.join(pr.out, f'{k}.svg'), 'w', encoding='utf-8').write(v)
    docs = {k: R.to_pdf(pr, v, f'{KEY}_{k}') for k, v in pages.items()}
    docs['art_outside'].save(os.path.join(pr.out, f'{KEY}_print_artwork.pdf'))
    docs['dieline'].save(os.path.join(pr.out, f'{KEY}_dieline.pdf'))
    docs['art_outside'][0].get_pixmap(dpi=110, alpha=False).save(os.path.join(pr.out, 'tex_outside.png'))
    docs['art_outside'][0].get_pixmap(dpi=110, alpha=False).save(os.path.join(pr.out, 'tex_inside.png'))
    master = f'<g id="ART_OUTSIDE">{A}</g>' + D
    open(os.path.join(pr.out, f'{KEY}_dieline_master.svg'), 'w', encoding='utf-8').write(R.svg_page(pr, master))
    dim = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-22 -22 {SW+44:.2f} {SH+44:.2f}" class="dieline-svg">'
           f'<g id="art">{A}</g>{D}<g id="dims">{dims()}</g></svg>')
    open(os.path.join(pr.out, 'dieline_dim.svg'), 'w', encoding='utf-8').write(dim)
    json.dump({'key': KEY, 'title': pr.title, 'sheet': [SW, SH], 'pad': R.PAD, 'mode': 'tube', 'shift': [0, 0, 0], 'panels': [],
               'cone': {'Rt': RT, 'Rb': RB, 'h': HC, 'sl': SL, 'Ro': RO, 'Ri': RI, 'theta': TH, 'ox': OX, 'oy': OY}},
              open(os.path.join(pr.out, 'scene.json'), 'w'))
    print('cup ok', round(SL, 2), round(RO, 2), round(RI, 2), round(math.degrees(TH), 2), round(SW, 1), round(SH, 1))
