#!/usr/bin/env python3
"""Generate the homepage 'Keep' architecture SVG map.

Same visual grammar as the original hand-built diagram (rect boxes, right-
angle connector lines, teal accent for top-level nodes, muted borders for
leaves, JetBrains Mono text) but wide enough to show how the actual product
line and service stack both plug into the same Capability Router. Clickable
nodes (an actual product/page exists) get wrapped in <a href>; reference-only
labels (internal service names with no public page yet) stay plain text.

Run: python3 gen_keep_map.py > keep_map.svg
"""

W, H = 1200, 606
BG = "#0e131b"
BOX = "#121926"
BORDER = "#1e2a3b"
BORDER_BRIGHT = "#2d3e56"
ACCENT = "#39e6c8"
TEXT = "#e4edf5"
DIM = "#8ea0b6"
FONT = "'JetBrains Mono', ui-monospace, monospace"

out = []


def rect(x, y, w, h, stroke=BORDER, fill=BOX, sw=1.3, rx=6):
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def text(x, y, s, size=12.5, weight=600, fill=TEXT, anchor="middle"):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
               f'font-size="{size}" font-weight="{weight}" fill="{fill}">{s}</text>')


def line(x1, y1, x2, y2, stroke=BORDER, sw=1.3):
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
               f'stroke="{stroke}" stroke-width="{sw}"/>')


def vconnector(x, y1, y2):
    line(x, y1, x, y2)


def branch(x_parent, y_top, xs, y_bottom):
    """Drop from a parent's bottom center, fan out horizontally, drop to each child's top."""
    y_mid = (y_top + y_bottom) / 2
    line(x_parent, y_top, x_parent, y_mid)
    if len(xs) > 1:
        line(min(xs), y_mid, max(xs), y_mid)
    for x in xs:
        line(x, y_mid, x, y_bottom)


def node(x, y, w, h, title, sublabels=None, href=None, top_level=False, divider=True):
    """A box with a title and optional stacked sub-labels, optionally clickable."""
    if href:
        out.append(f'<a href="{href}">')
    stroke = ACCENT if top_level else BORDER_BRIGHT
    sw = 1.6 if top_level else 1.3
    rect(x, y, w, h, stroke=stroke, sw=sw)
    cx = x + w / 2
    if not sublabels:
        text(cx, y + h / 2 + 4, title, size=12.5, weight=600, fill=TEXT if not top_level else ACCENT)
    elif divider:
        text(cx, y + 24, title, size=12.5, weight=600, fill=ACCENT)
        liney = y + 34
        line(x + 14, liney, x + w - 14, liney)
        sy = liney + 20
        for lbl in sublabels:
            text(cx, sy, lbl, size=10.7, weight=500, fill=DIM)
            sy += 18
    else:
        text(cx, y + 22, title, size=12.5, weight=600, fill=TEXT)
        sy = y + 40
        for lbl in sublabels:
            text(cx, sy, lbl, size=11, weight=500, fill=DIM)
            sy += 16
    if href:
        out.append(f'<text x="{cx:.1f}" y="{y+h-8:.1f}" text-anchor="middle" font-family="{FONT}" '
                   f'font-size="9" font-weight="600" fill="{ACCENT}" opacity="0.85">open &#8599;</text>')
        out.append('</a>')
    return cx


def main():
    out.append(f'<svg viewBox="0 0 {W} {H}" role="img" '
               f'aria-label="The Keep architecture: agent products and service stack both route through one shared Capability Router, which dispatches to local GPU models, remote workers, or other nodes. Boxes with an open arrow link to that product\'s page." '
               f'xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;">')
    rect(0, 0, W, H, stroke=BG, fill=BG, rx=0)

    root_cx = W / 2
    node(root_cx - 75, 18, 150, 36, "YOUR KEEP", top_level=True)

    # Level 1: AI AGENTS | SERVICES
    agents_cx = W * 0.28
    services_cx = W * 0.74
    branch(root_cx, 54, [agents_cx, services_cx], 94)
    node(agents_cx - 90, 94, 180, 32, "AI AGENT PRODUCTS", top_level=True)
    node(services_cx - 90, 94, 180, 32, "SERVICE STACK", top_level=True)

    # Level 2a: AI agent products, 2x2 grid under agents_cx
    agent_products = [
        ("Otacon Lite", ["Chat", "Memory / Voice"], "/otacon/"),
        ("KeepRoute", ["Provider fallback", "Mission control"], "/keeproute/"),
        ("Keep Desk", ["Computer-use", "Local agents"], "/keepdesk/"),
        ("Expansion", ["5-agent hierarchy", "REX"], "/expansion/"),
    ]
    col_w, col_gap = 150, 16
    total_w = 2 * col_w + col_gap
    ax0 = agents_cx - total_w / 2
    row_h, row_gap = 108, 14
    positions = []
    for i, _ in enumerate(agent_products):
        r, c = divmod(i, 2)
        x = ax0 + c * (col_w + col_gap)
        y = 172 + r * (row_h + row_gap)
        positions.append((x, y))
    grid_top = 172
    grid_bottom = grid_top + 2 * row_h + row_gap
    branch(agents_cx, 126, [ax0 + col_w / 2, ax0 + col_w + col_gap + col_w / 2], grid_top)
    for (title, subs, href), (x, y) in zip(agent_products, positions):
        node(x, y, col_w, row_h, title, subs, href=href)

    # Level 2b: service stack, 3x2 grid under services_cx
    services = [
        ("Media", ["Plex", "*arr stack"], None),
        ("Requests", ["Doplarr", "Seerr"], None),
        ("FOXDIE", ["Integrity scan", "Auto-fix"], "/foxdie/"),
        ("Home + Automation", ["Home Assistant", "n8n"], None),
        ("Creative Pipeline", ["Video Studio", "The Director"], None),
        ("Search", ["SearXNG"], None),
    ]
    scol_w, scol_gap = 150, 14
    stotal_w = 3 * scol_w + 2 * scol_gap
    sx0 = services_cx - stotal_w / 2
    spositions = []
    for i, _ in enumerate(services):
        r, c = divmod(i, 3)
        x = sx0 + c * (scol_w + scol_gap)
        y = 172 + r * (row_h + row_gap)
        spositions.append((x, y))
    branch(services_cx, 126, [sx0 + scol_w / 2, sx0 + scol_w + scol_gap + scol_w / 2,
                               sx0 + 2 * (scol_w + scol_gap) + scol_w / 2], grid_top)
    for (title, subs, href), (x, y) in zip(services, spositions):
        node(x, y, scol_w, row_h, title, subs, href=href)

    # Converge: both grids drop into CAPABILITY ROUTER
    router_y_top = grid_bottom + 46
    agents_bottom_cx = ax0 + total_w / 2
    services_bottom_cx = sx0 + stotal_w / 2
    line(agents_bottom_cx, grid_bottom, agents_bottom_cx, grid_bottom + 18)
    line(services_bottom_cx, grid_bottom, services_bottom_cx, grid_bottom + 18)
    line(agents_bottom_cx, grid_bottom + 18, services_bottom_cx, grid_bottom + 18)
    mid_cx = (agents_bottom_cx + services_bottom_cx) / 2
    line(mid_cx, grid_bottom + 18, mid_cx, router_y_top)
    node(mid_cx - 95, router_y_top, 190, 36, "CAPABILITY ROUTER", top_level=True)

    # Level 4: Local GPU | Remote Workers | Other Nodes
    final_y = router_y_top + 36 + 46
    fx = [mid_cx - 190, mid_cx, mid_cx + 190]
    branch(mid_cx, router_y_top + 36, fx, final_y)
    node(fx[0] - 84, final_y, 168, 52, "Local GPU", ["Models"], divider=False)
    node(fx[1] - 84, final_y, 168, 52, "Remote", ["Workers"], divider=False)
    node(fx[2] - 84, final_y, 168, 52, "Other", ["Nodes"], divider=False)

    out.append('</svg>')
    print(''.join(out))


if __name__ == "__main__":
    main()
