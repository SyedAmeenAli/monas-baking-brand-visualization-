"""Generic product renderer: dieline + art + dimensioned SVG, vector PDF (Chrome), textures, 3D scene JSON."""
import base64, json, math, os, subprocess, sys
import numpy as np
import pymupdf as fz
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '01_CAKE_BOXES', '4-inch', 'src'))
import geom as g
import build as b            # v0.1 helpers (offset_ring, dieline pieces) - geometry only
import ink

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
PAD = 16.0
LOGO = os.path.join(SITE, '..', '00_BRAND_ASSETS', 'approved_logo_transparent.png')
logo_uri = 'data:image/png;base64,' + base64.b64encode(open(LOGO, 'rb').read()).decode()
C_CUT, C_CREASE, C_GLUE, C_BLEED, C_SAFE = '#EC008C', '#00AEEF', '#F5C400', '#3B5BDB', '#2F9E44'


class Product:
    def __init__(self, key, title, P, SW, SH, outer, inner, mode, dims, notes=''):
        self.key, self.title, self.P, self.SW, self.SH = key, title, P, SW, SH
        self.outer, self.inner, self.mode, self.dims, self.notes = outer, inner, mode, dims, notes
        self.out = os.path.join(SITE, 'assets', key)
        os.makedirs(self.out, exist_ok=True)


def art_group(pr, side):
    parts, defs = [], []
    for n, p in pr.P.items():
        if not p.art or p.role == 'glue':
            continue
        body = pr.outer(n, p) if side == 'out' else pr.inner(n, p)
        if not body:
            continue
        ring = p.ring() if p.role in ('tongue', 'tongue-neck', 'tongue-heart') else b.offset_ring(p, g.BLEED)
        cid = f'bp_{pr.key}_{side}_{n}'
        defs.append(f'<clipPath id="{cid}"><path d="{b.poly_d(ring)}"/></clipPath>')
        Wp = p.art['size'][0]
        inner_t = f'<g transform="{b.mat(p.art)}">{body}</g>' if side == 'out' else f'<g transform="{b.mat(p.art)}"><g transform="matrix(-1 0 0 1 {Wp} 0)">{body}</g></g>'
        parts.append(f'<g id="art_{side}_{n}" clip-path="url(#{cid})">{inner_t}</g>')
    inner = ''.join(parts)
    if side == 'in':
        inner = f'<g transform="matrix(-1 0 0 1 {pr.SW} 0)">{inner}</g>'
    return '<defs>' + ''.join(defs) + '</defs>' + inner


def dieline_markup(pr):
    cut, crease, glue, seen = [], [], [], set()
    for n, p in pr.P.items():
        for r, closed in b.runs(p.edges, g.CUT):
            cut.append(f'<path d="{"".join(b.edge_d(e, i == 0) for i, e in enumerate(r)) + (" Z" if closed else "")}"/>')
        for r, closed in b.runs(p.edges, g.GLUE):
            cut.append(f'<path d="{"".join(b.edge_d(e, i == 0) for i, e in enumerate(r))}"/>')
        for e in p.edges:
            if e.kind == g.CREASE:
                key = tuple(sorted([tuple(round(v, 2) for v in e.p0), tuple(round(v, 2) for v in e.p1)]))
                if key in seen:
                    continue
                seen.add(key)
                crease.append(f'<line x1="{e.p0[0]:.3f}" y1="{e.p0[1]:.3f}" x2="{e.p1[0]:.3f}" y2="{e.p1[1]:.3f}"/>')
        for h in p.holes:
            cut.append(f'<path d="{"".join(b.edge_d(e, i == 0) for i, e in enumerate(h)) + " Z"}"/>')
        if p.role in ('glue',):
            glue.append(f'<path d="{b.poly_d(p.ring())}"/>')
    return cut, crease, glue


def dieline_group(pr, bleed_safe=True):
    cut, crease, glue = dieline_markup(pr)
    o = f'<g id="GLUE" fill="{C_GLUE}" fill-opacity=".38" stroke="none">{"".join(glue)}</g>'
    if bleed_safe:
        bl = ''.join(f'<path d="{b.poly_d(b.offset_ring(p, g.BLEED))}"/>' for p in pr.P.values() if p.role not in ('glue', 'tongue', 'dust'))
        sf = ''.join(f'<path d="{b.poly_d(b.offset_ring(p, -g.SAFE, -2.0))}"/>' for p in pr.P.values() if p.role not in ('glue', 'tongue', 'dust', 'tongue-neck', 'tongue-heart'))
        o += f'<g id="BLEED" fill="none" stroke="{C_BLEED}" stroke-width="0.14" stroke-dasharray="1.2 .8">{bl}</g>'
        o += f'<g id="SAFE" fill="none" stroke="{C_SAFE}" stroke-width="0.14" stroke-dasharray=".8 .8">{sf}</g>'
    o += f'<g id="CREASE" fill="none" stroke="{C_CREASE}" stroke-width="0.24" stroke-dasharray="2.2 1.2">{"".join(crease)}</g>'
    o += f'<g id="CUT" fill="none" stroke="{C_CUT}" stroke-width="0.3" stroke-linejoin="round">{"".join(cut)}</g>'
    return o


def svg_page(pr, content, pad=PAD, bg='#ffffff'):
    w, h = pr.SW + 2 * pad, pr.SH + 2 * pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w:.3f}mm" height="{h:.3f}mm" '
            f'viewBox="{-pad} {-pad} {w:.3f} {h:.3f}"><rect x="{-pad}" y="{-pad}" width="{w}" height="{h}" fill="{bg}"/>{content}</svg>')


def to_pdf(pr, svg, tag):
    w, h = pr.SW + 2 * PAD, pr.SH + 2 * PAD
    tmp = os.path.join(pr.out, '_tmp')
    os.makedirs(tmp, exist_ok=True)
    hp, pp = os.path.join(tmp, tag + '.html'), os.path.join(tmp, tag + '.pdf')
    open(hp, 'w', encoding='utf-8').write(f'<!doctype html><meta charset="utf-8"><style>@page{{size:{w:.3f}mm {h:.3f}mm;margin:0}}html,body{{margin:0}}svg{{display:block}}</style>{svg}')
    if os.path.exists(pp):
        os.remove(pp)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--run-all-compositor-stages-before-draw',
                    f'--print-to-pdf={pp}', 'file:///' + hp.replace(chr(92), '/')], check=True, capture_output=True, timeout=240)
    return fz.open(pp)


def export_scene(pr, shift):
    P = pr.P
    M = g.fold_matrices(P)
    panels = []
    for n, p in P.items():
        sgn = 0
        if p.parent:
            (x0, y0), (x1, y1) = p.hinge
            c = np.array(p.ring()).mean(axis=0)
            h = np.array([x1 - x0, -(y1 - y0), 0.0])
            s = np.array([c[0] - x0, -(c[1] - y0), 0.0])
            hn = h / np.linalg.norm(h)
            s = s - np.dot(s, hn) * hn
            sgn = 1 if np.cross(h, s)[2] > 0 else -1
        panels.append({'name': n, 'role': p.role, 'ring': [list(q) for q in p.ring()], 'holes': [[list(q) for q in r] for r in p.hole_rings()],
                       'parent': p.parent, 'hinge': p.hinge, 'angle': p.angle, 'sgn': sgn, 'art': bool(p.art)})
    return {'key': pr.key, 'title': pr.title, 'sheet': [pr.SW, pr.SH], 'pad': PAD, 'mode': pr.mode, 'shift': shift, 'panels': panels}


def build_outputs(pr, shift, dpi=110, textures=True):
    out_art = art_group(pr, 'out')
    in_art = art_group(pr, 'in')
    marks = ''
    pages = {
        'art_outside': svg_page(pr, out_art),
        'art_inside': svg_page(pr, in_art),
        'dieline': svg_page(pr, dieline_group(pr, False)),
        'proof_outside': svg_page(pr, out_art + dieline_group(pr)),
    }
    for k, v in pages.items():
        open(os.path.join(pr.out, f'{k}.svg'), 'w', encoding='utf-8').write(v)
    docs = {k: to_pdf(pr, v, f'{pr.key}_{k}') for k, v in pages.items()}
    pf = fz.open()
    pf.insert_pdf(docs['art_outside'])
    pf.insert_pdf(docs['art_inside'])
    pf.save(os.path.join(pr.out, f'{pr.key}_print_artwork.pdf'))
    docs['dieline'].save(os.path.join(pr.out, f'{pr.key}_dieline.pdf'))
    if textures:
        docs['art_outside'][0].get_pixmap(dpi=dpi, alpha=False).save(os.path.join(pr.out, 'tex_outside.png'))
        docs['art_inside'][0].get_pixmap(dpi=dpi, alpha=False).save(os.path.join(pr.out, 'tex_inside.png'))
        docs['proof_outside'][0].get_pixmap(dpi=60, alpha=False).save(os.path.join(pr.out, 'proof.png'))
    json.dump(export_scene(pr, shift), open(os.path.join(pr.out, 'scene.json'), 'w'))
    # master editable svg (layers)
    master = (f'<g id="ART_OUTSIDE">{out_art}</g><g id="ART_INSIDE_MIRRORED" style="display:none">{in_art}</g>' + dieline_group(pr))
    open(os.path.join(pr.out, f'{pr.key}_dieline_master.svg'), 'w', encoding='utf-8').write(svg_page(pr, master))


# ---- dimension drawing helpers (labels carry data-mm so the page can switch mm / cm / in)
def dim_h(x0, x1, y, off=0, mm=None, cls='d'):
    mm = mm if mm is not None else abs(x1 - x0)
    yy = y + off
    return (f'<g class="{cls}"><path d="M{x0},{y} V{yy + (2 if off<0 else -2)} M{x1},{y} V{yy + (2 if off<0 else -2)} M{x0},{yy} H{x1}" />'
            f'<path d="M{x0},{yy} l2.4,-1.1 v2.2z M{x1},{yy} l-2.4,-1.1 v2.2z" class="ah"/>'
            f'<text x="{(x0+x1)/2}" y="{yy-1.6}" data-mm="{mm:.2f}" text-anchor="middle">{mm:.1f}</text></g>')


def dim_v(x, y0, y1, off=0, mm=None, cls='d'):
    mm = mm if mm is not None else abs(y1 - y0)
    xx = x + off
    return (f'<g class="{cls}"><path d="M{x},{y0} H{xx + (2 if off<0 else -2)} M{x},{y1} H{xx + (2 if off<0 else -2)} M{xx},{y0} V{y1}" />'
            f'<path d="M{xx},{y0} l-1.1,2.4 h2.2z M{xx},{y1} l-1.1,-2.4 h2.2z" class="ah"/>'
            f'<text x="{xx-1.8}" y="{(y0+y1)/2}" data-mm="{mm:.2f}" text-anchor="end" transform="rotate(-90 {xx-1.8} {(y0+y1)/2})" dy="0">{mm:.1f}</text></g>')


def dimmed_dieline(pr, dims_svg):
    content = f'<g id="art">{art_group(pr, "out")}</g>' + dieline_group(pr, False) + f'<g id="dims">{dims_svg}</g>'
    w, h = pr.SW + 2 * 22, pr.SH + 2 * 22
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-22 -22 {w:.2f} {h:.2f}" class="dieline-svg">{content}</svg>')
