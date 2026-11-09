"""Build the 4-inch handled cake box and the 5.5 in brownie tuck box: art, dielines, PDFs, textures, 3D scene data."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import ink, scenes as S, tuck as T
import render as R
import geom as g
from ink import *


# ============================== 4-inch handled cake box (geometry from validated-by-self kinematics, still unvalidated)
def box4():
    P = g.build_panels()
    L = logo = R.logo_uri

    k = g.K
    def sc(body):
        return body if abs(k - 1) < 1e-6 else f'<g transform="scale({k:.5f})">{body}</g>'

    def outer(n, p):
        Wp, Hp = p.art['size']
        Wp, Hp = Wp / k, Hp / k
        return sc({'B': lambda: S.base(Wp, Hp, logo), 'F': lambda: S.front(Wp, Hp, logo), 'K': lambda: S.back(Wp, Hp, logo),
                'L': lambda: S.side_door(Wp, Hp, logo), 'R': lambda: S.side_window(Wp, Hp, logo),
                'BL': lambda: S.roof(Wp, Hp, True), 'FL': lambda: S.roof(Wp, Hp, False),
                'HB': lambda: S.handle_art(Wp, Hp, 'b'), 'HF': lambda: S.handle_art(Wp, Hp, 'f')}.get(n, lambda: '')())

    def inner(n, p):
        Wp, Hp = p.art['size']
        Wp, Hp = Wp / k, Hp / k
        return sc({'F': lambda: S.wall_in(Wp, Hp), 'K': lambda: S.wall_in(Wp, Hp), 'L': lambda: S.wall_in(Wp, Hp), 'R': lambda: S.wall_in(Wp, Hp),
                'BL': lambda: S.lid_note_back(Wp, Hp), 'FL': lambda: S.lid_note_front(Wp, Hp), 'TH': lambda: S.tongue_in(Wp, Hp)}.get(n, lambda: '')())
    W_, D_, H_ = g.W, g.D, g.H
    xb, yb = g.XB, g.YB
    dm = ''
    dm += R.dim_h(xb, xb + W_, yb + D_ + H_ + g.LID + g.HP + 6, 0, W_)           # base width (shown below)
    dm += R.dim_v(xb - H_, yb, yb + D_, -4, D_)                                    # side wall depth D
    dm += R.dim_v(xb + W_ + H_, yb - 0, yb - 0 + 0.001, 0, 0) if False else ''
    dm += R.dim_v(xb + W_, yb + D_, yb + D_ + H_, 12, H_)                          # wall height
    dm += R.dim_v(xb + W_, yb + D_ + H_, yb + D_ + H_ + g.LID, 12, g.LID)          # lid depth
    dm += R.dim_v(xb + W_, yb + D_ + H_ + g.LID, yb + D_ + H_ + g.LID + g.HP, 12, g.HP)  # ply height
    dm += R.dim_h(xb - H_, xb, yb + D_ + 3, 8, H_)                                 # side wall length (height)
    dm += R.dim_h(g.XC - g.PW / 2, g.XC + g.PW / 2, yb + D_ + H_ + g.LID + g.HP + 2, 8, g.PW)
    dm += R.dim_h(xb - H_, xb + W_ + H_, -8, 0, g.SHEET_W)
    dm += R.dim_v(xb - H_ - 6, 0, g.SHEET_H, -10, g.SHEET_H)
    key = 'box4' if g.CAKE_IN == 4 else f'cake{int(g.CAKE_IN)}'
    pr = R.Product(key, f'{g.CAKE_IN:g}-inch handled cake box', P, g.SHEET_W, g.SHEET_H, outer, inner, 'tray', dm)
    shift = [-g.XC, 0, g.YB + g.D / 2]
    return pr, shift


# ============================== brownie tuck-end box
def tuckbox():
    P = T.build()
    logo = R.logo_uri
    Wf, Hf = T.L, T.Hh

    def front(Wp, Hp):
        o = S.bgp(Wp, Hp)
        o += bunting(6, Wp - 6, 6, 18, 3)
        o += awning(10, 11, Wp - 20, 10, 18, 3)
        wx, wy, ww, wh = 16, 24, Wp - 32, 22
        ins = curtain(wx + 1, wy + 1, 10, 14, True) + curtain(wx + ww - 1, wy + 1, 10, 14, False)
        for i in range(4):
            ins += brownie(wx + 14 + i * ((ww - 28) / 3), wy + wh - 5, 14)
        o += window_scene(wx, wy, ww, wh, ins, arched=False)
        o += hand('brownies', Wp / 2, 58.5, 6.6, CAVEAT, COCOA)
        o += gingham(0, 51, Wp, Hp - 51 + 3) if False else ''
        return o + grain(Wp, Hp)

    def sidep(Wp, Hp):
        o = S.bgp(Wp, Hp) + gingham(0, Hp - 24, Wp, 28)
        o += shape(rect_pts(Wp / 2 - 24, 8, 48, 22, 2), CREAM, 0.7) + hand('fudgy &', Wp / 2, 18.5, 7.4) + hand('full of love', Wp / 2, 27, 7.4)
        o += vine([(8, Hp - 4), (6, Hp - 20), (9, 14)], 4, [(7, 40, 1.9)], 31) + vine([(Wp - 8, Hp - 4), (Wp - 6, Hp - 20), (Wp - 9, 14)], 4, [(Wp - 7, 40, 1.9)], 33)
        return o + grain(Wp, Hp)

    def backp(Wp, Hp):
        o = S.bgp(Wp, Hp) + gingham(0, Hp - 24, Wp, 28)
        o += hand('4 fudgy brownies', Wp / 2, 18, 9, CAVEAT, COCOA) + hand('baked fresh, made with love', Wp / 2, 30, 7.2, CAVEAT, COCOA)
        o += line([(Wp / 2 - 30, 35), (Wp / 2 + 30, 35)], 0.3, double=False, dash='.9 1.4')
        return o + grain(Wp, Hp)

    def lid(Wp, Hp):
        o = S.bgp(Wp, Hp, BABY)
        o += line(rect_pts(5, 5, Wp - 10, Hp - 10, 6), 0.7, closed=True) + line(rect_pts(8, 8, Wp - 16, Hp - 16, 4), 0.3, closed=True, double=False, dash='1.2 1.1')
        lw = 78
        o += f'<image x="{(Wp-lw)/2:.2f}" y="{Hp/2-lw*0.333-4:.2f}" width="{lw}" height="{lw*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
        o += hand('homemade bakes, made with love', Wp / 2, Hp - 28, 8.4, CAVEAT, COCOA)
        o += vine([(14, Hp - 14), (12, Hp - 34), (16, Hp - 54)], 4, [(13, Hp - 40, 2.2)], 35) + vine([(Wp - 14, Hp - 14), (Wp - 12, Hp - 34), (Wp - 16, Hp - 54)], 4, [(Wp - 13, Hp - 40, 2.2)], 37)
        return o + grain(Wp, Hp)

    def tuckflap(Wp, Hp):
        return S.bgp(Wp, Hp, BLUSH) + hatch(0, 0, Wp, Hp, 2.2, 45, COCOA, .12) + grain(Wp, Hp)

    def outer(n, p):
        Wp, Hp = p.art['size']
        if n == 'F': return front(Wp, Hp)
        if n in ('SR', 'SL'): return sidep(Wp, Hp)
        if n == 'K': return backp(Wp, Hp)
        if n == 'TTT': return lid(Wp, Hp)
        if n == 'TTB': return tuckflap(Wp, Hp)
        if p.role == 'dust': return S.bgp(Wp, Hp, BABY) + grain(Wp, Hp)
        if p.role == 'tongue': return S.bgp(Wp, Hp, BLUSH)
        return ''

    def inner(n, p):
        Wp, Hp = p.art['size']
        if n in ('F', 'K', 'SR', 'SL'):
            return S.bgp(Wp, Hp, '#FFFDFD')
        if p.role in ('dust', 'tongue'):
            return S.bgp(Wp, Hp, '#FFFDFD')
        if n == 'TTT':
            return S.bgp(Wp, Hp, BABY) + hand('enjoy!', Wp / 2, Hp / 2 + 4, 12, CAVEAT, COCOA, rot=-3) + grain(Wp, Hp)
        return ''
    xs = {'F': 0, 'SR': T.L, 'K': T.L + T.Wd, 'SL': 2 * T.L + T.Wd}
    dm = ''
    y1 = T.YB0 + T.Hh
    dm += R.dim_h(0, T.L, T.SHEET_H + 6, 0, T.L) + R.dim_h(T.L, T.L + T.Wd, T.SHEET_H + 6, 0, T.Wd)
    dm += R.dim_v(-4, T.YB0, y1, -6, T.Hh)
    dm += R.dim_h(0, T.SHEET_W, -8, 0, T.SHEET_W) + R.dim_v(-4, 0, T.SHEET_H, -16, T.SHEET_H)
    dm += R.dim_v(T.L + T.Wd + T.L, T.YB0 - T.TD, T.YB0, 8, T.TD)
    dm += R.dim_h(T.L + T.Wd + T.L + T.Wd, T.SHEET_W, T.YB0 + T.Hh / 2 + 8, 14, T.GW)
    pr = R.Product('tuck', '5.5 in brownie tuck-end box', P, T.SHEET_W, T.SHEET_H, outer, inner, 'tube', dm)
    # shift: computed after folding (centre x/z of body, base at y=0)
    M = g.fold_matrices(P)
    pts = np.vstack([np.array([(x, -Y, 0) for x, Y in P[n].ring()]) for n in ('F', 'SR', 'K', 'SL')])
    fp = np.vstack([(M[n] @ np.array([x, -Y, 0, 1.0]))[:3] for n in ('F', 'SR', 'K', 'SL') for x, Y in P[n].ring()])
    shift = [-(fp[:, 0].min() + fp[:, 0].max()) / 2, -(-(T.YB0 + T.Hh)), -(fp[:, 2].min() + fp[:, 2].max()) / 2]
    return pr, shift


def brownie(x, y, w=14):
    h = w * 0.62
    o = shape(rect_pts(x - w / 2, y - h, w, h, 1.2), '#B9786A', 0.4, dx=0.3, dy=0.25)
    o += shape(rect_pts(x - w / 2, y - h, w, h * 0.38, 1.0), COCOA, 0.35, dx=0.2, dy=0.2)
    for (a, c) in ((-0.28, 0.1), (0.05, 0.2), (0.3, 0.08)):
        o += shape(ellipse_pts(x + a * w, y - h + h * c, 0.9, 0.7, 6), BUTTER, 0.25, dx=0.15, dy=0.1)
    return o


if __name__ == '__main__':
    which = sys.argv[1:] or ['box4', 'tuck']
    for k in which:
        pr, shift = {'box4': box4, 'tuck': tuckbox}[k]()
        R.build_outputs(pr, shift, dpi=int(min(110, 3000 / ((pr.SH + 32) / 25.4))))
        open(os.path.join(pr.out, 'dieline_dim.svg'), 'w', encoding='utf-8').write(R.dimmed_dieline(pr, pr.dims))
        print(k, 'ok', pr.SW, pr.SH, shift)
