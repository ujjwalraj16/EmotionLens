"""
charts.py — Pure-SVG visualisation helpers for EmotionLens.
Each function returns an SVG string ready for st.markdown(..., unsafe_allow_html=True).
"""
import math

from config import EMOTION_META, EMOTION_GROUPS

# ── Geometry helper ───────────────────────────────────────────────────────────

def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)

# ── Confidence ring ───────────────────────────────────────────────────────────

def svg_confidence_ring(conf: float, color: str, t: dict) -> str:
    r = 54
    circ = 2 * math.pi * r
    dash, gap = circ * conf, circ * (1 - conf)
    pct = round(conf * 100, 1)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 140" width="140" height="140" style="display:block;margin:auto">
  <circle cx="70" cy="70" r="{r}" fill="none" stroke="{t['track']}" stroke-width="13"/>
  <circle cx="70" cy="70" r="{r}" fill="none" stroke="{color}" stroke-width="13"
    stroke-linecap="round" stroke-dasharray="{dash:.2f} {gap:.2f}" transform="rotate(-90 70 70)"/>
  <text x="70" y="62" text-anchor="middle" font-size="22" font-weight="700" fill="{color}" font-family="Plus Jakarta Sans">{pct}%</text>
  <text x="70" y="82" text-anchor="middle" font-size="9.5" fill="{t['text2']}" font-family="Space Mono" letter-spacing="1.2">CONFIDENCE</text>
</svg>"""

# ── Donut chart ───────────────────────────────────────────────────────────────

def svg_donut(all_emotions: dict, top_emotion: str, t: dict) -> str:
    top8  = sorted(all_emotions.items(), key=lambda x: x[1], reverse=True)[:8]
    total = sum(v for _, v in top8) or 1
    cx, cy, ro, ri = 120, 130, 108, 54
    W, H = 470, 278

    paths = ""
    angle = -90.0
    for emo, prob in top8:
        sweep = (prob / total) * 360
        end   = angle + sweep
        laf   = 1 if sweep > 180 else 0
        x1,y1 = _pt(cx,cy,ro,angle);  x2,y2  = _pt(cx,cy,ro,end)
        xi1,yi1 = _pt(cx,cy,ri,end);  xi2,yi2 = _pt(cx,cy,ri,angle)
        d = (f"M{x1:.1f},{y1:.1f} A{ro},{ro},0,{laf},1,{x2:.1f},{y2:.1f} "
             f"L{xi1:.1f},{yi1:.1f} A{ri},{ri},0,{laf},0,{xi2:.1f},{yi2:.1f}Z")
        meta   = EMOTION_META.get(emo, {"color": "#9CA3AF"})
        opa    = "1" if emo == top_emotion else "0.62"
        sw     = "3" if emo == top_emotion else "1.5"
        stroke = "rgba(0,0,0,0.2)" if t["bg"] < "#5" else "rgba(255,255,255,0.15)"
        paths += f'<path d="{d}" fill="{meta["color"]}" opacity="{opa}" stroke="{stroke}" stroke-width="{sw}"><title>{emo}: {round(prob*100,1)}%</title></path>'
        angle  = end

    top_m  = EMOTION_META.get(top_emotion, {"emoji": "❓"})
    center = (f'<text x="{cx}" y="{cy-8}" text-anchor="middle" font-size="26">{top_m["emoji"]}</text>'
              f'<text x="{cx}" y="{cy+16}" text-anchor="middle" font-size="9" fill="{t["text2"]}" font-family="Space Mono" letter-spacing="1.5">TOP EMOTION</text>')

    legend = ""
    for i, (emo, prob) in enumerate(top8):
        meta = EMOTION_META.get(emo, {"color": "#9CA3AF", "emoji": "❓"})
        pct  = round(prob * 100, 1)
        lx, ly = 256, 24 + i * 30
        bold = 'font-weight="700"' if emo == top_emotion else ''
        ec   = meta["color"] if emo == top_emotion else t["text2"]
        opa  = "1" if emo == top_emotion else "0.65"
        legend += (
            f'<rect x="{lx}" y="{ly-10}" width="11" height="11" rx="3" fill="{meta["color"]}" opacity="{opa}"/>'
            f'<text x="{lx+16}" y="{ly}" font-size="12" fill="{ec}" {bold} font-family="Plus Jakarta Sans">{meta["emoji"]} {emo.capitalize()}</text>'
            f'<text x="{W-6}" y="{ly}" font-size="11" fill="{meta["color"]}" {bold} font-family="Space Mono" text-anchor="end">{pct}%</text>'
        )

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="100%" style="max-width:{W}px;display:block;margin:auto">'
            f'{paths}{center}{legend}</svg>')

# ── Sentiment polarity gauge ──────────────────────────────────────────────────

def svg_gauge(all_emotions: dict, t: dict) -> str:
    pos   = sum(all_emotions.get(e, 0) for e in EMOTION_GROUPS["Positive"])
    neg   = sum(all_emotions.get(e, 0) for e in EMOTION_GROUPS["Negative"])
    amb   = sum(all_emotions.get(e, 0) for e in EMOTION_GROUPS["Ambiguous"])
    total = pos + neg + amb or 1
    val = pos / total         

    cx, cy, R = 150, 140, 110
    W, H = 300, 190

    def arc_seg(sd, ed, color):
        ro, ri = R, R - 22
        laf = 1 if (ed - sd) > 180 else 0
        x1,y1 = _pt(cx,cy,ro,sd); x2,y2 = _pt(cx,cy,ro,ed)
        xi1,yi1 = _pt(cx,cy,ri,ed); xi2,yi2 = _pt(cx,cy,ri,sd)
        d = (f"M{x1:.1f},{y1:.1f} A{ro},{ro},0,{laf},1,{x2:.1f},{y2:.1f} "
             f"L{xi1:.1f},{yi1:.1f} A{ri},{ri},0,{laf},0,{xi2:.1f},{yi2:.1f}Z")
        return f'<path d="{d}" fill="{color}" opacity="0.8"/>'

    arcs = (arc_seg(180, 225, "#EF4444") + arc_seg(225, 270, "#F97316") +
            arc_seg(270, 300, "#FCD34D") + arc_seg(300, 360, "#22C55E"))

    na = 180 + val * 180
    nax, nay = _pt(cx, cy, R - 12, na)
    needle = (f'<line x1="{cx}" y1="{cy}" x2="{nax:.1f}" y2="{nay:.1f}" '
              f'stroke="{t["text"]}" stroke-width="3" stroke-linecap="round"/>'
              f'<circle cx="{cx}" cy="{cy}" r="7" fill="{t["text"]}"/>')

    pp, np_, ap = round(pos/total*100), round(neg/total*100), round(amb/total*100)
    labs = (
        f'<text x="20" y="{cy+8}" font-size="11" fill="#EF4444" font-family="Plus Jakarta Sans" font-weight="700">NEG</text>'
        f'<text x="20" y="{cy+22}" font-size="10" fill="#EF4444" font-family="Space Mono">{np_}%</text>'
        f'<text x="{W-52}" y="{cy+8}" font-size="11" fill="#22C55E" font-family="Plus Jakarta Sans" font-weight="700">POS</text>'
        f'<text x="{W-52}" y="{cy+22}" font-size="10" fill="#22C55E" font-family="Space Mono">{pp}%</text>'
        f'<text x="{cx}" y="{cy+44}" text-anchor="middle" font-size="10" fill="{t["text2"]}" font-family="Space Mono">NEUTRAL {ap}%</text>'
    )

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="100%" style="max-width:{W}px;display:block;margin:auto">'
            f'{arcs}{needle}{labs}</svg>')