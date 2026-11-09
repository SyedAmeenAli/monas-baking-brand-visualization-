"""Flat print items (stickers, seal, tag, cards, label, ribbon, tissue) + wide hero storefront. Design sizes - to confirm with printer."""
import os, sys, math, base64
sys.path.insert(0, os.path.dirname(__file__))
from ink import *
import ink as K
import scenes as S
import render as R

OUT = os.path.join(R.SITE, 'assets', 'items')
os.makedirs(OUT, exist_ok=True)
logo = R.logo_uri
NS = 'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'


def logo_img(cx, cy, w):
    return f'<image x="{cx-w/2:.2f}" y="{cy-w*0.333:.2f}" width="{w}" height="{w*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'


def wrap(key, w, h, art, cutd, dims, title, spec, pad=14):
    """cutd: SVG path d of die-cut. Artwork is clipped to cut + 2 mm bleed (bleed via stroke)."""
    cid = f'cl_{key}'
    body = (f'<defs><clipPath id="{cid}"><path d="{cutd}"/></clipPath></defs>'
            f'<g clip-path="url(#{cid})">{art}</g>'
            f'<path d="{cutd}" fill="none" stroke="#EC008C" stroke-width="0.3" stroke-dasharray="1.6 1" class="cutline"/>'
            f'<g class="dims">{dims}</g>')
    svg = f'<svg {NS} viewBox="{-pad} {-pad} {w+2*pad} {h+2*pad}" class="item-svg" data-w="{w}" data-h="{h}">{body}</svg>'
    open(os.path.join(OUT, key + '.svg'), 'w', encoding='utf-8').write(svg)
    return {'key': key, 'title': title, 'w': w, 'h': h, 'spec': spec}


def rr(x, y, w, h, r):
    return f'M{x+r},{y} H{x+w-r} A{r},{r} 0 0 1 {x+w},{y+r} V{y+h-r} A{r},{r} 0 0 1 {x+w-r},{y+h} H{x+r} A{r},{r} 0 0 1 {x},{y+h-r} V{y+r} A{r},{r} 0 0 1 {x+r},{y} Z'


def circ(cx, cy, r):
    return f'M{cx-r},{cy} A{r},{r} 0 1 0 {cx+r},{cy} A{r},{r} 0 1 0 {cx-r},{cy} Z'


def scallop_circle(cx, cy, r, n=16, bump=1.7):
    pts = []
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        if i == 0:
            pts.append(f'M{x0:.2f},{y0:.2f}')
        pts.append(f'A{bump*r*math.sin(math.pi/n)*1.0:.2f},{bump*r*math.sin(math.pi/n)*1.0:.2f} 0 0 1 {x1:.2f},{y1:.2f}')
    return ' '.join(pts) + ' Z'


def whisk(x, y, h):
    s = h / 40
    o = ''
    for rx in (7, 4.5, 2):
        o += line(ellipse_pts(x, y + 8 * s, rx * s, 12 * s, 14), 0.4, closed=True, double=False)
    o += line([(x, y + 20 * s), (x, y + 30 * s)], 0.5, double=False) + shape(rect_pts(x - 1.8 * s, y + 30 * s, 3.6 * s, 10 * s, 1.6 * s), BLUSH, 0.4)
    return o


def items():
    res = []
    # ---- round logo sticker 50 mm
    a = S.bgp(50, 50, CREAM) + line(ellipse_pts(25, 25, 22.5, 22.5, 28), 0.7, closed=True) + line(ellipse_pts(25, 25, 20.6, 20.6, 28), 0.3, closed=True, double=False, dash='1.1 1')
    a += logo_img(25, 25.5, 34) + grain(50, 50)
    res.append(wrap('sticker_round', 50, 50, a, circ(25, 25, 25), R.dim_h(0, 50, 50, 8, 50) + R.dim_v(0, 0, 50, -8, 50), 'Round logo sticker', 'Die-cut circle, 50 mm. Closes boxes, seals bags.'))
    # ---- scalloped thank-you sticker 45 mm
    a = S.bgp(45, 45, BABY) + line(ellipse_pts(22.5, 22.5, 18.5, 18.5, 28), 0.35, closed=True, double=False, dash='1.1 1')
    a += hand('thank', 22.5, 17.5, 9, CAVEAT, COCOA, rot=-5) + hand('you!', 22.5, 27, 9, CAVEAT, COCOA, rot=-5) + cherry(22.5, 36, 1.8) + grain(45, 45)
    res.append(wrap('sticker_thanks', 45, 45, a, scallop_circle(22.5, 22.5, 21.2, 16, 1.55), R.dim_h(0, 45, 45, 8, 45) + R.dim_v(0, 0, 45, -8, 45), 'Thank-you sticker', 'Scalloped die-cut, 45 mm.'))
    # ---- tamper seal 18 x 60
    a = S.bgp(60, 18, BLUSH) + hatch(0, 0, 60, 18, 2.2, 45, COCOA, .12) + hand('made with love', 30, 11, 7.2, CAVEAT, COCOA) + cherry(8, 9.5, 1.8) + cherry(52, 9.5, 1.8) + grain(60, 18)
    res.append(wrap('seal', 60, 18, a, rr(0, 0, 60, 18, 9), R.dim_h(0, 60, 18, 8, 60) + R.dim_v(60, 0, 18, 8, 18), 'Box tamper seal', 'Strip seal 60 x 18 mm, rounded ends.'))
    # ---- tag 50 x 90 with hole
    cut = f'M10,0 H40 L50,10 V90 H0 V10 Z'
    a = S.bgp(50, 90, CREAM) + line(rect_pts(3, 3, 44, 84, 3), 0.4, closed=True, double=False, dash='1.2 1.1')
    a += hand('Happy', 25, 36, 11, CAVEAT, COCOA, rot=-4) + hand('Birthday!', 25, 48, 11, CAVEAT, COCOA, rot=-4) + cake(25, 78, 22, 2, 7) + vine([(8, 62), (6, 50), (8, 40)], 3, [(7, 55, 1.7)], 41)
    a += f'<circle cx="25" cy="9" r="3" fill="#fff" stroke="{COCOA}" stroke-width=".5"/>' + grain(50, 90)
    res.append(wrap('tag', 50, 90, a, cut + f' M25,6 a3,3 0 1 0 0.01,0 Z', R.dim_h(0, 50, 90, 8, 50) + R.dim_v(50, 0, 90, 8, 90) + R.dim_v(0, 0, 9, -6, 9), 'Gift tag', 'Birthday tag 50 x 90 mm, 6 mm punched hole, ribbon-tied.'))
    # ---- thank-you card A6 105 x 148
    a = S.bgp(105, 148, CREAM)
    a += f'<g transform="translate(5 8) scale(0.78)">{S.front(127, 152.4, logo)}</g>'.replace('', '')
    a += hand('Thank you!', 52.5, 124, 15, CAVEAT, COCOA, rot=-2) + hand('for supporting', 52.5, 134, 7.8, CAVEAT, COCOA) + hand("Mona's Baking", 52.5, 142, 8.6, CAVEAT, COCOA)
    res.append(wrap('card_a6', 105, 148, a, rr(0, 0, 105, 148, 2.5), R.dim_h(0, 105, 148, 8, 105) + R.dim_v(105, 0, 148, 8, 148), 'Thank-you card (A6)', 'A6 105 x 148 mm, tucked into every box.'))
    # ---- business card 90 x 50 (front) - contact placeholders from the concept sheet
    a = S.bgp(90, 50, BABY) + logo_img(45, 25, 56) + grain(90, 50)
    res.append(wrap('bizcard', 90, 50, a, rr(0, 0, 90, 50, 2), R.dim_h(0, 90, 50, 8, 90) + R.dim_v(90, 0, 50, 8, 50), 'Business card', '90 x 50 mm. Contact details on the back are placeholders.'))
    # ---- product label 60 x 40
    a = S.bgp(60, 40, CREAM) + line(rect_pts(2.5, 2.5, 55, 35, 3), 0.6, closed=True)
    a += logo_img(30, 11.5, 24)
    for i, t in enumerate(['product', 'flavour', 'made on', 'best before']):
        yy = 22 + i * 4.6
        a += hand(t, 6, yy, 3.6, CAVEAT, COCOA, anchor='start') + line([(6 + 16, yy + 0.4), (54, yy + 0.4)], 0.22, double=False)
    a += grain(60, 40)
    res.append(wrap('label', 60, 40, a, rr(0, 0, 60, 40, 3.5), R.dim_h(0, 60, 40, 8, 60) + R.dim_v(60, 0, 40, 8, 40), 'Product label', '60 x 40 mm, hand-filled fields.'))
    # ---- ribbon 25 x 150
    a = gingham(0, -2, 25, 156, cell=5) + line([(0.6, 0), (0.6, 150)], 0.3, double=False) + line([(24.4, 0), (24.4, 150)], 0.3, double=False) + grain(25, 150)
    res.append(wrap('ribbon', 25, 150, a, f'M0,0 H25 V150 H0 Z', R.dim_h(0, 25, 150, 8, 25) + R.dim_v(25, 0, 150, 8, 150), 'Gingham ribbon', '25 mm wide, cut to length. Woven or printed grosgrain.'))
    # ---- tissue tile 80 x 80
    a = S.bgp(80, 80, CREAM)
    for (cx, cy, kind) in ((18, 18, 'c'), (58, 14, 'w'), (40, 44, 'k'), (14, 64, 'w'), (66, 62, 'c'), (44, 74, 'h')):
        if kind == 'c':
            a += cupcake(cx, cy + 6, 1.15, BLUSH)
        elif kind == 'w':
            a += whisk(cx, cy - 4, 26)
        elif kind == 'k':
            a += cake(cx, cy + 8, 20, 2, 6.5)
        else:
            a += cherry(cx, cy, 2.4) + cherry(cx + 6, cy + 1, 2.0)
    for (sx, sy) in ((36, 8), (8, 42), (72, 40), (28, 66), (62, 36), (50, 20)):
        a += sparkle_ink(sx, sy)
    a += grain(80, 80)
    res.append(wrap('tissue', 80, 80, a, 'M0,0 H80 V80 H0 Z', R.dim_h(0, 80, 80, 8, 80) + R.dim_v(80, 0, 80, 8, 80), 'Tissue paper repeat', 'Seamless 80 mm tile; printed sheet 500 x 700 mm (design size).'))
    return res


def sparkle_ink(x, y, r=2.2):
    return line([(x, y - r), (x, y + r)], 0.35, double=False) + line([(x - r, y), (x + r, y)], 0.35, double=False)


def hero_layers():
    """Hero storefront split into depth layers (back wall, awning, sign, floor) so the page can parallax them."""
    W, H = 320, 170
    L = {}
    o = ''
    wx, wy, ww, wh = 50, 90, 128, 52
    ins = curtain(wx + 1, wy + 1, 18, 38, True) + curtain(wx + ww - 1, wy + 1, 18, 38, False)
    ins += tiered_stand(wx + 36, wy + wh - 12, 34) + cakestand(wx + 92, wy + wh - 12, 40) + cake(wx + 92, wy + wh - 14.5, 32, 3, 8.5) + dome(wx + 92, wy + wh - 14.4, 38, 26)
    o += window_scene(wx, wy, ww, wh, ins, arched=False)
    dx, dy, dw, dh = 205, 94, 50, 66
    o += shape(arch_pts(dx, dy, dw, dh), CREAM, 1.0) + line(arch_pts(dx + 3, dy + 3, dw - 6, dh - 3), 0.4, closed=True, double=False)
    for (px, py) in ((dx + 8, dy + 26), (dx + dw - 21, dy + 26), (dx + 8, dy + 46), (dx + dw - 21, dy + 46)):
        o += shape(rect_pts(px, py, 13, 15, 1.5), BLUSH, 0.5)
    o += shape(rect_pts(dx + 12, dy + 12, 26, 11, 2), CREAM, 0.6) + hand('open', dx + 25, dy + 20, 8, CAVEAT, COCOA)
    for px in (14, 280):
        o += shape(rect_pts(px, 86, 14, 74), CREAM, 0.8)
        for yy in range(92, 156, 7):
            o += line([(px + 2, yy), (px + 12, yy)], 0.25, double=False, op=.6)
        o += shape(rect_pts(px - 2, 82, 18, 4), BLUSH, 0.6)
    o += vine([(21, 160), (19, 140), (24, 120), (18, 100), (22, 88)], 10, [(20, 132, 3), (23, 108, 2.6)], 3)
    o += vine([(287, 160), (289, 140), (284, 120), (290, 100), (286, 88)], 10, [(288, 128, 3), (285, 104, 2.6)], 5)
    o += vine([(262, 160), (260, 140), (264, 124)], 5, [(261, 144, 2.4)], 7)
    L['back'] = f'<rect x="-6" y="-6" width="{W+12}" height="{H+12}" fill="{BABY}"/>' + o + grain(W, H, 'hb')
    L['flowers'] = flower_box(wx - 2, wy + wh + 2, ww + 4, 12)
    L['awning'] = awning(30, 50, 260, 26, 21, 9) + bunting(6, W - 6, 86, 26, 5)
    L['lanternL'] = lantern(34, 84, 1.0)
    L['lanternR'] = lantern(W - 34, 84, 1.0)
    sg = shape(rect_pts(70, 6, 180, 38, 4), CREAM, 1.1) + line(rect_pts(73.5, 9.5, 173, 31, 3), 0.4, closed=True, double=False)
    sg += f'<image x="{160-34}" y="9" width="68" height="{68*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
    sg += hand('homemade bakes,', 100, 27, 9, CAVEAT, COCOA) + hand('made with love', 220, 27, 9, CAVEAT, COCOA)
    L['sign'] = sg
    L['floor'] = gingham(0, 154, W, 22, cell=6.5)
    return L, W, H


def hero():
    L, W, H = hero_layers()
    return ''.join(L[k] for k in ('back', 'flowers', 'lanternL', 'lanternR', 'awning', 'sign', 'floor')), W, H


if __name__ == '__main__':
    import json
    res = items()
    h, W, H = hero()
    open(os.path.join(OUT, 'hero.svg'), 'w', encoding='utf-8').write(f'<svg {NS} viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax meet">{h}</svg>')
    L, W, H = hero_layers()
    for k, v in L.items():
        open(os.path.join(OUT, f'hero_{k}.svg'), 'w', encoding='utf-8').write(f'<svg {NS} viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax meet">{v}</svg>')
    json.dump(res, open(os.path.join(OUT, 'items.json'), 'w'), indent=1)
    print(len(res), 'items + hero')
