"""Sticker sheet (A5 landscape, kiss-cut): 12 stickers, hand-inked art, die-cut paths in mm.
Outputs assets/stickers/: sheet.svg (art + cut lines, viewer), sticker_sheet_art.pdf, sticker_sheet_cut.pdf, stickers.dxf, stickers.json."""
import os, sys, math, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import pymupdf as fz
import ezdxf
import render as R
import scenes as S
from ink import *

OUT = os.path.join(R.SITE, 'assets', 'stickers')
os.makedirs(OUT, exist_ok=True)
logo = R.logo_uri
NS = 'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
SW, SH = 210.0, 148.0


def limg(cx, cy, w):
    return f'<image x="{cx-w/2:.2f}" y="{cy-w*0.333:.2f}" width="{w}" height="{w*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'


# ---- shape specs: path d (svg) + polyline pts (dxf)
def sp_circle(x, y, d):
    r = d / 2
    return dict(kind='circle', x=x, y=y, w=d, h=d, d=f'M0,{r} A{r},{r} 0 1 0 {d},{r} A{r},{r} 0 1 0 0,{r} Z', c=(x + r, y + r), r=r)


def sp_oval(x, y, w, h):
    a, b = w / 2, h / 2
    return dict(kind='oval', x=x, y=y, w=w, h=h, d=f'M0,{b} A{a},{b} 0 1 0 {w},{b} A{a},{b} 0 1 0 0,{b} Z',
                pts=[(x + a + a * math.cos(2 * math.pi * i / 72), y + b + b * math.sin(2 * math.pi * i / 72)) for i in range(72)])


def sp_rr(x, y, w, h, r):
    d = f'M{r},0 H{w-r} A{r},{r} 0 0 1 {w},{r} V{h-r} A{r},{r} 0 0 1 {w-r},{h} H{r} A{r},{r} 0 0 1 0,{h-r} V{r} A{r},{r} 0 0 1 {r},0 Z'
    pts = []
    for (cx, cy, a0) in ((w - r, r, -90), (w - r, h - r, 0), (r, h - r, 90), (r, r, 180)):
        for i in range(9):
            a = math.radians(a0 + 90 * i / 8)
            pts.append((x + cx + r * math.cos(a), y + cy + r * math.sin(a)))
    return dict(kind='rrect', x=x, y=y, w=w, h=h, d=d, pts=pts)


def sp_scal(x, y, d, n=14):
    """scalloped circle: arcs between n points on radius R0"""
    r = d / 2 - d * 0.045
    pts = [(r + r * math.cos(2 * math.pi * i / n) + d * .045, r + r * math.sin(2 * math.pi * i / n) + d * .045) for i in range(n + 1)]
    chord = 2 * r * math.sin(math.pi / n)
    br = chord * 0.58
    ds = f'M{pts[0][0]:.2f},{pts[0][1]:.2f} ' + ' '.join(f'A{br:.2f},{br:.2f} 0 0 1 {px:.2f},{py:.2f}' for px, py in pts[1:]) + ' Z'
    dxf = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = mx - d / 2, my - d / 2
        nl = math.hypot(nx, ny) or 1
        sag = br - math.sqrt(max(br * br - (chord / 2) ** 2, 0))
        for t in range(7):
            u = t / 6
            px, py = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
            k = math.sin(math.pi * u) * (chord / 2) * 0.62
            dxf.append((x + px + nx / nl * k, y + py + ny / nl * k))
    return dict(kind='scal', x=x, y=y, w=d, h=d, d=ds, pts=dxf)


def cut_pts(s):
    if s['kind'] == 'circle':
        r = s['r']
        return [(s['c'][0] + r * math.cos(2 * math.pi * i / 90), s['c'][1] + r * math.sin(2 * math.pi * i / 90)) for i in range(90)]
    return s['pts']


# ---- art for each sticker (local coords 0..w, 0..h)
def a_logo(w, h):
    return S.bgp(w, h, CREAM) + line(ellipse_pts(w / 2, h / 2, w / 2 - 2.6, h / 2 - 2.6, 30), 0.7, closed=True) + line(ellipse_pts(w / 2, h / 2, w / 2 - 4.6, h / 2 - 4.6, 30), 0.3, closed=True, double=False, dash='1.1 1') + limg(w / 2, h / 2 + .6, w * .68)


def a_thanks(w, h):
    o = S.bgp(w, h, BABY) + line(ellipse_pts(w / 2, h / 2, w / 2 - 5, h / 2 - 5, 30), 0.35, closed=True, double=False, dash='1.1 1')
    return o + hand('thank', w / 2, h / 2 - 4, 10, CAVEAT, COCOA, rot=-6) + hand('you!', w / 2, h / 2 + 7, 10, CAVEAT, COCOA, rot=-6) + cherry(w / 2, h - 9, 2)


def a_cupcake(w, h):
    o = S.bgp(w, h, BLUSH) + hatch(0, 0, w, h, 2.4, 45, COCOA, .10)
    o += shape(ellipse_pts(w / 2, h / 2, w / 2 - 4, h / 2 - 4, 30), CREAM, 0.6)
    return o + cupcake(w / 2, h / 2 + 6, 2.0, BLUSH) + hand('fresh', w / 2, h - 7.2, 5.4, CAVEAT, COCOA)


def a_cherry(w, h):
    o = S.bgp(w, h, CREAM) + line(ellipse_pts(w / 2, h / 2, w / 2 - 2.4, h / 2 - 2.4, 30), 0.5, closed=True)
    return o + cherry(w / 2 - 5, h / 2 + 4, 4.6) + cherry(w / 2 + 5.5, h / 2 + 6, 3.8) + line([(w / 2 - 5, h / 2 - 1), (w / 2, h / 2 - 9), (w / 2 + 5.5, h / 2 + 2)], 0.5, double=False)


def a_fresh(w, h):
    o = S.bgp(w, h, BABY) + line(ellipse_pts(w / 2, h / 2, w / 2 - 2.5, h / 2 - 2.5, 40), 0.6, closed=True)
    o += hand('fresh baked', w / 2, h / 2 - 1, 8.2, CAVEAT, COCOA) + hand('daily', w / 2, h / 2 + 8.5, 7, CAVEAT, COCOA)
    return o + cherry(8, h / 2 + 1, 1.8) + strawberry(w - 8.5, h / 2, 2.4)


def a_handmade(w, h):
    o = S.bgp(w, h, CREAM) + line(rect_pts(2.4, 2.4, w - 4.8, h - 4.8, 4), 0.55, closed=True) + line(rect_pts(4.4, 4.4, w - 8.8, h - 8.8, 3), 0.28, closed=True, double=False, dash='1.1 1')
    return o + hand('handmade', w / 2, h / 2 + 2, 11, CAVEAT, COCOA, rot=-2) + hand('with love', w / 2, h / 2 + 11, 6.5, CAVEAT, COCOA, rot=-2)


def a_seal(w, h):
    o = S.bgp(w, h, BLUSH) + line(ellipse_pts(w / 2, h / 2, w / 2 - 4, h / 2 - 4, 30), 0.35, closed=True, double=False, dash='1 1')
    o += rose(w / 2, h / 2 - 5, 4.6, ROSE) + hand('sealed', w / 2, h / 2 + 6.5, 5.6, CAVEAT, COCOA) + hand('with love', w / 2, h / 2 + 11, 4.4, CAVEAT, COCOA)
    return o


def a_straw(w, h):
    o = S.bgp(w, h, BABY) + line(ellipse_pts(w / 2, h / 2, w / 2 - 2.2, h / 2 - 2.2, 30), 0.45, closed=True)
    return o + strawberry(w / 2, h / 2 + 1, 6.4)


def a_madewith(w, h):
    o = S.bgp(w, h, BLUSH) + hatch(0, 0, w, h, 2.2, 45, COCOA, .12)
    return o + hand('made with love', w / 2, h / 2 + 2, 5.4, CAVEAT, COCOA) + cherry(8.5, h / 2 + .5, 1.3) + cherry(w - 8.5, h / 2 + .5, 1.3)


def a_heart(w, h):
    o = S.bgp(w, h, CREAM) + line(ellipse_pts(w / 2, h / 2, w / 2 - 2, h / 2 - 2, 40), 0.5, closed=True)
    hp = []
    for i in range(41):
        t = 2 * math.pi * i / 40
        hp.append((w / 2 + 0.78 * 16 * math.sin(t) ** 3 * (w / 70), h / 2 - 1 - 0.78 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * (w / 70)))
    return o + shape(hp, ROSE, 0.55) + hand('xoxo', w / 2, h / 2 + 2, 6, CAVEAT, CREAM)


def a_door(w, h):
    o = S.bgp(w, h, BABY) + line(rect_pts(2.2, 2.2, w - 4.4, h - 4.4, 3.5), 0.5, closed=True)
    return o + hand('open', w / 2, h / 2 + 1.2, 10, CAVEAT, COCOA, rot=-3) + hand('daily', w / 2, h / 2 + 8.4, 4.6, CAVEAT, COCOA)


def a_cake(w, h):
    o = S.bgp(w, h, CREAM) + line(ellipse_pts(w / 2, h / 2, w / 2 - 2, h / 2 - 2, 30), 0.5, closed=True)
    return o + cake(w / 2, h / 2 + 6, 18, 2, 6)


STICKERS = [
    ('Round logo', sp_circle(8, 8, 50), a_logo), ('Thank you', sp_scal(64, 8, 44), a_thanks),
    ('Cupcake', sp_circle(114, 8, 40), a_cupcake), ('Cherries', sp_circle(160, 8, 34), a_cherry),
    ('Fresh baked daily', sp_oval(8, 64, 62, 36), a_fresh), ('Handmade', sp_rr(76, 64, 52, 36, 7), a_handmade),
    ('Sealed with love', sp_scal(134, 64, 36, 12), a_seal), ('Strawberry', sp_circle(174, 64, 28), a_straw),
    ('Made with love strip', sp_rr(8, 108, 50, 24, 12), a_madewith), ('Heart', sp_oval(64, 108, 40, 28), a_heart),
    ('Open daily', sp_rr(110, 108, 36, 24, 5), a_door), ('Cake', sp_circle(152, 108, 30), a_cake),
]


def build():
    art, cuts, dims, viewer = '', '', '', ''
    meta = []
    for i, (name, s, fn) in enumerate(STICKERS):
        cid = f'stk{i}'
        a = fn(s['w'], s['h']) + grain(s['w'], s['h'], uid=f'gs{i}')
        one = (f'<svg {NS} viewBox="-2.4 -2.4 {s["w"]+4.8:.2f} {s["h"]+4.8:.2f}"><defs><clipPath id="o{i}"><path d="{s["d"]}"/></clipPath></defs>'
               f'<path d="{s["d"]}" fill="#fff" stroke="#fff" stroke-width="4.4" stroke-linejoin="round"/><g clip-path="url(#o{i})">{a}</g>'
               f'<path d="{s["d"]}" fill="none" stroke="rgba(139,74,58,.18)" stroke-width=".25"/></svg>')
        open(os.path.join(OUT, f's{i}.svg'), 'w', encoding='utf-8').write(one)
        viewer += (f'<g class="stk" data-i="{i}" data-name="{name}" data-w="{s["w"]:.1f}" data-h="{s["h"]:.1f}"><g transform="translate({s["x"]} {s["y"]})"><defs><clipPath id="v{i}"><path d="{s["d"]}"/></clipPath></defs>'
                   f'<path d="{s["d"]}" fill="none" stroke="rgba(0,0,0,0)" stroke-width="3"/><g clip-path="url(#v{i})">{a}</g></g></g>')
        art += (f'<g transform="translate({s["x"]} {s["y"]})"><defs><clipPath id="{cid}"><path d="{s["d"]}"/></clipPath></defs>'
                f'<g clip-path="url(#{cid})">{a}</g></g>')
        cuts += f'<path transform="translate({s["x"]} {s["y"]})" d="{s["d"]}"/>'
        meta.append({'name': name, 'x': s['x'], 'y': s['y'], 'w': round(s['w'], 1), 'h': round(s['h'], 1)})
    return art, cuts, meta, viewer


def main():
    art, cuts, meta, viewer = build()
    sheet = f'<rect x="0" y="0" width="{SW}" height="{SH}" fill="#fff"/>'
    cutg = f'<g class="cutlayer" fill="none" stroke="#EC008C" stroke-width="0.3" stroke-dasharray="1.6 1">{cuts}</g>'
    sheet_border = f'<rect x="0" y="0" width="{SW}" height="{SH}" fill="none" stroke="#bdb" stroke-width=".25"/>'
    pad = 10
    vb = f'viewBox="{-pad} {-pad} {SW+2*pad} {SH+2*pad}"'
    # viewer svg (web, with cut overlay and sheet edge)
    open(os.path.join(OUT, 'sheet.svg'), 'w', encoding='utf-8').write(f'<svg {NS} {vb} class="item-svg" data-w="{SW}" data-h="{SH}">{sheet}<g id="art">{viewer}</g>{cutg}{sheet_border}</svg>')
    # print files
    pr = R.Product('stickers', 'Sticker sheet', {}, SW, SH, None, None, 'tube', '')
    pr.out = OUT
    os.makedirs(os.path.join(OUT, '_tmp'), exist_ok=True)
    pa = R.svg_page(pr, sheet + art)
    pc = R.svg_page(pr, sheet + art + cutg)
    R.to_pdf(pr, pa, 'sticker_art').save(os.path.join(OUT, 'sticker_sheet_art.pdf'))
    R.to_pdf(pr, pc, 'sticker_cut').save(os.path.join(OUT, 'sticker_sheet_cutline.pdf'))
    # dxf (Y up)
    d = ezdxf.new('R2010')
    d.header['$INSUNITS'] = 4
    d.layers.add('CUT', color=6)
    d.layers.add('SHEET', color=8)
    d.layers.add('INFO', color=8)
    m = d.modelspace()
    Y = lambda p: (p[0], SH - p[1])
    m.add_lwpolyline([Y((0, 0)), Y((SW, 0)), Y((SW, SH)), Y((0, SH))], close=True, dxfattribs={'layer': 'SHEET'})
    for name, s, fn in STICKERS:
        if s['kind'] == 'circle':
            m.add_circle((s['c'][0], SH - s['c'][1]), s['r'], dxfattribs={'layer': 'CUT'})
        else:
            m.add_lwpolyline([Y(p) for p in s['pts']], close=True, dxfattribs={'layer': 'CUT'})
    m.add_text(f'Mona\'s Baking sticker sheet | {SW:.0f} x {SH:.0f} mm | kiss-cut paths | DRAFT - not validated by a printer',
               dxfattribs={'layer': 'INFO', 'height': 3}).set_placement((0, -8))
    d.saveas(os.path.join(OUT, 'stickers.dxf'))
    json.dump({'sheet': [SW, SH], 'stickers': meta}, open(os.path.join(OUT, 'stickers.json'), 'w'), indent=1)
    print('stickers ok', len(meta))


if __name__ == '__main__':
    main()
