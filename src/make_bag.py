"""Build the gusseted paper shopping bag: hand-inked art, dieline, PDFs, textures, 3D scene data (+ twisted-paper cords)."""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import scenes as S
import render as R
import bag as B
import geom as g
from ink import *

L, WD, H = B.L, B.WD, B.H
KEY = os.environ.get('MONA_BAG_KEY', 'bag')
TITLE = os.environ.get('MONA_BAG_TITLE', 'Paper shopping bag, 180 x 90 x 240 mm')
CORD = int(os.environ.get('MONA_BAG_CORD', '0xF2D6DC'), 16)
K = B.K


def sc(fn, Wp, Hp, logo):
    if abs(K - 1) < 1e-6:
        return fn(Wp, Hp, logo)
    return f'<g transform="scale({K:.4f})">{fn(Wp / K, Hp / K, logo)}</g>'


def front(Wp, Hp, logo):
    o = S.bgp(Wp, Hp)
    o += bunting(14, Wp - 14, 27, 9, 6)
    px, py, pw, ph = 26, 50, Wp - 52, 112
    o += shape(arch_pts(px, py, pw, ph), CREAM, 0.9)
    o += line(arch_pts(px + 6, py + 6, pw - 12, ph - 12), 0.35, closed=True, double=False, dash='1.4 1.2')
    lw = 96
    o += f'<image x="{(Wp-lw)/2:.2f}" y="{py+14:.2f}" width="{lw}" height="{lw*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
    o += hand('homemade bakes', Wp / 2, py + 83, 10.4, CAVEAT, COCOA) + hand('made with love', Wp / 2, py + 96, 10.4, CAVEAT, COCOA)
    o += vine([(12, 206), (10, 170), (14, 132), (10, 96), (13, 58)], 8, [(11, 180, 3.2), (13.5, 124, 3.0), (11, 80, 2.8)], 11)
    o += vine([(Wp - 12, 206), (Wp - 10, 168), (Wp - 14, 128), (Wp - 10, 92), (Wp - 13, 58)], 8, [(Wp - 11, 176, 3.2), (Wp - 13.5, 116, 3.0), (Wp - 11, 76, 2.8)], 13)
    o += cupcake(44, 203, 1.5) + cake(Wp / 2, 203, 36, 2, 12) + cupcake(Wp - 44, 203, 1.5, BABY)
    o += gingham(0, 212, Wp, Hp - 212 + 4)
    return o + grain(Wp, Hp)


def back(Wp, Hp, logo):
    o = S.bgp(Wp, Hp, CREAM)
    cx, cy, R0 = Wp / 2, 112, 38
    rnd = random.Random(21)
    motifs = ('c', 's', 'r')
    k = 0
    for row, yy in enumerate(range(40, 204, 33)):
        for xx in range(22 + (row % 2) * 19, int(Wp) - 10, 38):
            if ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5 < R0 + 16:
                continue
            xj, yj = xx + rnd.uniform(-3, 3), yy + rnd.uniform(-3, 3)
            m = motifs[k % 3]; k += 1
            if m == 'c': o += cherry(xj, yj, 3.4)
            elif m == 's': o += strawberry(xj, yj, 4.2)
            else: o += leaf(xj - 5, yj + 2, 330, 6) + rose(xj, yj, 4.2, ROSE if k % 2 else BLUSH) + leaf(xj + 5, yj + 2, 210, 6)
    o += shape(ellipse_pts(cx, cy, R0 + 8, R0 + 8, 36), BABY, 0.9)
    o += stamp_round(cx, cy, R0, "mona's baking", '')
    o += hand('thank', cx, cy - 2, 15, CAVEAT, COCOA, rot=-4) + hand('you!', cx, cy + 14, 15, CAVEAT, COCOA, rot=-4)
    o += hand('baked fresh, made with love', Wp / 2, 190, 8.4, CAVEAT, COCOA)
    o += gingham(0, 212, Wp, Hp - 212 + 4)
    return o + grain(Wp, Hp)


def gusset(Wp, Hp, logo):
    o = S.bgp(Wp, Hp)
    o += vine([(10, 206), (7, 170), (12, 132), (8, 92), (11, 54)], 7, [(9, 160, 2.8), (10, 100, 2.6)], 15)
    o += vine([(Wp - 10, 206), (Wp - 7, 168), (Wp - 12, 128), (Wp - 8, 90), (Wp - 11, 56)], 7, [(Wp - 9, 150, 2.8), (Wp - 10, 96, 2.6)], 17)
    o += shape(rect_pts(Wp / 2 - 13, 38, 26, 134, 3), CREAM, 0.7)
    o += hand('fresh baked daily', Wp / 2, 107, 9.6, CAVEAT, COCOA, rot=-90)
    o += rose(Wp / 2, 28, 5.2) + leaf(Wp / 2 - 7, 31, 200, 6) + leaf(Wp / 2 + 7, 31, 340, 6)
    o += gingham(0, 212, Wp, Hp - 212 + 4)
    return o + grain(Wp, Hp)


def make():
    P = B.build()
    logo = R.logo_uri

    def outer(n, p):
        Wp, Hp = p.art['size']
        if n == 'F': return sc(front, Wp, Hp, logo)
        if n == 'K': return sc(back, Wp, Hp, logo)
        if n in ('SRa', 'SRb', 'SLa', 'SLb'): return sc(gusset, Wp, Hp, logo)
        if n == 'BF': return S.bgp(Wp, Hp, BLUSH) + hatch(0, 0, Wp, Hp, 2.2, 45, COCOA, .12) + hand("mona's baking", Wp / 2, Hp / 2 + 3, 9, CAVEAT, COCOA) + grain(Wp, Hp)
        return S.bgp(Wp, Hp, BLUSH) + grain(Wp, Hp)

    def inner(n, p):
        Wp, Hp = p.art['size']
        return S.bgp(Wp, Hp, '#FFFDFD')

    dm, y = '', B.SH + 6
    dm += R.dim_h(0, L, y, 0, L) + R.dim_h(L, B.xS1, y, 0, WD) + R.dim_h(B.xS1, B.xK1, y, 0, L)
    dm += R.dim_h(B.xK1, B.xL1, y, 0, WD) + R.dim_h(B.xL1, B.xG1, y, 0, B.GW)
    dm += R.dim_h(L / 2 - B.HOLE_DX, L / 2 + B.HOLE_DX, -6, 0, 2 * B.HOLE_DX)
    dm += R.dim_h(0, B.SW, -16, 0, B.SW)
    dm += R.dim_v(-4, 0, H, -6, H) + R.dim_v(-4, H, H + B.FD, -6, B.FD) + R.dim_v(-4, 0, B.SH, -16, B.SH)
    pr = R.Product(KEY, TITLE, P, B.SW, B.SH, outer, inner, 'tube', dm)
    M = g.fold_matrices(P)
    fp = np.vstack([(M[n] @ np.array([x, -Y, 0, 1.0]))[:3] for n in ('F', 'SRa', 'SRb', 'K', 'SLa', 'SLb') for x, Y in P[n].ring()])
    shift = [-(fp[:, 0].min() + fp[:, 0].max()) / 2, -fp[:, 1].min(), -(fp[:, 2].min() + fp[:, 2].max()) / 2]
    return pr, shift


def cord(xc):
    """Twisted-paper handle: out through one hole, over an arch above the top edge, back in through the other (panel-local x, Y, z)."""
    a, b, d = xc - B.HOLE_DX, xc + B.HOLE_DX, B.HOLE_DY
    k = K
    return [[a, d, -3 * k], [a, d, 3 * k], [a - 3 * k, -8 * k, 6 * k], [a + 6 * k, -48 * k, 8 * k], [xc, -72 * k, 8 * k], [b - 6 * k, -48 * k, 8 * k], [b + 3 * k, -8 * k, 6 * k], [b, d, 3 * k], [b, d, -3 * k]]


if __name__ == '__main__':
    pr, shift = make()
    R.build_outputs(pr, shift)
    open(os.path.join(pr.out, 'dieline_dim.svg'), 'w', encoding='utf-8').write(R.dimmed_dieline(pr, pr.dims))
    sp = os.path.join(pr.out, 'scene.json')
    sc = json.load(open(sp))
    sc['cords'] = [{'panel': 'F', 'pts': cord(L / 2), 'r': 2.0 * K, 'color': CORD}, {'panel': 'K', 'pts': cord(B.xS1 + L / 2), 'r': 2.0 * K, 'color': CORD}]
    json.dump(sc, open(sp, 'w'))
    print(KEY, 'ok', pr.SW, pr.SH, shift)
