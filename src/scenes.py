"""Panel artwork for the 4-inch cake box: a miniature hand-inked bakery shop. Local coords u right, w down (mm)."""
import math
import ink as k
from ink import *


def bgp(w, h, col=BABY):
    return f'<rect x="-6" y="-6" width="{w+12}" height="{h+12}" fill="{col}"/>'


def sign_band(W, logo, y=5, h=40):
    o = shape(rect_pts(6, y, W - 12, h, 3), CREAM, 0.9)
    o += line(rect_pts(8.6, y + 2.6, W - 17.2, h - 5.2, 2), 0.35, closed=True, double=False)
    lw = 46
    o += f'<image x="{(W-lw)/2:.2f}" y="{y+4.5:.2f}" width="{lw}" height="{lw*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
    o += hand('homemade', 26, y + 17, 6.6, CAVEAT, COCOA) + hand('bakes', 26, y + 24.5, 6.6, CAVEAT, COCOA)
    o += hand('made with', W - 26, y + 17, 6.6, CAVEAT, COCOA) + hand('love', W - 26, y + 24.5, 6.6, CAVEAT, COCOA)
    for xx in (14, W - 14):
        o += line([(xx - 3, y + 33), (xx + 3, y + 33)], 0.3, double=False)
    return o


def front(W, H, logo):
    o = bgp(W, H)
    o += sign_band(W, logo)
    o += awning(4, 49, W - 8, 21, 11, 5)
    # shop window
    wx, wy, ww, wh = 22, 77, 83, 38
    inside = curtain(wx + 1, wy + 1, 14, 27, True) + curtain(wx + ww - 1, wy + 1, 14, 27, False)
    inside += tiered_stand(wx + 22, wy + wh - 11, 22)
    inside += cakestand(wx + 61, wy + wh - 11, 28) + cake(wx + 61, wy + wh - 13.5, 22, 2, 7.5) + dome(wx + 61, wy + wh - 13.4, 27, 17)
    o += window_scene(wx, wy, ww, wh, inside, arched=False)
    o += flower_box(wx - 2, wy + wh + 1.5, ww + 4, 9)
    # pilasters + vines
    for px in (8, W - 17):
        o += shape(rect_pts(px, 74, 9, 52), CREAM, 0.6)
        for yy in range(78, 124, 6):
            o += line([(px + 1.4, yy), (px + 7.6, yy)], 0.25, double=False, op=.6)
        o += shape(rect_pts(px - 1.5, 71.5, 12, 3.2), BLUSH, 0.5) + shape(rect_pts(px - 1.5, 124, 12, 3.2), BLUSH, 0.5)
    o += vine([(13, 124), (11.5, 108), (14.5, 94), (10.8, 80), (13.5, 70)], 8, [(12, 100, 2.4), (14, 84, 2.1)], 3)
    o += vine([(W - 12.5, 124), (W - 14, 106), (W - 10.8, 92), (W - 14.2, 78), (W - 12, 70)], 8, [(W - 13, 98, 2.4), (W - 11.5, 82, 2.1)], 5)
    o += lantern(6, 62, 0.8) + lantern(W - 6, 62, 0.8)
    o += gingham(0, 127, W, H - 127 + 4)
    o += hand('open daily', W / 2, 143.6, 6.2, CAVEAT, COCOA, rot=-1.5, op=.9)
    return o + grain(W, H)


def side_window(W, H, logo):
    o = bgp(W, H)
    o += shape(rect_pts(26, 8, W - 52, 18, 2.5), CREAM, 0.8) + hand('cupcakes & more', W / 2, 20, 8.6, CAVEAT, COCOA)
    o += bunting(10, W - 10, 31, 11, 4.5)
    wx, wy, ww, wh = 28, 44, 71, 80
    inside = curtain(wx + 1, wy + 8, 12, 50, True) + curtain(wx + ww - 1, wy + 8, 12, 50, False)
    inside += tiered_stand(wx + ww / 2, wy + 62, 36)
    inside += cherry(wx + 12, wy + 70, 2.2) + cherry(wx + 59, wy + 71, 2.2)
    o += window_scene(wx, wy, ww, wh, inside, arched=True)
    o += shape(rect_pts(wx - 3, wy + wh, ww + 6, 4), CREAM, 0.6)
    o += flower_box(wx - 3, wy + wh + 3, ww + 6, 9, 8)
    o += vine([(12, 126), (9.5, 106), (14, 88), (10.5, 70), (13, 50), (11, 38)], 10, [(11, 112, 2.5), (13.5, 92, 2.2), (11.5, 62, 2.2)], 7)
    o += vine([(W - 12, 126), (W - 9.5, 106), (W - 14, 88), (W - 10.5, 70), (W - 13, 50), (W - 11, 38)], 10, [(W - 11, 100, 2.5), (W - 13.5, 78, 2.2), (W - 11.5, 56, 2.2)], 9)
    o += lantern(8, 42, 0.75) + lantern(W - 8, 42, 0.75)
    o += gingham(0, 127, W, H - 127 + 4)
    o += hand('fresh every morning', W / 2, 143.6, 6.2, CAVEAT, COCOA, rot=1.2, op=.9)
    return o + grain(W, H)


def side_door(W, H, logo):
    o = bgp(W, H)
    o += awning(20, 12, W - 40, 17, 9, 4)
    o += bunting(8, W - 8, 36, 12, 4.5)
    dx, dy, dw, dh = 38, 50, 51, 76
    door = arch_pts(dx, dy, dw, dh)
    o += shape(door, CREAM, 1.0)
    o += line(arch_pts(dx + 3, dy + 3, dw - 6, dh - 3), 0.4, closed=True, double=False)
    o += shape(ellipse_pts(dx + dw / 2, dy + 17, 10, 10, 18, 180, 360) + [(dx + dw / 2 + 10, dy + 17)], BABY, 0.5)
    o += line([(dx + dw / 2, dy + 7), (dx + dw / 2, dy + 17)], 0.3, double=False)
    for (rx_, ry_) in ((dx + 9, dy + 34), (dx + dw - 22, dy + 34), (dx + 9, dy + 56), (dx + dw - 22, dy + 56)):
        o += shape(rect_pts(rx_, ry_, 13, 17, 1.5), BLUSH, 0.5)
    o += shape(ellipse_pts(dx + dw - 7, dy + 46, 1.6, 1.6, 8), GOLD, 0.4)
    # hanging open sign
    o += line([(dx + 16, dy + 20), (dx + 19, dy + 26), (dx + 33, dy + 26), (dx + 36, dy + 20)], 0.3, double=False)
    o += shape(rect_pts(dx + 14, dy + 26, 24, 11, 2), CREAM, 0.6) + hand('open', dx + 26, dy + 34.2, 7.4, CAVEAT, COCOA)
    o += shape(rect_pts(dx - 5, 126, dw + 10, 3.6), BLUSH, 0.6)
    o += flower_box(14, 118, 20, 4, 2) + flower_box(W - 34, 118, 20, 4, 6)
    o += vine([(10, 126), (8.5, 104), (12, 86), (9.5, 66), (11, 52)], 8, [(10, 96, 2.4), (11, 72, 2.1)], 11)
    o += vine([(W - 10, 126), (W - 8.5, 104), (W - 12, 86), (W - 9.5, 66), (W - 11, 52)], 8, [(W - 10, 90, 2.4), (W - 11, 68, 2.1)], 13)
    o += lantern(dx - 9, 52, 0.7) + lantern(dx + dw + 9, 52, 0.7)
    o += gingham(0, 130, W, H - 130 + 4)
    return o + grain(W, H)


def back(W, H, logo):
    o = bgp(W, H)
    o += bunting(6, W - 6, 10, 13, 5)
    bx, by, bw, bh = 16, 28, W - 32, 88
    o += shape(rect_pts(bx, by, bw, bh, 4), CREAM, 1.0)
    o += line(rect_pts(bx + 3, by + 3, bw - 6, bh - 6, 3), 0.35, closed=True, double=False)
    o += hand("what's baking", W / 2, by + 17, 11.5, CAVEAT, COCOA)
    items = ['cakes & bento cakes', 'cupcakes', 'cookies & brownies', 'dessert boxes', 'custom celebration cakes']
    for i, t in enumerate(items):
        yy = by + 31 + i * 10.6
        o += hand(t, W / 2, yy, 7.2, CAVEAT, COCOA)
        if i < len(items) - 1:
            o += line([(W / 2 - 15, yy + 3.6), (W / 2 + 15, yy + 3.6)], 0.25, double=False, dash='0.8 1.4', op=.7)
    o += cherry(bx + 12, by + bh - 12, 2.0) + cherry(bx + bw - 13, by + bh - 12, 2.0)
    o += line([(W / 2 - 9, by + bh - 6.5), (W / 2 + 9, by + bh - 6.5)], 0.3, double=False)
    o += vine([(10, 126), (8, 104), (11, 84), (8.5, 66), (10, 50)], 7, [(9, 96, 2.2)], 15)
    o += vine([(W - 10, 126), (W - 8, 104), (W - 11, 84), (W - 8.5, 66), (W - 10, 50)], 7, [(W - 9, 84, 2.2)], 17)
    o += gingham(0, 127, W, H - 127 + 4)
    o += hand('baked with love', W / 2, 143.6, 6.2, CAVEAT, COCOA, rot=-1, op=.9)
    return o + grain(W, H)


def roof(W, H, back_half):
    """Lid half = roof tiles. Art local frame already oriented 'up = away from viewer'."""
    o = bgp(W, H, BLUSH)
    rows = int(H / 6) + 2
    for r in range(rows):
        y = 3 + r * 6.2
        off = (r % 2) * 5
        for i in range(-1, int(W / 10) + 2):
            cx = i * 10 + off
            pts = ellipse_pts(cx, y, 5, 5.2, 10, 0, 180)
            o += blob(pts + [(cx + 5, y - 6), (cx - 5, y - 6)], BLUSH if (r + i) % 3 else BABY, 0.3, 0.3, 0.9)
            o += line(pts, 0.4, INK, amp=0.12, lam=6, double=False, op=.8)
    o += grain(W, H)
    return o


def handle_art(W, H, which):
    o = bgp(W, H, BABY)
    o += line(rect_pts(3, 3, W - 6, H + 10, 10), 0.4, closed=True, dash='1.2 1.2', double=False)
    o += vine([(8, H), (6, H - 10), (9, H - 22)], 3, [(7, H - 4, 1.8)], 21 if which == 'f' else 23)
    o += vine([(W - 8, H), (W - 6, H - 10), (W - 9, H - 22)], 3, [(W - 7, H - 4, 1.8)], 25 if which == 'f' else 27)
    if which == 'f':
        o += hand('with love,', W / 2, 14, 7.5, CAVEAT, COCOA, rot=-3)
    else:
        o += hand('mona', W / 2, 14, 7.5, CAVEAT, COCOA, rot=3)
    return o + grain(W, H)


def base(W, H, logo):
    o = bgp(W, H, CREAM)
    s = 12.7
    for i in range(int(W / s) + 1):
        for j in range(int(H / s) + 1):
            if (i + j) % 2 == 0:
                o += blob(rect_pts(i * s, j * s, s, s), BABY, 0.3, 0.3, 0.8)
    for i in range(int(W / s) + 2):
        o += line([(i * s, 0), (i * s, H)], 0.25, double=False, op=.5)
        o += line([(0, i * s), (W, i * s)], 0.25, double=False, op=.5)
    o += shape(ellipse_pts(W / 2, H / 2, 44, 44, 30), CREAM, 0.8)
    o += f'<image x="{W/2-31:.2f}" y="{H/2-21:.2f}" width="62" height="{62*640/960:.2f}" xlink:href="{logo}" href="{logo}"/>'
    return o + grain(W, H)


# ---- inside
def wall_in(W, H):
    gh, n = 40, 7
    r = W / n / 2
    clip = f'M-6,-6 L{W+6},-6 L{W+6},{gh} L{W},{gh} ' + ''.join(f'A{r:.3f},{r:.3f} 0 0 1 {W-(i+1)*2*r:.3f},{gh} ' for i in range(n)) + f'L-6,{gh} Z'
    o = f'<clipPath id="wic"><path d="{clip}"/></clipPath><g clip-path="url(#wic)">' + gingham(-6, -6, W + 12, gh + 20, uid='wi') + '</g>'
    o += f'<path d="{clip}" fill="none" stroke="{COCOA}" stroke-width="0.5" opacity=".7"/>'
    return o


def lid_note_back(W, H):
    o = bgp(W, H, BABY) + line(rect_pts(6, 6, W - 12, H - 12, 5), 0.4, closed=True, dash='1.3 1.1', double=False)
    o += hand('A little cake,', W / 2, 26, 11.5, CAVEAT, COCOA, rot=-2) + hand('a lot of love', W / 2, 40, 11.5, CAVEAT, COCOA, rot=-1)
    o += cherry(W / 2 - 24, 48, 2.0) + cherry(W / 2 + 24, 48, 2.0)
    return o + grain(W, H)


def lid_note_front(W, H):
    o = bgp(W, H, BABY) + line(rect_pts(6, 6, W - 12, H - 12, 5), 0.4, closed=True, dash='1.3 1.1', double=False)
    o += cake(W / 2, 40, 22, 2, 7) + hand('thank you!', W / 2, 53, 8.4, CAVEAT, COCOA)
    return o + grain(W, H)


def tongue_in(W, H):
    return f'<rect x="-6" y="-6" width="{W+12}" height="{H+12}" fill="{CHERRY}"/>'
