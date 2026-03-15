"""
styles.py — Theme tokens + CSS injection for EmotionLens.
Import and call inject_css(t) once at the top of main().
"""
import streamlit as st

# ── Theme tokens ──────────────────────────────────────────────────────────────

def get_theme(dark: bool) -> dict:
    if dark:
        return dict(
            bg="#080C14", surface="#0D1526",
            border="rgba(56,189,248,0.18)", border2="rgba(255,255,255,0.07)",
            text="#E2E8F0", text2="#94A3B8", text3="#475569",
            input_bg="#060A12",
            tip_bg="rgba(56,189,248,0.06)", tip_bdr="rgba(56,189,248,0.18)", tip_txt="#7DD3FC",
            track="rgba(255,255,255,0.07)", footer="#1E293B",
            accent="#38BDF8", shadow="rgba(0,0,0,0.4)",
        )
    return dict(
        bg="#F1F5F9", surface="#FFFFFF",
        border="rgba(14,165,233,0.22)", border2="rgba(0,0,0,0.07)",
        text="#0F172A", text2="#475569", text3="#94A3B8",
        input_bg="#FFFFFF",
        tip_bg="rgba(14,165,233,0.07)", tip_bdr="rgba(14,165,233,0.2)", tip_txt="#0369A1",
        track="rgba(0,0,0,0.08)", footer="#CBD5E1",
        accent="#0EA5E9", shadow="rgba(0,0,0,0.08)",
    )

# ── CSS injection ─────────────────────────────────────────────────────────────

def inject_css(t: dict):
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* background — every Streamlit shell layer */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
section[data-testid="stSidebar"], .main .block-container {{
    background-color: {t['bg']} !important;
    background: {t['bg']} !important;
    color: {t['text']} !important;
}}
::-webkit-scrollbar {{ width:6px; background:{t['bg']}; }}
::-webkit-scrollbar-thumb {{ background:{t['border']}; border-radius:3px; }}
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {t['text']} !important;
}}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ padding-top:0.5rem !important; max-width:1100px !important; }}

/* textarea */
.stTextArea > label {{ display:none !important; }}
.stTextArea {{ margin-top:0 !important; }}
textarea {{
    background:{t['input_bg']} !important; border:1.5px solid {t['border']} !important;
    border-radius:14px !important; color:{t['text']} !important;
    font-size:1rem !important; font-family:'Plus Jakarta Sans',sans-serif !important;
}}
textarea::placeholder {{ color:{t['text3']} !important; }}
textarea:focus {{ outline:none; border-color:{t['accent']} !important; box-shadow:0 0 0 3px {t['accent']}22 !important; }}

/* buttons */
div.stButton > button {{
    width:100%; background:linear-gradient(135deg,#0EA5E9,#6366F1);
    color:#fff !important; border:none; border-radius:14px;
    padding:0.8rem 2rem; font-weight:600; font-size:1rem;
    transition:all 0.18s; box-shadow:0 4px 20px rgba(14,165,233,0.3);
    font-family:'Plus Jakarta Sans',sans-serif !important;
}}
div.stButton > button[kind="secondary"] {{
    background:{t['surface']} !important; color:{t['text2']} !important;
    border:1px solid {t['border2']} !important; box-shadow:none !important;
}}
div.stButton > button[kind="secondary"]:hover {{
    border-color:{t['accent']} !important; color:{t['accent']} !important; transform:translateY(-1px);
}}
div.stButton > button:hover {{ transform:translateY(-2px); box-shadow:0 8px 32px rgba(14,165,233,0.45); }}

/* cards */
.el-card {{
    background:{t['surface']}; border:1px solid {t['border2']}; border-radius:20px;
    padding:1.8rem; margin-bottom:1.2rem; position:relative; overflow:hidden;
    box-shadow:0 4px 24px {t['shadow']}; animation:fadeUp 0.45s ease both;
}}
.el-card-accent::before {{
    content:''; position:absolute; top:0; left:0; right:0;
    height:3px; background:var(--accent,{t['accent']});
}}

/* hero */
.hero {{ text-align:center; padding:2rem 1rem 1.2rem; animation:fadeDown 0.65s ease both; }}
.hero-badge {{
    display:inline-block; font-family:'Space Mono',monospace; font-size:0.68rem;
    letter-spacing:0.2em; text-transform:uppercase; color:{t['accent']};
    background:{t['accent']}18; border:1px solid {t['accent']}40;
    border-radius:999px; padding:4px 16px; margin-bottom:1rem;
}}
.hero-title {{
    font-size:clamp(2.4rem,5vw,3.6rem); font-weight:700; letter-spacing:-0.03em; line-height:1.1;
    background:linear-gradient(135deg,{t['text']} 0%,{t['accent']} 50%,#818CF8 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0 0 0.6rem;
}}
.hero-sub {{ font-size:1rem; color:{t['text2']}; margin:0; }}

/* section label */
.slabel {{
    font-family:'Space Mono',monospace; font-size:0.62rem;
    letter-spacing:0.16em; text-transform:uppercase; color:{t['text2']}; margin-bottom:1rem;
}}
.slabel span {{ color:{t['accent']}; margin-right:6px; }}

/* top-emotion block */
.top-block {{ display:flex; align-items:center; gap:1.6rem; flex-wrap:wrap; }}
.emo-emoji-big {{ font-size:4.5rem; line-height:1; animation:bounceIn 0.6s ease; }}
.emo-name {{ font-size:2.4rem; font-weight:700; text-transform:capitalize; }}
.emo-conf {{ font-size:0.9rem; color:{t['text2']}; margin-top:4px; }}
.emo-conf strong {{ color:{t['text']}; }}

/* probability bars */
.prob-list {{ display:flex; flex-direction:column; gap:0.5rem; }}
.prob-row {{ display:grid; grid-template-columns:138px 1fr 50px; align-items:center; gap:0.65rem; }}
.prob-name {{ font-size:0.82rem; color:{t['text2']}; text-align:right; text-transform:capitalize; }}
.prob-track {{ height:9px; background:{t['track']}; border-radius:99px; overflow:hidden; }}
.prob-fill  {{ height:100%; border-radius:99px; transition:width 0.7s ease; }}
.prob-pct   {{ font-family:'Space Mono',monospace; font-size:0.72rem; color:{t['text3']}; }}
.prob-row.tb .prob-name {{ color:{t['text']}; font-weight:700; }}
.prob-row.tb .prob-pct  {{ color:{t['text']}; font-weight:700; }}

/* file uploader */
[data-testid="stFileUploader"] > label {{ display:none !important; }}
[data-testid="stFileUploader"] section {{
    background:{t['input_bg']} !important; border:2px dashed {t['border']} !important;
    border-radius:14px !important; padding:2rem 1rem !important; transition:border-color 0.2s;
}}
[data-testid="stFileUploader"] section:hover {{ border-color:{t['accent']} !important; }}
[data-testid="stFileUploader"] section p,
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section small {{ color:{t['text2']} !important; }}
[data-testid="stFileUploader"] button {{
    background:{t['surface']} !important; color:{t['accent']} !important;
    border:1px solid {t['border']} !important; border-radius:8px !important;
}}
.file-preview {{
    background:{t['input_bg']}; border:1px solid {t['border']}; border-radius:14px;
    padding:1rem 1.2rem; margin-top:0.8rem; max-height:180px; overflow-y:auto;
    font-size:0.88rem; color:{t['text2']}; line-height:1.6; white-space:pre-wrap;
}}
.file-meta {{
    display:flex; align-items:center; gap:10px; margin-bottom:0.7rem;
    font-family:'Space Mono',monospace; font-size:0.68rem;
    color:{t['accent']}; letter-spacing:0.1em;
}}

/* misc */
.tip {{
    background:{t['tip_bg']}; border:1px solid {t['tip_bdr']}; border-radius:14px;
    padding:0.85rem 1.2rem; color:{t['tip_txt']}; font-size:0.85rem; margin-bottom:1.2rem;
}}
hr.div {{ border:none; border-top:1px solid {t['border2']}; margin:1.2rem 0; }}
.footer {{ text-align:center; padding:2rem 1rem 1rem; color:{t['footer']}; font-size:0.72rem; font-family:'Space Mono',monospace; }}

@keyframes fadeDown {{ from{{opacity:0;transform:translateY(-18px)}} to{{opacity:1;transform:translateY(0)}} }}
@keyframes fadeUp   {{ from{{opacity:0;transform:translateY(16px)}}  to{{opacity:1;transform:translateY(0)}} }}
@keyframes bounceIn {{ 0%{{transform:scale(0.3);opacity:0}} 55%{{transform:scale(1.1)}} 100%{{transform:scale(1);opacity:1}} }}
</style>""", unsafe_allow_html=True)