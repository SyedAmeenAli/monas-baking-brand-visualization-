/* Mona's Baking: reactive layer. Hero parallax, draggable stickers, sprinkles, reveal-on-scroll, nav tracking,
   viewer glow, magnetic buttons, sticker-sheet peel, and the logo size studio. No dependencies. */
(() => {
  const BUILD = '20261110b';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;
  const $ = (q, r = document) => r.querySelector(q);
  const $$ = (q, r = document) => [...r.querySelectorAll(q)];
  const M = () => window.MONA || { fmt: (v) => Math.round(v * 10) / 10 + ' mm', unit: () => 'mm', apply() {} };

  // ---------------------------------------------------------- hero parallax
  const hero = $('.hero');
  if (hero && !reduce) {
    const layers = $$('.ly', hero), fls = $$('.fl', hero);
    let tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
    const tick = () => {
      cx += (tx - cx) * 0.08; cy += (ty - cy) * 0.08;
      layers.forEach((l) => { const d = +l.dataset.d; l.style.setProperty('--px', (-cx * d).toFixed(2) + 'px'); l.style.setProperty('--py', (-cy * d * 0.6).toFixed(2) + 'px'); });
      fls.forEach((f) => { const d = +f.dataset.d; f.style.setProperty('--px', (cx * d).toFixed(2) + 'px'); f.style.setProperty('--py', (cy * d * 0.6).toFixed(2) + 'px'); });
      raf = (Math.abs(tx - cx) > 0.002 || Math.abs(ty - cy) > 0.002) ? requestAnimationFrame(tick) : 0;
    };
    const aim = (x, y) => { const r = hero.getBoundingClientRect(); tx = (x - r.left) / r.width - 0.5; ty = (y - r.top) / r.height - 0.5; if (!raf) raf = requestAnimationFrame(tick); };
    hero.addEventListener('pointermove', (e) => aim(e.clientX, e.clientY));
    hero.addEventListener('pointerleave', () => { tx = 0; ty = 0; if (!raf) raf = requestAnimationFrame(tick); });
    // the layers have a CSS transition for polish; the rAF smoothing already eases, so shorten it
    layers.forEach((l) => { l.style.transition = 'none'; });

    // draggable stickers with a little throw
    fls.forEach((f) => {
      let sx, sy, ox, oy, vx = 0, vy = 0, lx, ly, id = null, fly = 0;
      f.addEventListener('pointerdown', (e) => {
        cancelAnimationFrame(fly); id = e.pointerId; f.setPointerCapture(id); f.classList.add('drag');
        sx = e.clientX; sy = e.clientY; ox = parseFloat(f.style.getPropertyValue('--dx')) || 0; oy = parseFloat(f.style.getPropertyValue('--dy')) || 0; lx = sx; ly = sy; vx = vy = 0;
        f.style.zIndex = 5; e.stopPropagation();
      });
      f.addEventListener('pointermove', (e) => {
        if (id !== e.pointerId) return;
        vx = e.clientX - lx; vy = e.clientY - ly; lx = e.clientX; ly = e.clientY;
        f.style.setProperty('--dx', (ox + e.clientX - sx) + 'px'); f.style.setProperty('--dy', (oy + e.clientY - sy) + 'px');
        f.style.setProperty('--rr', (parseFloat(getComputedStyle(f).getPropertyValue('--r')) + vx * 0.6) + 'deg');
        e.stopPropagation();
      });
      const up = () => {
        if (id === null) return; id = null; f.classList.remove('drag'); f.style.removeProperty('--rr');
        const glide = () => {
          vx *= 0.92; vy *= 0.92;
          f.style.setProperty('--dx', ((parseFloat(f.style.getPropertyValue('--dx')) || 0) + vx) + 'px'); f.style.setProperty('--dy', ((parseFloat(f.style.getPropertyValue('--dy')) || 0) + vy) + 'px');
          if (Math.abs(vx) + Math.abs(vy) > 0.4) fly = requestAnimationFrame(glide);
        };
        glide();
      };
      f.addEventListener('pointerup', up); f.addEventListener('pointercancel', up);
    });

    // sprinkles on click
    const COL = ['#F7B6C7', '#D9526F', '#8B4A3A', '#FFF6F6', '#E98CA8', '#F6DDA8'];
    hero.addEventListener('click', (e) => {
      if (e.target.closest('a,.fl')) return;
      for (let i = 0; i < 18; i++) {
        const s = document.createElement('i'); s.className = 'spr' + (i % 2 ? ' bar' : '');
        s.style.background = COL[i % COL.length]; document.body.appendChild(s);
        const a = Math.random() * Math.PI * 2, v = 60 + Math.random() * 130, rot = Math.random() * 540;
        s.animate([{ transform: `translate(${e.clientX}px,${e.clientY}px) rotate(0)`, opacity: 1 },
          { transform: `translate(${e.clientX + Math.cos(a) * v}px,${e.clientY + Math.sin(a) * v + 90}px) rotate(${rot}deg)`, opacity: 0 }],
          { duration: 800 + Math.random() * 500, easing: 'cubic-bezier(.2,.7,.3,1)' }).onfinish = () => s.remove();
      }
    });
  }

  // ---------------------------------------------------------- scroll progress, reveal, active nav
  const bar = document.createElement('div'); bar.className = 'progress'; document.body.appendChild(bar);
  const onScroll = () => { const h = document.documentElement; bar.style.setProperty('--p', (h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)).toFixed(4)); };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  const rv = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); rv.unobserve(e.target); } }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  $$('.stage>.wrap>header, .grid3d, .flat, .sthead, .stgrid, .bench .wrap>*, .brand .wrap>*').forEach((n) => { if (!reduce) { n.setAttribute('data-rv', ''); rv.observe(n); } });
  const links = $$('.jump a');
  const nav = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) links.forEach((a) => {
      const on = a.getAttribute('href') === '#' + e.target.id; a.classList.toggle('on', on);
      const bar = a.parentElement; if (on && bar.scrollWidth > bar.clientWidth) bar.scrollTo({ left: a.offsetLeft - (bar.clientWidth - a.offsetWidth) / 2, behavior: 'smooth' });
    });
  }), { rootMargin: '-45% 0px -50% 0px' });
  $$('main section[id]').forEach((s) => nav.observe(s));

  // ---------------------------------------------------------- viewer glow + magnetic buttons
  $$('.viewer').forEach((v) => v.addEventListener('pointermove', (e) => { const r = v.getBoundingClientRect(); v.style.setProperty('--mx', (e.clientX - r.left) + 'px'); v.style.setProperty('--my', (e.clientY - r.top) + 'px'); }));
  if (fine && !reduce) $$('.btn, .dl a').forEach((b) => {
    b.addEventListener('pointermove', (e) => { const r = b.getBoundingClientRect(); b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.18}px,${(e.clientY - r.top - r.height / 2) * 0.3 - 2}px)`; });
    b.addEventListener('pointerleave', () => { b.style.transform = ''; });
  });

  // ---------------------------------------------------------- sticker sheet
  const sheet = $('#stickersheet');
  if (sheet) {
    fetch(sheet.dataset.sheet + '?v=' + BUILD).then((r) => r.text()).then((t) => {
      const svg = new DOMParser().parseFromString(t, 'image/svg+xml').documentElement;
      sheet.replaceChildren(document.importNode(svg, true));
      const name = $('#pname'), size = $('#psize'), info = $('#peelinfo');
      let cur = null;
      const show = () => {
        if (!cur) return;
        const w = +cur.dataset.w, h = +cur.dataset.h, m = M();
        name.textContent = cur.dataset.name; size.textContent = (cur.dataset.w === cur.dataset.h ? m.fmt(w) + ' across' : m.fmt(w) + ' x ' + m.fmt(h));
      };
      $$('.stk', sheet).forEach((g) => {
        g.setAttribute('tabindex', '0'); g.setAttribute('role', 'button'); g.setAttribute('aria-label', g.dataset.name + ' sticker');
        const pick = () => {
          $$('.stk.peel', sheet).forEach((x) => x.classList.remove('peel')); g.classList.add('peel'); cur = g; show();
          info.classList.remove('bump'); void info.offsetWidth; info.classList.add('bump');
        };
        g.addEventListener('click', pick);
        g.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } });
      });
      document.addEventListener('unit', show);
    });
  }

  // ---------------------------------------------------------- logo studio
  const lpbox = $('#lpbox'), range = $('#lpsize');
  if (lpbox && range) {
    const note = $('#lpnote'), read = $('#lpread'), plate = $('#logoplate');
    const PXW = 960; // pixel width of the approved logo file
    const MMPX = 3.2; // preview scale, px per mm
    const apply = () => {
      const mm = +range.value, m = M();
      lpbox.style.setProperty('--lw', Math.max(40, mm * MMPX) + 'px');
      read.textContent = m.fmt(mm);
      const dpi = Math.round(PXW / (mm / 25.4));
      let msg = `At ${m.fmt(mm)} wide the logo file prints at ${dpi} dpi.`;
      const warn = dpi < 300 || mm < 25;
      if (mm < 25) msg = `Below 25 mm the cookie and the word BAKING stop reading. ` + msg;
      else if (dpi < 300) msg += ` That is soft for print; larger sizes need a vector version of the logo.`;
      else msg += ` Sharp enough for print.`;
      note.textContent = msg; note.classList.toggle('warn', warn);
      $$('[data-lw]').forEach((c) => c.setAttribute('aria-pressed', String(+c.dataset.lw === mm)));
    };
    range.addEventListener('input', apply);
    $$('[data-lw]').forEach((c) => c.addEventListener('click', () => { range.value = c.dataset.lw; apply(); }));
    $('#lpclear').addEventListener('change', (e) => lpbox.classList.toggle('nocs', !e.target.checked));
    document.addEventListener('unit', apply);
    // drag on the plate to scale
    let down = false, y0 = 0, v0 = 0;
    plate.addEventListener('wheel', (e) => { if (!e.ctrlKey && !e.shiftKey) return; e.preventDefault(); range.value = Math.min(200, Math.max(12, +range.value - Math.sign(e.deltaY) * 4)); apply(); }, { passive: false });
    apply();
  }

})();
