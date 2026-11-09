"""Write a mm DXF (R2010) per product with CUT / CREASE / GLUE / PERFORATION / BLEED / SAFE layers, Y up, sheet origin bottom-left.
Usage: python make_dxf.py <key>   (cake sizes: run with MONA_CAKE_IN set, key box4 or cakeN)"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import ezdxf
import render as R
import geom as g
import build as b

LAYERS = {'CUT': 6, 'CREASE': 4, 'GLUE': 2, 'PERFORATION': 3, 'BLEED': 5, 'SAFE': 94, 'INFO': 8}


def new_doc():
    d = ezdxf.new('R2010')
    d.header['$INSUNITS'] = 4
    for n, c in LAYERS.items():
        d.layers.add(n, color=c)
    d.layers.get('CREASE').dxf.linetype = 'DASHED' if 'DASHED' in d.linetypes else 'Continuous'
    return d


def info(msp, key, title, SW, SH):
    msp.add_text(f'{title} | sheet {SW:.1f} x {SH:.1f} mm | DRAFT - not validated by a manufacturer', dxfattribs={'layer': 'INFO', 'height': 4}).set_placement((0, -12))


def panel_product(pr):
    d = new_doc(); m = d.modelspace(); SH = pr.SH
    Y = lambda p: (p[0], SH - p[1])
    seen = set()
    for n, p in pr.P.items():
        for r, closed in b.runs(p.edges, g.CUT):
            pts = [Y(r[0].p0)]
            for e in r:
                pts += [Y(q) for q in e.pts[1:]]
            m.add_lwpolyline(pts, close=closed, dxfattribs={'layer': 'CUT'})
        for e in p.edges:
            if e.kind == g.CREASE:
                k = tuple(sorted([tuple(round(v, 2) for v in e.p0), tuple(round(v, 2) for v in e.p1)]))
                if k not in seen:
                    seen.add(k)
                    m.add_line(Y(e.p0), Y(e.p1), dxfattribs={'layer': 'CREASE'})
        for h in p.hole_rings():
            m.add_lwpolyline([Y(q) for q in h], close=True, dxfattribs={'layer': 'CUT'})
        if p.role == 'glue':
            m.add_lwpolyline([Y(q) for q in p.ring()], close=True, dxfattribs={'layer': 'GLUE'})
        elif p.role not in ('tongue', 'dust', 'under', 'under2') and p.art:
            m.add_lwpolyline([Y(q) for q in b.offset_ring(p, g.BLEED)], close=True, dxfattribs={'layer': 'BLEED'})
            try:
                m.add_lwpolyline([Y(q) for q in b.offset_ring(p, -g.SAFE, -2.0)], close=True, dxfattribs={'layer': 'SAFE'})
            except Exception:
                pass
    info(m, pr.key, pr.title, pr.SW, SH)
    return d


def cup():
    import make_cup as C
    d = new_doc(); m = d.modelspace()
    Y = lambda p: (p[0] + C.OX, C.SH - (p[1] + C.OY))
    m.add_lwpolyline([Y(p) for p in C.body], close=True, dxfattribs={'layer': 'CUT'})
    m.add_lwpolyline([Y(p) for p in C.tabp], close=True, dxfattribs={'layer': 'CUT'})
    m.add_lwpolyline([Y(p) for p in C.tabp], close=True, dxfattribs={'layer': 'GLUE'})
    m.add_circle((C.BCX, C.SH - C.BCY), C.BASE_R, dxfattribs={'layer': 'CUT'})
    m.add_circle((C.BCX, C.SH - C.BCY), C.BASE_R - 6, dxfattribs={'layer': 'CREASE'})
    a = C.TH / 2
    m.add_line(Y(C.pt(C.RI, a)), Y(C.pt(C.RO, a)), dxfattribs={'layer': 'CREASE'})
    info(m, 'cup', 'Dessert cup sleeve', C.SW, C.SH)
    return d, 'cup'


if __name__ == '__main__':
    key = sys.argv[1]
    out = os.path.join(R.SITE, 'assets', key)
    if key == 'cup' or os.environ.get('MONA_CUP_KEY') == key:
        d, _ = cup(); pr = None
    else:
        import make_boxes as MB, make_bag as MG, make_tube as MT
        if key in ('box4',) or key.startswith('cake'):
            pr, _ = MB.box4()
        elif key == 'tuck':
            pr, _ = MB.tuckbox()
        elif key == 'bag' or os.environ.get('MONA_BAG_KEY') == key:
            pr, _ = MG.make()
        else:
            pr, _ = MT.make(key)
        d = panel_product(pr)
    path = os.path.join(out, f'{key}_dieline.dxf')
    d.saveas(path)
    print('dxf', path, os.path.getsize(path))
