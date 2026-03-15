import io, re, requests
import streamlit as st

from config  import API_URL, EMOTION_META, EMOTION_GROUPS
from styles  import get_theme, inject_css
from charts  import svg_confidence_ring, svg_donut, svg_gauge

# optional PDF support
try:
    import pypdf
    def _read_pdf(buf):
        r = pypdf.PdfReader(buf)
        return "\n".join(p.extract_text() or "" for p in r.pages), len(r.pages)
except ImportError:
    def _read_pdf(buf):
        return "[pypdf not installed — run: pip install pypdf]", 0

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(page_title="EmotionLens", layout="wide", initial_sidebar_state="collapsed")

# ── Session defaults ──────────────────────────────────────────────────────────
st.session_state.setdefault("dark_mode", True)
st.session_state.setdefault("input_tab", "type")

# ── Helpers ───────────────────────────────────────────────────────────────────

def read_txt(f) -> str:
    raw = f.read()
    for enc in ("utf-8", "latin-1", "cp1252"):
        try: return raw.decode(enc)
        except UnicodeDecodeError: pass
    return raw.decode("utf-8", errors="replace")

def read_pdf(f) -> tuple:
    text, pages = _read_pdf(io.BytesIO(f.read()))
    return text, pages

def clean(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()[:2000]

def call_api(text: str) -> dict:
    try:
        r = requests.post(API_URL, json={"text": text}, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"_error": "❌ Backend not reachable — is Flask running on port 5001?"}
    except requests.exceptions.Timeout:
        return {"_error": "⏱️ Request timed out."}
    except Exception as e:
        return {"_error": f"⚠️ {e}"}

# ── Result cards ──────────────────────────────────────────────────────────────

def render_results(result: dict, t: dict):
    emotion    = result["emotion"]
    confidence = result["confidence"]
    all_emo    = result["all_emotions"]
    meta       = EMOTION_META.get(emotion, {"emoji": "❓", "color": t["accent"]})
    color, emoji = meta["color"], meta["emoji"]

    # Card 1 — primary detection + confidence ring
    ring = svg_confidence_ring(confidence, color, t)
    st.markdown(f"""
<div class="el-card el-card-accent" style="--accent:{color}">
  <div class="slabel"><span>01</span>PRIMARY DETECTION</div>
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1.5rem">
    <div class="top-block">
      <div class="emo-emoji-big">{emoji}</div>
      <div>
        <div class="emo-name" style="color:{color}">{emotion.capitalize()}</div>
        <div class="emo-conf">Confidence: <strong>{round(confidence*100,1)}%</strong></div>
      </div>
    </div>
    <div>{ring}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Cards 2 & 3 — donut | probability bars
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
<div class="el-card">
  <div class="slabel"><span>02</span>DISTRIBUTION — DONUT CHART</div>
  {svg_donut(all_emo, emotion, t)}
</div>""", unsafe_allow_html=True)

    with c2:
        top10 = sorted(all_emo.items(), key=lambda x: x[1], reverse=True)[:10]
        rows  = "".join(
            f'<div class="prob-row {"tb" if e==emotion else ""}">'
            f'<span class="prob-name" style="color:{EMOTION_META.get(e,{"color":t["text2"]})["color"] if e==emotion else t["text2"]}">'
            f'{EMOTION_META.get(e,{"emoji":"❓"})["emoji"]} {e}</span>'
            f'<div class="prob-track"><div class="prob-fill" style="width:{round(p*100,1)}%;background:{EMOTION_META.get(e,{"color":"#9CA3AF"})["color"]};"></div></div>'
            f'<span class="prob-pct">{round(p*100,1)}%</span></div>'
            for e, p in top10
        )
        st.markdown(f"""
<div class="el-card">
  <div class="slabel"><span>03</span>TOP 10 PROBABILITIES</div>
  <div class="prob-list">{rows}</div>
</div>""", unsafe_allow_html=True)

    # Card 4 — sentiment gauge
    grp       = next((g for g, es in EMOTION_GROUPS.items() if emotion in es), "Ambiguous")
    grp_color = {"Positive": "#22C55E", "Negative": "#EF4444", "Ambiguous": "#F59E0B"}[grp]
    st.markdown(f"""
<div class="el-card">
  <div class="slabel"><span>04</span>SENTIMENT POLARITY GAUGE</div>
  {svg_gauge(all_emo, t)}
  <hr class="div">
  <div style="text-align:center">
    <span style="background:{grp_color}20;border:1px solid {grp_color}50;color:{grp_color};
      border-radius:999px;padding:5px 18px;font-size:0.82rem;font-weight:600;display:inline-block">
      <b>{emotion.capitalize()}</b> → {grp} sentiment
    </span>
  </div>
</div>""", unsafe_allow_html=True)


def render_input(t: dict) -> str:
    """Renders the input card and returns the final text to analyse (or '')."""

    # Tab switcher
    tc1, tc2 = st.columns(2)
    with tc1:
        if st.button("✏️  Type / Paste Text", key="tab_type", use_container_width=True,
                     type="primary" if st.session_state.input_tab == "type" else "secondary"):
            st.session_state.input_tab = "type"; st.rerun()
    with tc2:
        if st.button("📎  Upload File  (.txt / .pdf)", key="tab_file", use_container_width=True,
                     type="primary" if st.session_state.input_tab == "file" else "secondary"):
            st.session_state.input_tab = "file"; st.rerun()

    final = ""

    if st.session_state.input_tab == "type":
        st.markdown(f'<div class="slabel" style="margin-top:1rem"><span>✏️</span>YOUR TEXT</div>', unsafe_allow_html=True)
        final = st.text_area("text", label_visibility="hidden",
                              placeholder='e.g. "I can\'t believe how amazing this turned out!"',
                              height=140, key="u_input").strip()
    else:
        st.markdown(f'<div class="slabel" style="margin-top:1rem"><span>📎</span>UPLOAD A FILE</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("upload", label_visibility="hidden",
                                    type=["txt","pdf"], key="u_file")
        if uploaded:
            is_pdf = uploaded.name.lower().endswith(".pdf")
            extracted, pages = read_pdf(uploaded) if is_pdf else (read_txt(uploaded), None)
            icon       = "📄" if is_pdf else "📝"
            meta_extra = f"{pages} page{'s' if pages!=1 else ''}" if is_pdf else "plain text"
            fsize      = round(uploaded.size / 1024, 1)

            st.markdown(
                f'<div class="file-meta"><span style="font-size:1.4rem">{icon}</span>'
                f'<span>{uploaded.name}</span><span style="color:{t["text3"]}">·</span>'
                f'<span>{fsize} KB · {meta_extra}</span>'
                f'<span style="color:{t["text3"]}">·</span><span style="color:#22C55E">✓ Loaded</span></div>',
                unsafe_allow_html=True)

            preview = extracted[:600] + ("…" if len(extracted) > 600 else "")
            st.markdown(f'<div class="file-preview">{preview}</div>', unsafe_allow_html=True)

            cleaned = clean(extracted)
            clipped = len(cleaned) >= 2000
            clr     = "#F59E0B" if clipped else t["accent"]
            st.markdown(
                f'<div style="font-family:Space Mono,monospace;font-size:0.65rem;color:{clr};margin-top:0.5rem">'
                f'{"⚠️ " if clipped else ""}EXTRACTED {len(cleaned):,} CHARS'
                f'{" — TRUNCATED TO 2 000" if clipped else ""}</div>',
                unsafe_allow_html=True)
            final = cleaned
        else:
            st.markdown(
                f'<div style="text-align:center;padding:1.5rem 0;color:{t["text3"]}">'
                f'<div style="font-size:2.8rem">📂</div>'
                f'<div style="font-family:Space Mono,monospace;font-size:0.72rem;margin-top:0.5rem">DROP A .TXT OR .PDF FILE ABOVE</div>'
                f'<div style="font-size:0.8rem;margin-top:0.4rem">Text is extracted automatically</div></div>',
                unsafe_allow_html=True)
            
    # Analyse button
    _, cb, _ = st.columns([1, 2, 1])
    with cb:
        go = st.button("🔍  Analyse Emotion", use_container_width=True, key="go_btn")
    return final, go

def main():
    t = get_theme(st.session_state.dark_mode)
    inject_css(t)

    _, col_t = st.columns([7, 1])
    with col_t:
        if st.button("☀️ Light" if st.session_state.dark_mode else "🌙 Dark", key="mode_btn"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    # Hero
    st.markdown(
        '<div class="hero">'
        '<div class="hero-badge">Real-Time Recognition</div>'
        '<h1 class="hero-title">EmotionLens</h1>'
        '<p class="hero-sub">Discover the emotion hidden in your words.</p>'
        '</div>', unsafe_allow_html=True)

    # Input + analyse
    final_text, go = render_input(t)

    st.markdown(
        f'<div class="tip">💡 <b>Try:</b> "I\'m so grateful!" &nbsp;·&nbsp; '
        f'"I\'m furious!" &nbsp;·&nbsp; "I have no idea what happened." &nbsp;·&nbsp; '
        f'or upload a PDF / .txt file</div>', unsafe_allow_html=True)

    if go:
        if not final_text:
            st.error("Please enter some text or upload a file first.")
        else:
            with st.spinner("Analysing…"):
                res = call_api(final_text)
            if "_error" in res:
                st.error(res["_error"])
            else:
                render_results(res, t)

    st.markdown('<div class="footer">EmotionLens</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()