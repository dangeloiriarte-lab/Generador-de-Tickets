import math

FS_LABEL = 15
FS_TICK = 11
COLOR_TEXT = 'var(--svg-text, #64748b)'
COLOR_GRID = '#e2e8f0'

ESTADO_LABELS = {'abierto': 'Abiertos', 'en_proceso': 'En Proceso', 'pendiente': 'Pendientes', 'resuelto': 'Resueltos'}
ESTADO_COLORS = {'abierto': '#E86A6E', 'en_proceso': '#4DB8F7', 'pendiente': '#3347A0', 'resuelto': '#4DAF6E'}
TIPO_COLORS = {'Hardware': '#E86A6E', 'Software': '#5A63F7', 'Red': '#3347A0', 'Solicitud de servicio': '#4DAF6E'}


def _escape(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def _wrap(elem, href):
    if href:
        return f'<a xlink:href="{href}" href="{href}" target="_top" style="cursor:pointer;text-decoration:none;" class="chart-link">{elem}</a>'
    return elem


def svg_donut(data, labels, colors, w=480, h=340, inner_r=48, hrefs=None, explode=0, depth=0):
    cx = w // 2
    cy = 140
    r = 95
    ir = inner_r
    total = sum(data) or 1
    max_idx = data.index(max(data)) if data and explode > 0 else -1
    slices = []
    sa = -math.pi / 2
    for val in data:
        a = (val / total) * 2 * math.pi
        slices.append((sa, sa + a, val))
        sa += a
    paths = []
    if depth > 0 and ir == 0:
        for i, (ss, ee, val) in enumerate(slices):
            col = colors[i] if colors and i < len(colors) else '#64748b'
            darker_col = _adjust_color(col, -0.15)
            ma = ss + (ee - ss) / 2
            ocx, ocy = cx, cy
            if i == max_idx:
                ocx = cx + explode * math.cos(ma)
                ocy = cy + explode * math.sin(ma)
            x1 = ocx + r * math.cos(ss)
            y1 = ocy + r * math.sin(ss)
            x2 = ocx + r * math.cos(ee)
            y2 = ocy + r * math.sin(ee)
            la = 1 if (ee - ss) > math.pi else 0
            d_side = (f'M {x1:.1f},{y1:.1f} '
                      f'A {r},{r} 0 {la},1 {x2:.1f},{y2:.1f} '
                      f'L {x2:.1f},{y2 + depth:.1f} '
                      f'A {r},{r} 0 {la},0 {x1:.1f},{y1 + depth:.1f} Z')
            paths.append(f'<path d="{d_side}" fill="{darker_col}" stroke="none"/>')
        for i, (ss, ee, val) in enumerate(slices):
            col = colors[i] if colors and i < len(colors) else '#64748b'
            ma = ss + (ee - ss) / 2
            ocx, ocy = cx, cy
            if i == max_idx:
                ocx = cx + explode * math.cos(ma)
                ocy = cy + explode * math.sin(ma)
            x1 = ocx + r * math.cos(ss)
            y1 = ocy + r * math.sin(ss)
            x2 = ocx + r * math.cos(ee)
            y2 = ocy + r * math.sin(ee)
            la = 1 if (ee - ss) > math.pi else 0
            d_top = f'M {ocx},{ocy} L {x1:.1f},{y1:.1f} A {r},{r} 0 {la},1 {x2:.1f},{y2:.1f} Z'
            elem = f'<path d="{d_top}" fill="{col}" stroke="#fff" stroke-width="2"/>'
            href = hrefs[i] if hrefs and i < len(hrefs) else None
            paths.append(_wrap(elem, href))
            lr = r / 2
            lx = ocx + lr * math.cos(ma)
            ly = ocy + lr * math.sin(ma)
            pct = round((val / total) * 100)
            paths.append(f'<text x="{lx:.1f}" y="{ly - 7:.1f}" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="bold" fill="#fff">{val}</text>')
            paths.append(f'<text x="{lx:.1f}" y="{ly + 9:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" fill="#fff" opacity="0.9">{pct}%</text>')
    else:
        for i, (ss, ee, val) in enumerate(slices):
            col = colors[i] if colors and i < len(colors) else '#64748b'
            ma = ss + (ee - ss) / 2
            ocx, ocy = cx, cy
            if i == max_idx:
                ocx = cx + explode * math.cos(ma)
                ocy = cy + explode * math.sin(ma)
            x1 = ocx + r * math.cos(ss)
            y1 = ocy + r * math.sin(ss)
            x2 = ocx + r * math.cos(ee)
            y2 = ocy + r * math.sin(ee)
            la = 1 if (ee - ss) > math.pi else 0
            d = f'M {ocx},{ocy} L {x1:.1f},{y1:.1f} A {r},{r} 0 {la},1 {x2:.1f},{y2:.1f} Z'
            elem = f'<path d="{d}" fill="{col}" stroke="#fff" stroke-width="2"/>'
            href = hrefs[i] if hrefs and i < len(hrefs) else None
            paths.append(_wrap(elem, href))
            lr = (r + ir) / 2
            lx = ocx + lr * math.cos(ma)
            ly = ocy + lr * math.sin(ma)
            pct = round((val / total) * 100)
            paths.append(f'<text x="{lx:.1f}" y="{ly - 7:.1f}" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="bold" fill="#fff">{val}</text>')
            paths.append(f'<text x="{lx:.1f}" y="{ly + 9:.1f}" text-anchor="middle" dominant-baseline="central" font-size="11" fill="#fff" opacity="0.9">{pct}%</text>')
    n = len(labels)
    lx = 40
    ly = 255
    for i, (lbl, col) in enumerate(zip(labels, colors)):
        y = ly + i * 28
        href = hrefs[i] if hrefs and i < len(hrefs) else None
        rect = f'<rect x="{lx}" y="{y}" width="14" height="14" rx="3" fill="{col}"/>'
        paths.append(_wrap(rect, href))
        paths.append(f'<text x="{lx + 20}" y="{y + 11}" font-size="14" fill="{COLOR_TEXT}">{_escape(lbl)}</text>')
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">{"".join(paths)}</svg>'


def svg_bar_vertical(data, labels, color, w=600, h=300, pad_l=40, pad_r=20, pad_t=20, pad_b=60, hrefs=None):
    if not data:
        return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"></svg>'
    mx = max(data) or 1
    total = sum(data) or 1
    cw = w - pad_l - pad_r
    ch = h - pad_t - pad_b
    n = len(data)
    bw = max(20, min(60, (cw - n * 4) / n))
    gap = (cw - n * bw) / (n + 1)
    els = []
    for i, (val, lbl) in enumerate(zip(data, labels)):
        bh = (val / mx) * ch if mx else 0
        x = pad_l + gap + i * (bw + gap)
        y = pad_t + ch - bh
        elem = f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(bh, 0):.1f}" rx="4" fill="{color}"/>'
        href = hrefs[i] if hrefs and i < len(hrefs) else None
        els.append(_wrap(elem, href))
        if val:
            pct = round((val / total) * 100)
            cy_txt = y + bh / 2
            els.append(f'<text x="{x + bw / 2:.1f}" y="{cy_txt - 6:.1f}" text-anchor="middle" dominant-baseline="central" font-size="13" font-weight="bold" fill="#fff">{val}</text>')
            els.append(f'<text x="{x + bw / 2:.1f}" y="{cy_txt + 10:.1f}" text-anchor="middle" dominant-baseline="central" font-size="10" fill="#fff" opacity="0.9">{pct}%</text>')
        lbls = _escape(lbl)
        els.append(f'<text x="{x + bw / 2:.1f}" y="{pad_t + ch + 14}" text-anchor="end" font-size="10" fill="{COLOR_TEXT}" transform="rotate(-35,{x + bw / 2:.1f},{pad_t + ch + 14})">{lbls}</text>')
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">{"".join(els)}</svg>'


def _adjust_color(hex_color, factor):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    if factor > 0:
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
    else:
        r = max(0, int(r * (1 + factor)))
        g = max(0, int(g * (1 + factor)))
        b = max(0, int(b * (1 + factor)))
    return f'#{r:02x}{g:02x}{b:02x}'


def svg_bar_3d(data, labels, colors, w=600, h=380, pad_l=40, pad_r=40, pad_t=30, pad_b=100, hrefs=None, depth=10):
    if not data:
        return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"></svg>'
    mx = max(data) or 1
    total = sum(data) or 1
    cw = w - pad_l - pad_r - depth
    ch = h - pad_t - pad_b
    n = len(data)
    bw = max(30, min(70, (cw - n * 6) / n))
    gap = (cw - n * bw) / (n + 1)
    els = []
    for i, (val, lbl) in enumerate(zip(data, labels)):
        bh = (val / mx) * ch if mx else 0
        x = pad_l + gap + i * (bw + gap)
        y = pad_t + ch - bh
        col = colors[i] if colors and i < len(colors) else '#64748b'
        lighter = _adjust_color(col, 0.3)
        darker = _adjust_color(col, -0.25)
        dph = depth

        top = (f'{x},{y} {x + bw},{y} {x + bw + dph},{y - dph} {x + dph},{y - dph}')
        right = (f'{x + bw},{y} {x + bw},{y + bh} {x + bw + dph},{y + bh - dph} {x + bw + dph},{y - dph}')
        front = (f'{x + dph},{y} {x + bw + dph},{y} {x + bw + dph},{y + bh} {x + dph},{y + bh}')

        group = (
            f'<polygon points="{right}" fill="{darker}" stroke="none"/>'
            f'<polygon points="{top}" fill="{lighter}" stroke="none"/>'
            f'<polygon points="{front}" fill="{col}" stroke="none" rx="2"/>'
        )
        href = hrefs[i] if hrefs and i < len(hrefs) else None
        els.append(_wrap(group, href))

        if val:
            pct = round((val / total) * 100)
            cx = x + (bw / 2) + dph
            cy_txt = y + bh / 2
            els.append(f'<text x="{cx:.1f}" y="{cy_txt - 5:.1f}" text-anchor="middle" dominant-baseline="central" font-size="13" font-weight="bold" fill="#fff">{val}</text>')
            els.append(f'<text x="{cx:.1f}" y="{cy_txt + 10:.1f}" text-anchor="middle" dominant-baseline="central" font-size="10" fill="#fff" opacity="0.9">{pct}%</text>')

        lbls = _escape(lbl)
        els.append(f'<text x="{x + bw / 2 + dph / 2:.1f}" y="{pad_t + ch + 16}" text-anchor="middle" font-size="10" fill="{COLOR_TEXT}">{lbls}</text>')
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">{"".join(els)}</svg>'


def svg_lollipop_vertical(data, labels, color, w=600, h=350, pad_l=40, pad_r=20, pad_t=40, pad_b=80, hrefs=None):
    if not data:
        return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"></svg>'
    mx = max(data) or 1
    total = sum(data) or 1
    cw = w - pad_l - pad_r
    ch = h - pad_t - pad_b
    n = len(data)
    gap = cw / (n + 1) if n > 1 else cw / 2
    els = []
    for i, (val, lbl) in enumerate(zip(data, labels)):
        x = pad_l + gap * (i + 1)
        bh = (val / mx) * ch if mx else 0
        y_base = pad_t + ch
        y_top = y_base - bh
        pct = round((val / total) * 100) if val else 0

        line = f'<line x1="{x}" y1="{y_base}" x2="{x}" y2="{y_top}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>'
        dot = f'<circle cx="{x}" cy="{y_top}" r="18" fill="{color}" stroke="#fff" stroke-width="2"/>'
        inner = f'<text x="{x}" y="{y_top - 3}" text-anchor="middle" dominant-baseline="central" font-size="12" font-weight="bold" fill="#fff">{val}</text>'
        if pct:
            inner += f'<text x="{x}" y="{y_top + 9}" text-anchor="middle" dominant-baseline="central" font-size="9" fill="#fff" opacity="0.9">{pct}%</text>'
        if hrefs and i < len(hrefs) and hrefs[i]:
            els.append(_wrap(line + dot + inner, hrefs[i]))
        else:
            els.append(line)
            els.append(dot)
            els.append(inner)

        lbls = _escape(lbl)
        els.append(f'<text x="{x}" y="{y_base + 16}" text-anchor="end" font-size="10" fill="{COLOR_TEXT}" transform="rotate(-30,{x},{y_base + 16})">{lbls}</text>')

    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">{"".join(els)}</svg>'


def svg_lollipop(data, labels, color, w=650, h=400, pad_l=140, pad_r=70, pad_t=20, pad_b=20, hrefs=None):
    if not data:
        return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"></svg>'
    mx = max(data) or 1
    total = sum(data) or 1
    cw = w - pad_l - pad_r
    ch = h - pad_t - pad_b
    n = len(data)
    gap = ch / (n + 1) if n > 1 else ch / 2
    stem_color = color
    dot_color = color
    els = []
    for i, (val, lbl) in enumerate(zip(data, labels)):
        y = pad_t + gap * (i + 1)
        bw = (val / mx) * cw if mx else 0
        x_end = pad_l + bw
        pct = round((val / total) * 100) if val else 0

        line = f'<line x1="{pad_l}" y1="{y}" x2="{x_end}" y2="{y}" stroke="{stem_color}" stroke-width="5" stroke-linecap="round"/>'
        circle = f'<circle cx="{x_end}" cy="{y}" r="10" fill="{dot_color}" stroke="#fff" stroke-width="3"/>'
        if hrefs and i < len(hrefs) and hrefs[i]:
            els.append(_wrap(line + circle, hrefs[i]))
        else:
            els.append(line)
            els.append(circle)

        els.append(f'<text x="{x_end + 20}" y="{y}" text-anchor="start" dominant-baseline="central" font-size="13" font-weight="bold" fill="{COLOR_TEXT}">{val}</text>')

        els.append(f'<text x="{pad_l - 10}" y="{y + 4}" text-anchor="end" font-size="11" fill="{COLOR_TEXT}">{_escape(lbl)}</text>')

    x_axis_y = pad_t + ch + 10
    els.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{x_axis_y}" stroke="{COLOR_GRID}" stroke-width="1"/>')
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">{"".join(els)}</svg>'


def svg_bar_horizontal(data, labels, color, w=500, h=300, hrefs=None):
    if not data:
        return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"></svg>'
    mx = max(data) or 1
    total = sum(data) or 1
    pad_l, pad_r, pad_t, pad_b = 120, 60, 20, 20
    cw = w - pad_l - pad_r
    ch = h - pad_t - pad_b
    n = len(data)
    bh = max(20, min(50, (ch - n * 4) / n))
    gap = (ch - n * bh) / (n + 1)
    els = []
    for i, (val, lbl) in enumerate(zip(data, labels)):
        bw = (val / mx) * cw if mx else 0
        y = pad_t + gap + i * (bh + gap)
        elem = f'<rect x="{pad_l}" y="{y:.1f}" width="{max(bw, 0):.1f}" height="{bh:.1f}" rx="4" fill="{color}"/>'
        href = hrefs[i] if hrefs and i < len(hrefs) else None
        els.append(_wrap(elem, href))
        if val:
            pct = round((val / total) * 100)
            cx = pad_l + bw / 2
            cy = y + bh / 2
            if bw > 40:
                els.append(f'<text x="{cx:.1f}" y="{cy - 5:.1f}" text-anchor="middle" dominant-baseline="central" font-size="13" font-weight="bold" fill="#fff">{val}</text>')
                els.append(f'<text x="{cx:.1f}" y="{cy + 10:.1f}" text-anchor="middle" dominant-baseline="central" font-size="10" fill="#fff" opacity="0.9">{pct}%</text>')
            else:
                els.append(f'<text x="{pad_l + bw + 6:.1f}" y="{cy - 5:.1f}" text-anchor="start" dominant-baseline="central" font-size="13" font-weight="bold" fill="{color}">{val}</text>')
                els.append(f'<text x="{pad_l + bw + 6:.1f}" y="{cy + 10:.1f}" text-anchor="start" dominant-baseline="central" font-size="10" fill="{COLOR_TEXT}">{pct}%</text>')
        els.append(f'<text x="{pad_l - 8}" y="{y + bh / 2 + 4}" text-anchor="end" font-size="11" fill="{COLOR_TEXT}">{_escape(lbl)}</text>')
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">{"".join(els)}</svg>'
