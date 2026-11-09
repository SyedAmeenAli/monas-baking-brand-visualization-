"""Hand-inked illustration toolkit for Mona's Baking. Everything is drawn procedurally as SVG:
wobbly double ink lines, flat pastel fills printed slightly out of register, hand-lettered text (outlined).
Local coords: mm, u right, w down. No raster stock, no AI imagery."""
import math, os, random
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'fonts')
BABY, BLUSH, CREAM, COCOA = '#FFD9E4', '#F7B6C7', '#FFF6F6', '#8B4A3A'
ROSE, SAGE, BUTTER, GOLD, CHERRY = '#E98CA8', '#A9BC9A', '#F6DDA8', '#C9A063', '#D9526F'
INK = COCOA

_ctr = [0]


def _noise(seed, amp, lam):
    r = random.Random(seed)
    ph = [r.random() * 6.283 for _ in range(3)]
    fr = [1 / lam, 2.3 / lam, 4.1 / lam]
    return lambda s: amp * (0.6 * math.sin(6.283 * fr[0] * s + ph[0]) + 0.3 * math.sin(6.283 * fr[1] * s + ph[1]) + 0.1 * math.sin(6.283 * fr[2] * s + ph[2]))


def _resample(pts, step):
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / step))
        for i in range(1, n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def _wobble(pts, amp=0.28, lam=22.0, step=2.6, seed=None):
    if seed is None:
        _ctr[0] += 1
        seed = _ctr[0]
    p = _resample(pts, step)
    nz = _noise(seed, amp, lam)
    nz2 = _noise(seed + 977, amp, lam * 0.8)
    s = 0.0
    out = []
    for i, (x, y) in enumerate(p):
        if i:
            s += math.hypot(x - p[i - 1][0], y - p[i - 1][1])
        out.append((x + nz2(s), y + nz(s)))
    return out


def _smooth(pts, closed=False):
    """Catmull-Rom -> cubic bezier path."""
    n = len(pts)
    if n < 3:
        return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts)
    P = pts
    d = f'M{P[0][0]:.2f},{P[0][1]:.2f}'
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1, p2 = P[i], P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f' C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}'
    return d + (' Z' if closed else '')


# ---------------------------------------------------------------- shape point generators
def rect_pts(x, y, w, h, r=0):
    if r <= 0:
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(7):
            a = math.radians(a0 + k * 15)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def ellipse_pts(cx, cy, rx, ry, n=28, a0=0, a1=360):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def arch_pts(x, y, w, h):
    """Window with round top: x,y top-left of bounding box."""
    r = w / 2
    pts = [(x, y + h), (x, y + r)]
    pts += ellipse_pts(x + r, y + r, r, r, 16, 180, 360)[1:]
    pts += [(x + w, y + h)]
    return pts


# ---------------------------------------------------------------- stroking / filling
def line(pts, w=0.5, col=INK, closed=False, amp=0.28, lam=22, cap='round', fill='none', dash=None, double=True, op=1.0):
    """Wobbly ink stroke (+ faint second pass for a drawn feel)."""
    p = _wobble(pts + ([pts[0]] if closed else []), amp, lam)
    d = _smooth(p[:-1] if closed else p, closed)
    da = f' stroke-dasharray="{dash}"' if dash else ''
    o = f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"{da} opacity="{op}"/>'
    if double and w >= 0.35:
        p2 = _wobble(pts + ([pts[0]] if closed else []), amp * 1.1, lam * 0.9)
        o += f'<path d="{_smooth(p2[:-1] if closed else p2, closed)}" fill="none" stroke="{col}" stroke-width="{w*0.4:.2f}" stroke-linecap="round" opacity=".55"{da}/>'
    return o


def blob(pts, fill, dx=0.55, dy=0.4, op=1.0, amp=0.25):
    """Flat colour fill, printed slightly out of register with the ink."""
    p = _wobble(pts + [pts[0]], amp, 20)[:-1]
    p = [(x + dx, y + dy) for x, y in p]
    return f'<path d="{_smooth(p, True)}" fill="{fill}" opacity="{op}"/>'


def shape(pts, fill, w=0.5, col=INK, dx=0.55, dy=0.4, closed=True):
    return blob(pts, fill, dx, dy) + line(pts, w, col, closed=closed)


def hatch(x, y, w, h, gap=1.6, ang=45, col=INK, op=0.35, sw=0.22, uid='h'):
    _ctr[0] += 1
    cid = f'hc{_ctr[0]}'
    o = f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#{cid})" opacity="{op}" stroke="{col}" stroke-width="{sw}" fill="none">'
    n = int((w + h) / gap) + 2
    for i in range(n):
        o += f'<path d="M{x + i*gap - h:.2f},{y + h} L{x + i*gap:.2f},{y}"/>' if ang == 45 else f'<path d="M{x},{y + i*gap:.2f} L{x+w},{y + i*gap:.2f}"/>'
    return o + '</g>'


def grain(w, h, uid='g'):
    """Paper grain overlay (SVG turbulence)."""
    _ctr[0] += 1
    f = f'pg{_ctr[0]}'
    return (f'<filter id="{f}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="{_ctr[0]}"/>'
            f'<feColorMatrix values="0 0 0 0 0.55  0 0 0 0 0.29  0 0 0 0 0.23  0 0 0 0.10 0"/></filter>'
            f'<rect x="-6" y="-6" width="{w+12}" height="{h+12}" filter="url(#{f})"/>')


# ---------------------------------------------------------------- lettering (outlined, variable font default instance)
_fc = {}


def _f(name):
    if name not in _fc:
        t = TTFont(os.path.join(FONT_DIR, name))
        _fc[name] = (t, t.getGlyphSet(), t.getBestCmap(), t['head'].unitsPerEm)
    return _fc[name]


CAVEAT = 'Caveat[wght].ttf'
FRAUNCES = 'Fraunces[SOFT,WONK,opsz,wght].ttf'
FRAUNCES_I = 'Fraunces-Italic[SOFT,WONK,opsz,wght].ttf'


def tw(txt, font, size, ls=0):
    t, gs, cm, upm = _f(font)
    return sum(gs[cm[ord(c)]].width for c in txt if ord(c) in cm) * size / upm + ls * (len(txt) - 1)


def hand(txt, x, y, size, font=CAVEAT, fill=INK, anchor='middle', ls=0.0, rot=0, op=1.0):
    t, gs, cm, upm = _f(font)
    s = size / upm
    w = tw(txt, font, size, ls)
    cx = x - (w / 2 if anchor == 'middle' else w if anchor == 'end' else 0)
    pen = SVGPathPen(gs)
    for c in txt:
        if ord(c) not in cm:
            cx += size * 0.3
            continue
        g = cm[ord(c)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
        cx += gs[g].width * s + ls
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ''
    return f'<path d="{pen.getCommands()}" fill="{fill}" opacity="{op}"{tr}/>'


def ribbon_text(txt, cx, cy, size, rx, font=CAVEAT, fill=INK, a0=-60, a1=60):
    """Text laid along the top of a circle (centre cx,cy radius rx)."""
    t, gs, cm, upm = _f(font)
    n = len(txt)
    o = ''
    for i, ch in enumerate(txt):
        a = a0 + (a1 - a0) * (i + 0.5) / n
        x = cx + rx * math.sin(math.radians(a))
        y = cy - rx * math.cos(math.radians(a))
        o += hand(ch, x, y, size, font, fill, rot=a)
    return o


# ---------------------------------------------------------------- motifs
def gingham(x, y, w, h, cell=5.5, col=BLUSH, base=CREAM, wave=1.2, uid='gh'):
    _ctr[0] += 1
    cid = f'gg{_ctr[0]}'
    top = [(x + i * (w / 14), y + (wave if i % 2 else -wave) * 0.8) for i in range(15)]
    d = _smooth(_wobble(top, 0.25, 14), False) + f' L{x+w+3},{y+h+3} L{x-3},{y+h+3} Z'
    o = f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})"><rect x="{x-3}" y="{y-3}" width="{w+6}" height="{h+8}" fill="{base}"/>'
    for i in range(0, int(w / cell) + 3, 2):
        o += f'<rect x="{x + i*cell - 2:.2f}" y="{y-3}" width="{cell}" height="{h+8}" fill="{col}" fill-opacity=".62"/>'
    for j in range(0, int(h / cell) + 3, 2):
        o += f'<rect x="{x-3}" y="{y + j*cell - 2:.2f}" width="{w+6}" height="{cell}" fill="{col}" fill-opacity=".62"/>'
    o += '</g>' + line(top, 0.5, INK, amp=0.2)
    return o


def awning(x, y, w, h, n=11, tilt=7):
    """Striped shop awning, scalloped valance. x,y top-left; flares out by `tilt` each side."""
    o = ''
    topL, topR = x + tilt, x + w - tilt
    botL, botR = x, x + w
    ybot = y + h
    sw = (botR - botL) / n
    for i in range(n):
        a0, a1 = i / n, (i + 1) / n
        tl = topL + (topR - topL) * a0
        tr_ = topL + (topR - topL) * a1
        bl = botL + (botR - botL) * a0
        br = botR if i == n - 1 else botL + (botR - botL) * a1
        col = BLUSH if i % 2 == 0 else CREAM
        r = sw / 2
        pts = [(tl, y), (tr_, y), (br, ybot)] + [(br - r * (1 + math.cos(math.radians(a))) * 0.5 * 1.0 - 0, ybot + r * 0.9 * math.sin(math.radians(a))) for a in (30, 90, 150)] + [(bl, ybot)]
        o += blob(pts, col, 0.5, 0.35)
        o += line(pts + [pts[0]], 0.5, INK, amp=0.2)
    o += line([(topL - 1, y), (topR + 1, y)], 0.9, INK)
    return o


def lantern(x, y, s=1.0):
    o = line([(x, y - 9 * s), (x, y - 3 * s)], 0.4)
    top = [(x - 3 * s, y - 3 * s), (x + 3 * s, y - 3 * s), (x + 5 * s, y), (x - 5 * s, y)]
    body = [(x - 5 * s, y), (x + 5 * s, y), (x + 4 * s, y + 9 * s), (x - 4 * s, y + 9 * s)]
    o += shape(top, GOLD, 0.45) + shape(body, BUTTER, 0.45)
    o += line([(x, y), (x, y + 9 * s)], 0.3, double=False) + line([(x - 2.6 * s, y), (x - 2.2 * s, y + 9 * s)], 0.25, double=False) + line([(x + 2.6 * s, y), (x + 2.2 * s, y + 9 * s)], 0.25, double=False)
    o += shape([(x - 3 * s, y + 9 * s), (x + 3 * s, y + 9 * s), (x + 1.5 * s, y + 12 * s), (x - 1.5 * s, y + 12 * s)], GOLD, 0.4)
    return o


def rose(x, y, r=3.2, col=ROSE):
    o = blob(ellipse_pts(x, y, r, r * 0.95, 14), col, 0.3, 0.25)
    sp = []
    for i in range(0, 60):
        a = i * 0.55
        rr = r * (0.12 + i / 60 * 0.85)
        sp.append((x + rr * math.cos(a), y + rr * math.sin(a) * 0.95))
    o += line(sp, 0.22, INK, amp=0.06, lam=6, double=False, op=.7)
    o += line(ellipse_pts(x, y, r, r * 0.95, 14), 0.3, INK, closed=True, amp=0.1, lam=8, double=False)
    return o


def leaf(x, y, ang, s=4.0, col=SAGE):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    pts = [(x, y), (x + ux * s * 0.5 + px * s * 0.28, y + uy * s * 0.5 + py * s * 0.28), (x + ux * s, y + uy * s),
           (x + ux * s * 0.5 - px * s * 0.28, y + uy * s * 0.5 - py * s * 0.28)]
    return shape(pts, col, 0.35, dx=0.25, dy=0.2) + line([(x, y), (x + ux * s * 0.85, y + uy * s * 0.85)], 0.2, double=False)


def vine(pts, nleaf=7, roses=(), seed=1):
    o = line(pts, 0.55, INK, amp=0.35, lam=12)
    rs = _resample(pts, (sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))) / max(nleaf, 1))
    rr = random.Random(seed)
    for i, (px, py) in enumerate(rs[1:], 1):
        side = 1 if i % 2 else -1
        o += leaf(px, py, 90 + side * (40 + rr.random() * 25) + rr.random() * 20, 4.2 + rr.random() * 1.6)
    for (rx_, ry_, rs_) in roses:
        o += rose(rx_, ry_, rs_)
    return o


def cherry(x, y, r=2.2):
    o = line([(x, y - r), (x + r * 0.6, y - r * 2.6), (x + r * 1.6, y - r * 3.1)], 0.4, double=False)
    o += shape(ellipse_pts(x, y, r, r, 14), CHERRY, 0.4, dx=0.3, dy=0.25)
    o += line([(x - r * 0.5, y - r * 0.2), (x - r * 0.1, y - r * 0.6)], 0.3, '#fff', double=False, op=.9)
    return o


def strawberry(x, y, s=3.0):
    pts = [(x - s, y - s * 0.4), (x + s, y - s * 0.4), (x + s * 0.55, y + s * 0.9), (x, y + s * 1.4), (x - s * 0.55, y + s * 0.9)]
    o = shape(pts, CHERRY, 0.38, dx=0.3, dy=0.25)
    o += leaf(x - s * 0.7, y - s * 0.55, -20, s * 0.9) + leaf(x + s * 0.7, y - s * 0.55, 200, s * 0.9)
    for (dx, dy) in ((-0.4, 0), (0.4, 0.2), (0, 0.7), (-0.2, 0.9)):
        o += f'<circle cx="{x + dx * s:.2f}" cy="{y + dy * s:.2f}" r="0.28" fill="{CREAM}"/>'
    return o


def cake(x, y, w=26, tiers=2, h=8.0):
    """Tiered cake, front 3/4 view. x centre, y base line."""
    o = ''
    cw = w
    yy = y
    for t in range(tiers):
        rx = cw / 2
        ry = rx * 0.28
        body = [(x - rx, yy - h), (x + rx, yy - h), (x + rx, yy), (x - rx, yy)]
        o += blob(rect_pts(x - rx, yy - h, cw, h), BUTTER if t % 2 == 0 else BABY, 0.5, 0.4)
        o += line([(x - rx, yy - h), (x - rx, yy)], 0.5, amp=0.15) + line([(x + rx, yy - h), (x + rx, yy)], 0.5, amp=0.15)
        o += line(ellipse_pts(x, yy, rx, ry, 18, 0, 180), 0.5, amp=0.15)
        # icing top + drips
        o += blob(ellipse_pts(x, yy - h, rx, ry, 18), CREAM, 0.4, 0.3)
        drips = [(x - rx, yy - h)]
        for i in range(1, 8):
            ux = x - rx + cw * i / 8
            drips += [(ux - cw / 16, yy - h + (2.2 + (i * 7 % 3)) * (h / 8)), (ux, yy - h + 0.4)]
        drips += [(x + rx, yy - h)]
        o += line(drips, 0.45, amp=0.12, lam=8)
        o += line(ellipse_pts(x, yy - h, rx, ry, 18), 0.5, closed=True, amp=0.12)
        yy -= h
        cw *= 0.66
        h *= 0.9
    o += strawberry(x - 3, yy - 1.5, 2.0) + cherry(x + 3.2, yy - 1.2, 1.4)
    return o


def cakestand(x, y, w=30):
    o = line([(x - w * 0.15, y), (x + w * 0.15, y)], 0.5)
    o += shape([(x - w * 0.5, y - 2.2), (x + w * 0.5, y - 2.2), (x + w * 0.46, y), (x - w * 0.46, y)], CREAM, 0.5)
    o += line([(x, y), (x, y + 8)], 0.5) + shape([(x - 4.5, y + 8), (x + 4.5, y + 8), (x + 6, y + 10), (x - 6, y + 10)], CREAM, 0.45)
    return o


def dome(x, y, w, h):
    pts = [(x - w / 2, y)] + ellipse_pts(x, y, w / 2, h, 14, 180, 360)[1:-1] + [(x + w / 2, y)]
    return blob(pts, '#FFFFFF', 0.4, 0.3, 0.35) + line(pts, 0.4, INK, amp=0.2, op=.8) + shape(ellipse_pts(x, y - h - 1.4, 1.1, 1.1, 8), BLUSH, 0.35)


def cupcake(x, y, s=1.0, col=BLUSH):
    o = shape([(x - 3.2 * s, y - 3 * s), (x + 3.2 * s, y - 3 * s), (x + 2.4 * s, y), (x - 2.4 * s, y)], col, 0.4, dx=0.3, dy=0.25)
    for k in (-1.6, 0, 1.6):
        o += line([(x + k * s, y - 3 * s), (x + k * 0.75 * s, y)], 0.22, double=False)
    o += shape([(x - 3.5 * s, y - 3 * s), (x - 2.8 * s, y - 5.5 * s), (x, y - 7.4 * s), (x + 2.8 * s, y - 5.5 * s), (x + 3.5 * s, y - 3 * s)], CREAM, 0.4, dx=0.3, dy=0.25)
    o += cherry(x, y - 7.6 * s, 0.95 * s)
    return o


def tiered_stand(x, y, w=26):
    """3-tier stand of cupcakes (the 'hand iced cakes' window)."""
    o = line([(x, y - 30), (x, y + 6)], 0.5)
    for k, (yy, ww) in enumerate(((y, w), (y - 14, w * 0.75), (y - 27, w * 0.5))):
        o += shape([(x - ww / 2, yy - 1.6), (x + ww / 2, yy - 1.6), (x + ww / 2 - 1, yy), (x - ww / 2 + 1, yy)], CREAM, 0.45)
        n = [4, 3, 2][k]
        for i in range(n):
            cx = x - ww / 2 + ww * (i + 0.5) / n
            o += cupcake(cx, yy - 1.6, 0.8, BLUSH if (i + k) % 2 == 0 else BABY)
    o += shape([(x - 5, y + 6), (x + 5, y + 6), (x + 7, y + 8), (x - 7, y + 8)], CREAM, 0.4)
    return o


def curtain(x, y, w, h, left=True):
    s = 1 if left else -1
    pts = [(x, y), (x + s * w, y), (x + s * w * 0.35, y + h * 0.55), (x + s * w * 0.55, y + h), (x, y + h)]
    o = blob(pts, BLUSH, 0.4, 0.3) + line(pts, 0.45, closed=True, amp=0.2)
    for k in (0.3, 0.55, 0.8):
        o += line([(x + s * w * k, y + 0.5), (x + s * w * (k * 0.55), y + h * 0.9)], 0.22, double=False, op=.7)
    o += line([(x + s * w * 0.35, y + h * 0.55), (x, y + h * 0.58)], 0.35, double=False)
    return o


def window_scene(x, y, w, h, content, arched=True, uid='w'):
    """Window with glass, frame, curtains and content drawn by callback."""
    _ctr[0] += 1
    cid = f'ws{_ctr[0]}'
    gp = arch_pts(x, y, w, h) if arched else rect_pts(x, y, w, h)
    o = f'<clipPath id="{cid}"><path d="{_smooth(gp, True)}"/></clipPath>'
    o += blob(gp, '#FFFFFF', 0.4, 0.3, 0.9)
    o += f'<g clip-path="url(#{cid})">' + blob(gp, BABY, 0.3, 0.2, 0.55) + hatch(x, y, w, h, 2.1, 45, INK, 0.12) + content + '</g>'
    # frame (double line)
    o += line(gp, 1.0, INK, closed=True, amp=0.25)
    inner = arch_pts(x + 2.2, y + 2.2, w - 4.4, h - 4.4) if arched else rect_pts(x + 2.2, y + 2.2, w - 4.4, h - 4.4)
    o += line(inner, 0.4, INK, closed=True, amp=0.2)
    return o


def flower_box(x, y, w, n=7, seed=3):
    o = shape([(x, y), (x + w, y), (x + w - 2, y + 6), (x + 2, y + 6)], BLUSH, 0.5)
    o += hatch(x + 2, y, w - 4, 6, 1.5, 0, INK, 0.25)
    r = random.Random(seed)
    for i in range(n):
        px = x + 3 + (w - 6) * i / (n - 1)
        o += leaf(px, y + 0.5, 270 + r.uniform(-35, 35), 4.5)
    for i in range(n):
        px = x + 3 + (w - 6) * (i + 0.5) / n
        o += rose(px, y - 1.6 - (i % 2) * 1.4, 2.0 + (i % 3) * 0.3, ROSE if i % 2 else BLUSH)
    return o


def bunting(x0, x1, y, n, sag=4, flags=(BLUSH, CREAM, BABY)):
    o = ''
    pts = [(x0 + (x1 - x0) * i / 24, y + sag * math.sin(math.pi * i / 24)) for i in range(25)]
    o += line(pts, 0.4, amp=0.15)
    for i in range(n):
        t = (i + 0.5) / n
        px = x0 + (x1 - x0) * t
        py = y + sag * math.sin(math.pi * t)
        tri = [(px - 3.4, py), (px + 3.4, py), (px, py + 7)]
        o += shape(tri, flags[i % len(flags)], 0.4, dx=0.3, dy=0.25)
    return o


def stamp_round(cx, cy, r, top, bottom, fill=None):
    o = line(ellipse_pts(cx, cy, r, r, 30), 0.6, closed=True) + line(ellipse_pts(cx, cy, r - 2.2, r - 2.2, 30), 0.3, closed=True, double=False)
    o += ribbon_text(top, cx, cy + 1, r * 0.34, r - 6.8, CAVEAT, COCOA, -70, 70)
    o += ribbon_text(bottom[::-1], cx, cy - 1, r * 0.3, -(r - 6.4), CAVEAT, COCOA, 55, -55) if False else ''
    return o
