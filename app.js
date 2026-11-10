const BUILD = '20261110b';
/* Mona's Baking packaging site: units, dielines, items, and the 3D folding stage.
   The 3D model is folded live from the same panel tree (hinges + angles) that the dieline is cut from. */
(() => {
  // ------------------------------------------------------------ helpers
  const parseSvg = (txt) => {
    const doc = new DOMParser().parseFromString(txt, 'image/svg+xml');
    return document.importNode(doc.documentElement, true);
  };
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; };

  // ------------------------------------------------------------ units
  let unit = 'mm';
  const fmt = (mm) => {
    const v = parseFloat(mm);
    if (unit === 'mm') return (Math.round(v * 10) / 10).toString();
    if (unit === 'cm') return (Math.round(v * 10) / 100).toString().replace(/(\.\d)$/, '$1');
    return (v / 25.4).toFixed(2) + '"';
  };
  const suffix = () => (unit === 'in' ? '' : ' ' + unit);
  function applyUnits(root = document) {
    root.querySelectorAll('[data-mm]').forEach((n) => {
      n.textContent = fmt(n.dataset.mm) + (n.closest('svg') ? '' : suffix());
    });
  }
  document.querySelectorAll('.units button').forEach((b) => b.addEventListener('click', () => {
    unit = b.dataset.u;
    document.querySelectorAll('.units button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    applyUnits();
    document.dispatchEvent(new CustomEvent('unit'));
  }));
  window.MONA = { fmt: (mm) => fmt(mm) + suffix(), unit: () => unit, apply: applyUnits };

  // ------------------------------------------------------------ dielines

  // ------------------------------------------------------------ pan / zoom for flat templates (pinch, ctrl+wheel / trackpad pinch, drag, double-tap, buttons)
  function panZoom(host, svg) {
    const wrap = el('div', 'pz'), inner = el('div', 'pzin');
    inner.appendChild(svg); wrap.appendChild(inner); host.replaceChildren(wrap);
    let s = 1, tx = 0, ty = 0; const MAX = 8, P = new Map();
    const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
    const apply = () => {
      const w = wrap.clientWidth, h = inner.offsetHeight;
      tx = clamp(tx, w - w * s, 0); ty = clamp(ty, h - h * s, 0);
      inner.style.transform = `translate(${tx}px,${ty}px) scale(${s})`;
      wrap.style.touchAction = s > 1.001 ? 'none' : 'pan-y'; wrap.classList.toggle('zoomed', s > 1.001);
      if (label) label.textContent = Math.round(s * 100) + '%';
    };
    const fitH = () => { wrap.style.height = inner.offsetHeight + 'px'; apply(); };
    const zoomAt = (cx, cy, ns) => { ns = clamp(ns, 1, MAX); const k = ns / s; tx = cx - (cx - tx) * k; ty = cy - (cy - ty) * k; s = ns; apply(); };
    const rel = (e) => { const r = wrap.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
    let pd = 0, pcx = 0, pcy = 0, lastTap = 0, moved = 0;
    wrap.addEventListener('pointerdown', (e) => {
      P.set(e.pointerId, [e.clientX, e.clientY]); wrap.setPointerCapture(e.pointerId); moved = 0;
      if (P.size === 2) { const [a, b] = [...P.values()]; pd = Math.hypot(a[0] - b[0], a[1] - b[1]); pcx = (a[0] + b[0]) / 2; pcy = (a[1] + b[1]) / 2; }
    });
    wrap.addEventListener('pointermove', (e) => {
      if (!P.has(e.pointerId)) return;
      const prev = P.get(e.pointerId); P.set(e.pointerId, [e.clientX, e.clientY]);
      if (P.size === 2) {
        const [a, b] = [...P.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]), cx = (a[0] + b[0]) / 2, cy = (a[1] + b[1]) / 2, r = wrap.getBoundingClientRect();
        tx += cx - pcx; ty += cy - pcy; zoomAt(cx - r.left, cy - r.top, s * (d / (pd || d))); pd = d; pcx = cx; pcy = cy; moved = 99;
      } else if (P.size === 1 && s > 1.001) {
        tx += e.clientX - prev[0]; ty += e.clientY - prev[1]; moved += Math.abs(e.clientX - prev[0]) + Math.abs(e.clientY - prev[1]); apply();
      }
    });
    const up = (e) => {
      const was = P.size; P.delete(e.pointerId);
      if (was === 1 && moved < 8 && e.pointerType === 'touch') { // double-tap to zoom
        const now = performance.now(); if (now - lastTap < 320) { const [x, y] = rel(e); zoomAt(x, y, s > 1.01 ? 1 : 2.6); lastTap = 0; } else lastTap = now;
      }
      if (P.size === 1) { const [only] = [...P.values()]; pd = 0; void only; }
    };
    wrap.addEventListener('pointerup', up); wrap.addEventListener('pointercancel', up);
    wrap.addEventListener('dblclick', (e) => { if (e.pointerType === 'touch') return; const [x, y] = rel(e); zoomAt(x, y, s > 1.01 ? 1 : 2.6); });
    wrap.addEventListener('wheel', (e) => { if (!(e.ctrlKey || e.metaKey)) return; e.preventDefault(); const [x, y] = rel(e); zoomAt(x, y, s * Math.exp(-e.deltaY * (e.deltaMode ? 0.05 : 0.01))); }, { passive: false });
    new ResizeObserver(fitH).observe(wrap);
    // controls
    const bar = host.closest('.flat') && host.closest('.flat').querySelector('.bar'); let label = null;
    if (bar && !bar.querySelector('.zoom')) {
      const z = el('div', 'zoom'); label = el('span', 'zl', '100%');
      const mk = (t, aria, fn) => { const b = el('button', 'chip', t); b.type = 'button'; b.setAttribute('aria-label', aria); b.onclick = fn; return b; };
      const mid = () => [wrap.clientWidth / 2, wrap.clientHeight / 2];
      z.append(mk('−', 'Zoom out', () => zoomAt(...mid(), s / 1.6)), label, mk('+', 'Zoom in', () => zoomAt(...mid(), s * 1.6)), mk('Fit', 'Fit to screen', () => { s = 1; tx = ty = 0; apply(); }),
        el('span', 'zh', 'pinch, Ctrl + scroll, or double-tap to zoom; drag to move'));
      bar.appendChild(z);
    }
    requestAnimationFrame(fitH);
  }
  const loadDieline = async (box) => {
    const svg = parseSvg(await (await fetch(box.dataset.dieline + '?v=' + BUILD)).text());
    const vb = svg.viewBox.baseVal; svg.style.setProperty('--dfs', (vb.width * 0.0185).toFixed(2) + 'px'); svg.style.setProperty('--dsw', (vb.width * 0.0005).toFixed(3));
    if (matchMedia('(max-width: 900px)').matches) svg.style.setProperty('--dfs', (vb.width * 0.03).toFixed(2) + 'px');
    panZoom(box, svg);
    applyUnits(box);
  };
  const dio = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { dio.unobserve(e.target); loadDieline(e.target); } }), { rootMargin: '700px' });
  document.querySelectorAll('[data-dieline]').forEach((box) => dio.observe(box));
  document.querySelectorAll('.flat').forEach((flat) => {
    flat.querySelectorAll('input[data-layer]').forEach((cb) => cb.addEventListener('change', () => {
      flat.querySelector('.sheet').classList.toggle('hide-' + cb.dataset.layer, !cb.checked);
    }));
  });

  // ------------------------------------------------------------ items, all at one scale
  (async () => {
    const list = await (await fetch('assets/items/items.json?v=' + BUILD)).json();
    const host = document.getElementById('items');
    const PX = 3.1; // px per mm so every item shows its true relative size
    for (const it of list) {
      const svg = parseSvg(await (await fetch(`assets/items/${it.key}.svg?v=${BUILD}`)).text());
      const fig = el('figure', 'item');
      const wpx = Math.round((it.w + 28) * PX);
      fig.style.width = wpx + 'px';
      const art = el('div', 'art'); svg.style.width = wpx + 'px'; art.appendChild(svg);
      const cap = el('figcaption'); cap.append(el('h3', '', it.title), el('p', '', it.spec));
      fig.append(art, cap);
      host.appendChild(fig);
    }
    applyUnits(host);
  })();

  // ------------------------------------------------------------ 3D stage
  const POSES = {
    box4: { closed: null, open: { BL: -5, FL: -5, HB: 0, HF: 0, TA: 0, TH: 0 } },
    tuck: { closed: null, open: { TTT: -25, TGT: 0, TTB: 90, DSRT: 90, DSLT: 90 } },
    bag: { closed: null },
    cupbox: { closed: null, open: { TTT: -25, TGT: 0, TTB: 90, DSRT: 90, DSLT: 90 } },
    bento: { closed: null, open: { TTT: -25, TGT: 0, TTB: 90, DSRT: 90, DSLT: 90 } },
    cup: { closed: null, open: {} },
  };
  const Q = {
    tray: new THREE.Matrix4().set(1, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 1),
    tube: new THREE.Matrix4(),
  };

  function foldMats(data, t, over) {
    const byName = {}, M = {};
    data.panels.forEach((p) => (byName[p.name] = p));
    const get = (n) => {
      if (M[n]) return M[n];
      const p = byName[n];
      if (!p.parent) return (M[n] = new THREE.Matrix4());
      const Mp = get(p.parent);
      const [[x0, y0], [x1, y1]] = p.hinge;
      const h = new THREE.Vector3(x1 - x0, -(y1 - y0), 0).normalize();
      const ang = ((over && over[n] !== undefined ? over[n] : p.angle) * Math.PI) / 180;
      const phi = -ang * p.sgn * t;
      const A = new THREE.Matrix4().makeTranslation(x0, -y0, 0)
        .multiply(new THREE.Matrix4().makeRotationAxis(h, phi))
        .multiply(new THREE.Matrix4().makeTranslation(-x0, y0, 0));
      return (M[n] = Mp.clone().multiply(A));
    };
    data.panels.forEach((p) => get(p.name));
    return M;
  }

  class Stage {
    constructor(section) {
      this.sec = section;
      this.key = section.dataset.product;
      this.mode = section.dataset.front;
      this.host = section.querySelector('.viewer');
      this.t = 1; this.pose = 'closed'; this.az = 0; this.el = 0.3; this.dist = 600;
      this.init();
    }
    async init() {
      const base = `assets/${this.key}/`;
      this.data = await (await fetch(base + 'scene.json?v=' + BUILD)).json();
      const R = (this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true }));
      const phone = matchMedia('(max-width: 900px)').matches; this.phone = phone;
      R.setPixelRatio(Math.min(phone ? 1.5 : 2, devicePixelRatio));
      R.outputEncoding = THREE.sRGBEncoding;
      R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap;
      const lm = this.host.querySelector('.loadmsg'); if (lm) lm.remove();
      this.host.prepend(R.domElement);
      this.scene = new THREE.Scene();
      this.cam = new THREE.PerspectiveCamera(24, 1, 5, 6000);
      this.scene.add(new THREE.HemisphereLight(0xffffff, 0xf3c9d6, 0.95));
      const sun = new THREE.DirectionalLight(0xffffff, 0.55);
      const ext = Math.max(450, 0.45 * Math.max(...this.data.sheet)), k = ext / 450;
      sun.position.set(-300 * k, 700 * k, -400 * k); sun.castShadow = true;
      sun.shadow.mapSize.set(this.phone ? 1024 : 2048, this.phone ? 1024 : 2048);
      Object.assign(sun.shadow.camera, { left: -ext, right: ext, top: ext, bottom: -ext, near: 50, far: 2200 * k });
      sun.shadow.bias = -0.0004; this.scene.add(sun);
      const gr = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShadowMaterial({ opacity: 0.16 }));
      gr.rotation.x = -Math.PI / 2; gr.position.y = -0.6; gr.receiveShadow = true; this.scene.add(gr);
      const L = new THREE.TextureLoader();
      const tx = (u) => { const t = L.load(u + '?v=' + BUILD, () => this.render()); t.encoding = THREE.sRGBEncoding; t.anisotropy = 8; return t; };
      this.tOut = tx(base + 'tex_outside.png'); this.tIn = tx(base + 'tex_inside.png');
      this.group = new THREE.Group(); this.scene.add(this.group);
      this.meshes = [];
      this.build();
      this.ui();
      this.bind();
      this.apply();
      this.setView('iso');
      (this.ro = new ResizeObserver(() => this.resize())).observe(this.host);
      this.resize();
    }
    poseDef() { return POSES[this.sec.dataset.pose || this.key] || (this.mode === 'tube' ? POSES.tuck : POSES.box4); }
    geo(p, side) {
      const d = this.data, [SW, SH] = d.sheet, PAD = d.pad;
      const sh = new THREE.Shape(p.ring.map((q) => new THREE.Vector2(q[0], -q[1])));
      p.holes.forEach((h) => sh.holes.push(new THREE.Path(h.map((q) => new THREE.Vector2(q[0], -q[1])))));
      const g = new THREE.ShapeGeometry(sh, 16), pos = g.attributes.position, uv = new Float32Array(pos.count * 2);
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), Y = -pos.getY(i);
        uv[2 * i] = (side === 0 ? x + PAD : SW - x + PAD) / (SW + 2 * PAD);
        uv[2 * i + 1] = 1 - (Y + PAD) / (SH + 2 * PAD);
      }
      g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
      return g;
    }
    build() {
      this.data.panels.forEach((p) => {
        const mo = new THREE.Mesh(this.geo(p, 0), new THREE.MeshStandardMaterial({ map: this.tOut, side: THREE.FrontSide, roughness: 0.88 }));
        const mi = new THREE.Mesh(this.geo(p, 1), new THREE.MeshStandardMaterial({ map: this.tIn, side: THREE.BackSide, roughness: 0.92 }));
        const pts = p.ring.map((q) => new THREE.Vector3(q[0], -q[1], 0)); pts.push(pts[0].clone());
        const ln = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: 0x8b4a3a, transparent: true, opacity: 0.5 }));
        [mo, mi, ln].forEach((m) => { m.matrixAutoUpdate = false; m.castShadow = true; m.receiveShadow = true; this.group.add(m); this.meshes.push({ m, name: p.name, role: p.role }); });
      });
      (this.data.cords || []).forEach((c) => { // twisted-paper handles ride on their panel
        const pts = c.pts.map((q) => new THREE.Vector3(q[0], -q[1], q[2]));
        const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 80, c.r, 8, false), new THREE.MeshStandardMaterial({ color: c.color, roughness: 0.9 }));
        m.matrixAutoUpdate = false; m.castShadow = true; this.group.add(m);
        this.meshes.push({ m, name: c.panel, role: 'cord' });
      });
    }
    apply() {
      const M = foldMats(this.data, this.t, this.poseDef()[this.pose]);
      const S = new THREE.Matrix4().makeTranslation(...this.data.shift);
      this.meshes.forEach((o) => {
        o.m.matrix.copy(S).multiply(Q[this.mode]).multiply(M[o.name]);
        const inset = { glue: 0.9, dust: 1.3, tongue: 1.1, under: 2.2, under2: 3.4 }[o.role];
        if (inset && this.t > 0.02) { // flaps tuck just inside the panel they sit against (avoids z-fighting)
          const n = new THREE.Vector3(0, 0, 1).transformDirection(o.m.matrix);
          o.m.matrix.premultiply(new THREE.Matrix4().makeTranslation(-n.x * inset, -n.y * inset, -n.z * inset));
        }
        o.m.matrixWorldNeedsUpdate = true;
      });
      this.render();
    }
    fit() {
      // frame the folded, closed box so every view has the same scale
      const M = foldMats(this.data, 1, null), S = new THREE.Matrix4().makeTranslation(...this.data.shift);
      const box = new THREE.Box3();
      this.data.panels.forEach((p) => p.ring.forEach((q) => {
        box.expandByPoint(new THREE.Vector3(q[0], -q[1], 0).applyMatrix4(M[p.name]).applyMatrix4(Q[this.mode]).applyMatrix4(S));
      }));
      (this.data.cords || []).forEach((c) => c.pts.forEach((q) => box.expandByPoint(new THREE.Vector3(q[0], -q[1], q[2]).applyMatrix4(M[c.panel]).applyMatrix4(Q[this.mode]).applyMatrix4(S))));
      this.center = box.getCenter(new THREE.Vector3());
      this.radius = box.getSize(new THREE.Vector3()).length() / 2;
    }
    ui() {
      this.fit();
      const bar = el('div', 'vc');
      const chips = el('div', 'chips');
      ['iso', 'front', 'back', 'left', 'right', 'top', 'bottom'].forEach((v) => {
        const b = el('button', 'chip', v); b.dataset.v = v; b.onclick = () => this.setView(v); chips.appendChild(b);
      });
      const pose = el('button', 'chip', 'open lid'); pose.setAttribute('aria-pressed', 'false');
      pose.onclick = () => { this.pose = this.pose === 'open' ? 'closed' : 'open'; pose.setAttribute('aria-pressed', String(this.pose === 'open')); this.apply(); };
      if (this.poseDef().open) chips.appendChild(pose);
      const f = el('label', 'fold');
      const rng = document.createElement('input');
      Object.assign(rng, { type: 'range', min: 0, max: 1, step: 0.005, value: 1 }); rng.setAttribute('aria-label', 'Fold amount');
      f.append('flat ', rng, ' folded');
      rng.oninput = () => { this.t = parseFloat(rng.value); this.apply(); };
      const play = el('button', 'chip', 'fold it');
      play.onclick = () => {
        const t0 = performance.now();
        const go = (now) => {
          const k = Math.min(1, (now - t0) / 3200), e = 1 - Math.pow(1 - k, 3);
          this.t = e; rng.value = e; this.apply(); if (k < 1) requestAnimationFrame(go);
        };
        this.t = 0; requestAnimationFrame(go);
      };
      const glb = el('button', 'chip', 'download 3D (.glb)');
      glb.onclick = () => this.exportGLB();
      bar.append(chips, play, glb, f);
      const mq = matchMedia('(max-width: 900px)'), put = () => (mq.matches ? this.host.after(bar) : this.host.appendChild(bar));
      put(); mq.addEventListener('change', put);
    }
    exportGLB() { // the model exactly as posed now, in metres, without the ink outline lines
      if (!THREE.GLTFExporter) return;
      const root = new THREE.Group(); root.scale.setScalar(0.001);
      const copy = this.group.clone(true); const drop = [];
      copy.traverse((o) => { if (o.isLine) drop.push(o); });
      drop.forEach((o) => o.parent.remove(o));
      root.add(copy); root.updateMatrixWorld(true);
      new THREE.GLTFExporter().parse(root, (buf) => {
        const u = URL.createObjectURL(new Blob([buf], { type: 'model/gltf-binary' }));
        const a = document.createElement('a'); a.href = u; a.download = `monas-${this.key}.glb`; a.click();
        setTimeout(() => URL.revokeObjectURL(u), 4000);
      }, { binary: true });
    }
    setView(v) {
      const fa = this.mode === 'tray' ? Math.PI : 0;
      const M = { iso: [fa + 0.62, 0.42], front: [fa, 0.12], back: [fa + Math.PI, 0.12], left: [fa - Math.PI / 2, 0.12], right: [fa + Math.PI / 2, 0.12], top: [fa, 1.5], bottom: [fa, -1.5] }[v];
      [this.az, this.el] = M; this.dist = this.radius * 4.2;
      this.sec.querySelectorAll('.chip[data-v]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.v === v)));
      this.place();
    }
    place() {
      const d = this.dist, c = this.center;
      this.cam.up.set(0, 1, 0);
      if (Math.abs(this.el) > 1.45) { const s = this.mode === 'tray' ? 1 : -1; this.cam.up.set(0, 0, s * (this.el > 0 ? 1 : -1)); }
      this.cam.position.set(c.x + d * Math.cos(this.el) * Math.sin(this.az), c.y + d * Math.sin(this.el), c.z + d * Math.cos(this.el) * Math.cos(this.az));
      this.cam.lookAt(c); this.render();
    }
    bind() {
      const cv = this.renderer.domElement; let drag = false, lx = 0, ly = 0;
      const ptr = new Map(); let pd = 0;
      cv.addEventListener('pointerdown', (e) => { ptr.set(e.pointerId, [e.clientX, e.clientY]); drag = ptr.size === 1; lx = e.clientX; ly = e.clientY; cv.setPointerCapture(e.pointerId); if (ptr.size === 2) { const [a, b] = [...ptr.values()]; pd = Math.hypot(a[0] - b[0], a[1] - b[1]); } });
      cv.addEventListener('pointermove', (e) => {
        if (!ptr.has(e.pointerId)) return; ptr.set(e.pointerId, [e.clientX, e.clientY]);
        if (ptr.size === 2) { const [a, b] = [...ptr.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]); if (pd) { this.dist = Math.max(this.radius * 1.4, Math.min(this.radius * 9, this.dist * (pd / d))); this.place(); } pd = d; }
      });
      const gone = (e) => { ptr.delete(e.pointerId); pd = 0; drag = false; };
      cv.addEventListener('pointerup', gone); cv.addEventListener('pointercancel', gone);
      
      cv.addEventListener('pointermove', (e) => {
        if (!drag) return;
        this.az -= (e.clientX - lx) * 0.008;
        if (e.pointerType !== 'touch') this.el = Math.max(-1.45, Math.min(1.45, this.el + (e.clientY - ly) * 0.006));
        lx = e.clientX; ly = e.clientY;
        this.sec.querySelectorAll('.chip[data-v]').forEach((b) => b.setAttribute('aria-pressed', 'false'));
        this.place();
      });
      cv.addEventListener('wheel', (e) => {
        e.preventDefault();
        this.dist = Math.max(this.radius * 1.6, Math.min(this.radius * 9, this.dist * (1 + Math.sign(e.deltaY) * 0.07)));
        this.place();
      }, { passive: false });
    }
    resize() {
      const w = this.host.clientWidth, h = this.host.clientHeight;
      this.renderer.setSize(w, h, false); this.cam.aspect = w / h; this.cam.updateProjectionMatrix(); this.render();
    }
    render() { if (this.renderer) this.renderer.render(this.scene, this.cam); }
  }

  // dessert cup: the blank is an annular sector; each vertex slides from its flat (r, a) spot to its cone spot
  class ConeStage extends Stage {
    fit() { const c = this.data.cone; this.center = new THREE.Vector3(0, c.h / 2, 0); this.radius = Math.max(2.78 * c.Rt, 1.5 * c.h); }
    build() {
      const c = (this.c = this.data.cone), [SW, SH] = this.data.sheet, PAD = this.data.pad;
      const NR = 10, NA = 120, n = (NR + 1) * (NA + 1);
      const rm = (c.Ri + c.Ro) / 2, uv = new Float32Array(n * 2), rr = new Float32Array(n), aa = new Float32Array(n);
      for (let i = 0, k = 0; i <= NR; i++) for (let j = 0; j <= NA; j++, k++) {
        const r = c.Ri + ((c.Ro - c.Ri) * i) / NR, a = -c.theta / 2 + (c.theta * j) / NA;
        const xs = c.ox + r * Math.sin(a), ys = c.oy + r * Math.cos(a);
        rr[k] = r; aa[k] = a;
        uv.set([(xs + PAD) / (SW + 2 * PAD), 1 - (ys + PAD) / (SH + 2 * PAD)], 2 * k);
      }
      this.rr = rr; this.aa = aa; this.rm = rm;
      const idx = [];
      for (let i = 0; i < NR; i++) for (let j = 0; j < NA; j++) { const a = i * (NA + 1) + j, b = a + 1, d = a + NA + 1, e = d + 1; idx.push(a, d, b, b, d, e); }
      const g = (this.sg = new THREE.BufferGeometry());
      g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
      g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); g.setIndex(idx);
      const mo = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ map: this.tOut, side: THREE.FrontSide, roughness: 0.85 }));
      const mi = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0xfffdfd, side: THREE.BackSide, roughness: 0.9 }));
      [mo, mi].forEach((m) => { m.castShadow = true; m.receiveShadow = true; this.group.add(m); });
      this.extra = new THREE.Group();
      const ds = new THREE.MeshStandardMaterial({ color: 0xf7b6c7, roughness: 0.7 }), cr = new THREE.MeshStandardMaterial({ color: 0xfff6f6, roughness: 0.7 });
      const lay = (r0, r1, y0, y1, m) => { const q = new THREE.Mesh(new THREE.CylinderGeometry(r1, r0, y1 - y0, 40), m); q.position.y = (y0 + y1) / 2; q.castShadow = true; this.extra.add(q); };
      const f = c.h / 75, gk = c.Rt / 45;
      const rAt = (y) => c.Rb + ((c.Rt - c.Rb) * y) / c.h - 0.8;
      lay(rAt(f), rAt(26 * f), f, 26 * f, new THREE.MeshStandardMaterial({ color: 0x8b4a3a, roughness: 0.8 }));
      lay(rAt(26 * f), rAt(48 * f), 26 * f, 48 * f, ds); lay(rAt(48 * f), rAt(66 * f), 48 * f, 66 * f, cr);
      const ch = new THREE.Mesh(new THREE.SphereGeometry(5.5 * gk, 20, 14), new THREE.MeshStandardMaterial({ color: 0xd9526f, roughness: 0.4 }));
      ch.position.y = 71 * f; ch.castShadow = true; this.extra.add(ch);
      const base = new THREE.Mesh(new THREE.CircleGeometry(c.Rb, 40), new THREE.MeshStandardMaterial({ color: 0xf7b6c7, side: THREE.DoubleSide }));
      base.rotation.x = Math.PI / 2; this.extra.add(base);
      this.dome = new THREE.Mesh(new THREE.SphereGeometry(c.Rt + 0.5, 40, 16, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0.22, roughness: 0.1, side: THREE.DoubleSide, depthWrite: false }));
      this.dome.scale.y = 0.7; this.dome.position.y = c.h;
      this.extra.add(this.dome); this.group.add(this.extra);
    }
    shape(t) { // roll the fan into a cone (printed face outside), then turn it over so the rim is on top
      const c = this.c, P = this.sg.attributes.position.array, n = this.rr.length;
      const e = Math.min(1, t / 0.72), f = Math.max(0, Math.min(1, (t - 0.72) / 0.28)), ff = f * f * (3 - 2 * f);
      const sf = c.Rt / c.Ro, s = 1 + (sf - 1) * e, cs = Math.sqrt(Math.max(0, 1 - s * s));
      const th = Math.PI * ff, ct = Math.cos(th), st = Math.sin(th), hc = c.h / 2;
      for (let k = 0; k < n; k++) {
        const r = this.rr[k], a = this.aa[k], phi = a / s, rho = r * s;
        const x = rho * Math.sin(phi), z = rho * Math.cos(phi) - this.rm * (1 - e);
        const y = (c.Ro - r) * cs + 0.3;   // the rim stays on the ground while the fan rolls
        const yy = hc + (y - hc) * ct - z * st, zz = (y - hc) * st + z * ct;
        P[3 * k] = x; P[3 * k + 1] = yy; P[3 * k + 2] = zz;
      }
    }
    apply() {
      this.shape(this.t);
      this.sg.attributes.position.needsUpdate = true; this.sg.computeVertexNormals(); this.sg.computeBoundingSphere();
      this.extra.visible = this.t > 0.985; this.dome.visible = this.pose !== 'open';
      this.render();
    }
  }

  // lazy-start each stage when it nears the viewport (keeps WebGL contexts few)
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting && !e.target._stage) { e.target._stage = new (e.target.dataset.product === 'cup' ? ConeStage : Stage)(e.target); window.__stages = (window.__stages || []).concat(e.target._stage); }
  }), { rootMargin: '300px' });
  document.querySelectorAll('.stage').forEach((s) => io.observe(s));
  applyUnits();
})();
