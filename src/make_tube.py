"""Cupcake window box and bento carton (parametric straight-tuck cartons): art, dielines, PDFs, textures, scene data."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import scenes as S
import render as R
import tubebox as TB
import geom as g
from ink import *


def sparkle_ink(x, y, r=2.2):
    return line([(x, y - r), (x, y + r)], 0.35, double=False) + line([(x - r, y), (x + r, y)], 0.35, double=False)

SPECS = {
    'cupbox': dict(title='Cupcake window box (4 cupcakes)', L=165.0, Wd=165.0, Hh=100.0, front_win=(24, 30, 22), lid_win=None),
    'bento': dict(title='Bento carton with lid window', L=230.0, Wd=160.0, Hh=60.0, front_win=None, lid_win=(36, 38)),
}


def make(key):
    sp = SPECS[key]
    P, I = TB.build(sp['L'], sp['Wd'], sp['Hh'], front_win=sp['front_win'], lid_win=sp['lid_win'])
    logo = R.logo_uri
    L, Wd, Hh = sp['L'], sp['Wd'], sp['Hh']

    def front(Wp, Hp):
        o = S.bgp(Wp, Hp)
        if key == 'cupbox':
            o += awning(8, 5, Wp - 16, 17, 10, 3)
            fw = sp['front_win']
            o += line(rect_pts(fw[0] - 3, fw[1] - 3, Wp - 2 * fw[0] + 6, Hp - fw[1] - fw[2] + 6, 8), 1.0, closed=True)
            o += hand('cupcakes', Wp / 2, Hp - 7, 8.6, CAVEAT, COCOA, rot=-1)
            o += vine([(8, Hp - 4), (6, Hp - 30), (9, 30)], 4, [(7, 60, 2.2)], 41) + vine([(Wp - 8, Hp - 4), (Wp - 6, Hp - 30), (Wp - 9, 30)], 4, [(Wp - 7, 60, 2.2)], 43)
        else:
            lw = 46
            o += f'<image x="{(Wp-lw)/2:.2f}" y="5" width="{lw}" height="{lw*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
            o += hand('bento', Wp / 2, Hp - 17, 8, CAVEAT, COCOA)
            o += gingham(0, Hp - 8, Wp, 12)
        return o + grain(Wp, Hp)

    def side(Wp, Hp):
        o = S.bgp(Wp, Hp) + gingham(0, Hp - 18, Wp, 22)
        o += shape(rect_pts(Wp / 2 - 30, Hp * 0.22, 60, Hp * 0.34, 3), CREAM, 0.7)
        o += cupcake(Wp / 2, Hp * 0.22 + Hp * 0.17, 1.7, BLUSH) + hand('made with love', Wp / 2, Hp * 0.22 + Hp * 0.29, 6.2)
        for sx in (Wp / 2 - 44, Wp / 2 + 44):
            o += cherry(sx, Hp * 0.36, 2.2) + sparkle_ink(sx + (8 if sx < Wp / 2 else -8), Hp * 0.28, 2.4)
        return o + grain(Wp, Hp)

    def backp(Wp, Hp):
        o = S.bgp(Wp, Hp) + gingham(0, Hp - 18, Wp, 22)
        ttl, sub = ('4 fresh cupcakes', 'baked this morning') if key == 'cupbox' else ('a little lunch', 'packed with love')
        o += f'<image x="{Wp/2-26:.2f}" y="{Hp*0.05:.2f}" width="52" height="{52*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
        o += hand(ttl, Wp / 2, Hp * 0.36, 10, CAVEAT, COCOA) + hand(sub, Wp / 2, Hp * 0.36 + 13, 7.6, CAVEAT, COCOA)
        o += cherry(Wp / 2 - 40, Hp * 0.36 + 28, 3) + strawberry(Wp / 2 + 40, Hp * 0.36 + 28, 3.8)
        return o + grain(Wp, Hp)

    def lid_cupbox(Wp, Hp):
        o = S.bgp(Wp, Hp, BLUSH) + hatch(0, 0, Wp, Hp, 2.6, 45, COCOA, .08)
        o += gingham(0, 0, Wp, 16, cell=5.5) + gingham(0, Hp - 16, Wp, 16, cell=5.5)
        o += gingham(0, 0, 16, Hp, cell=5.5) + gingham(Wp - 16, 0, 16, Hp, cell=5.5)
        px, py, pw, ph = 20, 20, Wp - 40, Hp - 40
        o += shape(rect_pts(px, py, pw, ph, 12), CREAM, 1.1)
        o += line(rect_pts(px + 3.5, py + 3.5, pw - 7, ph - 7, 9), 0.4, closed=True, double=False, dash='1.4 1.2')
        cx = Wp / 2
        o += f'<image x="{cx-48:.2f}" y="{py+8:.2f}" width="96" height="{96*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
        o += hand('four fresh cupcakes', cx, py + 82, 11.5, CAVEAT, COCOA, rot=-2)
        yb = Hp - 36
        for i, ccx in enumerate([cx - 39, cx - 13, cx + 13, cx + 39]):
            o += cupcake(ccx, yb, 2.55, BLUSH if i % 2 == 0 else BABY)
        o += line([(cx - 52, yb + 3.5), (cx + 52, yb + 3.5)], 0.45)
        for (sx, sy) in ((px + 14, py + 16), (Wp - px - 14, py + 20), (px + 12, py + 60), (Wp - px - 12, py + 58)):
            o += sparkle_ink(sx, sy, 3.0)
        for (rx, ry) in ((px + 13, Hp - 44), (Wp - px - 13, Hp - 44)):
            o += rose(rx, ry, 4.2) + leaf(rx - 5, ry + 3, -30, 4) + leaf(rx + 5, ry + 3, 210, 4)
        o += cherry(px + 14, py + 40, 2.6) + strawberry(Wp - px - 14, py + 40, 3.2)
        return o + grain(Wp, Hp)

    def lid(Wp, Hp):
        if key == 'cupbox':
            return lid_cupbox(Wp, Hp)
        o = S.bgp(Wp, Hp, BABY)
        o += line(rect_pts(5, 5, Wp - 10, Hp - 10, 6), 0.7, closed=True) + line(rect_pts(8, 8, Wp - 16, Hp - 16, 4), 0.3, closed=True, double=False, dash='1.2 1.1')
        lw = 44 if key == 'bento' else 78
        if key == 'bento':
            o += f'<image x="{(Wp-lw)/2:.2f}" y="5" width="{lw}" height="{lw*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
            o += hand('made with love', Wp / 2, Hp - 14, 8.4, CAVEAT, COCOA)
        else:
            o += f'<image x="{(Wp-lw)/2:.2f}" y="{Hp/2-lw*0.333-4:.2f}" width="{lw}" height="{lw*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
            o += hand('homemade bakes, made with love', Wp / 2, Hp - 24, 8, CAVEAT, COCOA)
        return o + grain(Wp, Hp)

    def outer(n, p):
        Wp, Hp = p.art['size']
        if n == 'F': return front(Wp, Hp)
        if n in ('SR', 'SL'): return side(Wp, Hp)
        if n == 'K': return backp(Wp, Hp)
        if n == 'TTT': return lid(Wp, Hp)
        if n == 'TTB': return S.bgp(Wp, Hp, BLUSH) + hatch(0, 0, Wp, Hp, 2.2, 45, COCOA, .12) + grain(Wp, Hp)
        if p.role == 'dust': return S.bgp(Wp, Hp, BABY) + grain(Wp, Hp)
        if p.role == 'tongue': return S.bgp(Wp, Hp, BLUSH)
        return ''

    def inner(n, p):
        Wp, Hp = p.art['size']
        if n == 'TTT' and key == 'cupbox':
            return S.bgp(Wp, Hp, BABY) + hand('enjoy!', Wp / 2, Hp / 2 + 4, 12, CAVEAT, COCOA, rot=-3) + grain(Wp, Hp)
        return S.bgp(Wp, Hp, '#FFFDFD') if n else ''

    SW, SH, YB0, TD, GW = I['SW'], I['SH'], I['YB0'], I['TD'], I['GW']
    dm = R.dim_h(0, L, SH + 6, 0, L) + R.dim_h(L, L + Wd, SH + 6, 0, Wd) + R.dim_h(0, SW, -8, 0, SW)
    dm += R.dim_v(-4, YB0, YB0 + Hh, -6, Hh) + R.dim_v(-4, 0, SH, -16, SH) + R.dim_v(L + Wd + L, YB0 - TD, YB0, 8, TD)
    dm += R.dim_h(L + Wd + L + Wd, SW, YB0 + Hh / 2 + 8, 14, GW)
    pr = R.Product(key, sp['title'], P, SW, SH, outer, inner, 'tube', dm)
    M = g.fold_matrices(P)
    fp = np.vstack([(M[n] @ np.array([x, -Y, 0, 1.0]))[:3] for n in ('F', 'SR', 'K', 'SL') for x, Y in P[n].ring()])
    shift = [-(fp[:, 0].min() + fp[:, 0].max()) / 2, -fp[:, 1].min(), -(fp[:, 2].min() + fp[:, 2].max()) / 2]
    return pr, shift


if __name__ == '__main__':
    for k in sys.argv[1:] or list(SPECS):
        pr, shift = make(k)
        R.build_outputs(pr, shift)
        open(os.path.join(pr.out, 'dieline_dim.svg'), 'w', encoding='utf-8').write(R.dimmed_dieline(pr, pr.dims))
        print(k, 'ok', pr.SW, pr.SH)
