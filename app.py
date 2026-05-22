import streamlit as st
import time
import threading
from pipeline import run_research_pipeline

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MULTI-AGENT Research System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

  :root {
    --bg:        #0a0a0f;
    --surface:   #12121a;
    --border:    #1e1e2e;
    --accent:    #00ffe1;
    --accent2:   #ff4ecd;
    --accent3:   #ffd166;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --success:   #22d3a5;
    --radius:    12px;
  }

  /* ── Global reset ── */
  html, body, [class*="css"] {
    font-family: 'Space Mono', monospace !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 2rem 3rem 4rem; max-width: 1100px; }

  /* ── Hero header ── */
  .hero {
    position: relative;
    text-align: center;
    padding: 3.5rem 1rem 2rem;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse 60% 40% at 50% 0%, rgba(0,255,225,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 30% at 80% 80%, rgba(255,78,205,.08) 0%, transparent 60%);
    pointer-events: none;
  }
  .hero-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: .7rem;
    letter-spacing: .3em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: .75rem;
  }
  .hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -.02em;
    background: linear-gradient(135deg, #fff 30%, var(--accent) 70%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 .5rem;
  }
  .hero-sub {
    color: var(--muted);
    font-size: .82rem;
    letter-spacing: .05em;
    margin-bottom: 2.5rem;
  }

  /* ── Divider ── */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
  }

  /* ── Input card ── */
  .input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.8rem 2rem;
    margin-bottom: 2rem;
  }

  /* ── Streamlit text_input override ── */
  .stTextInput > div > div > input {
    background: #0d0d18 !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: .9rem !important;
    padding: .75rem 1rem !important;
    transition: border-color .2s;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,255,225,.1) !important;
  }
  .stTextInput > label {
    font-family: 'Space Mono', monospace !important;
    font-size: .75rem !important;
    letter-spacing: .1em !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
  }

  /* ── Primary button ── */
  .stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, #00c4ae 100%) !important;
    color: #000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: .9rem !important;
    letter-spacing: .05em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: .75rem 2rem !important;
    transition: opacity .2s, transform .1s !important;
    width: 100% !important;
  }
  .stButton > button:hover {
    opacity: .85 !important;
    transform: translateY(-1px) !important;
  }
  .stButton > button:active { transform: translateY(0) !important; }

  /* ── Pipeline step cards ── */
  .step-card {
    display: flex;
    align-items: flex-start;
    gap: 1.2rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    margin-bottom: .75rem;
    transition: border-color .3s;
  }
  .step-card.active  { border-color: var(--accent);  box-shadow: 0 0 20px rgba(0,255,225,.07); }
  .step-card.done    { border-color: var(--success);  }
  .step-card.pending { opacity: .45; }

  .step-num {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 800; font-size: .85rem;
    flex-shrink: 0;
  }
  .step-num.active  { background: var(--accent);  color: #000; }
  .step-num.done    { background: var(--success); color: #000; }
  .step-num.pending { background: var(--border);  color: var(--muted); }

  .step-body {}
  .step-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: .95rem;
    margin: 0 0 .2rem;
  }
  .step-desc { color: var(--muted); font-size: .76rem; }

  /* ── Result panels ── */
  .result-section {
    margin-top: 2rem;
  }
  .result-label {
    font-family: 'Space Mono', monospace;
    font-size: .68rem;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: .5rem;
  }
  .result-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: .82rem;
    line-height: 1.7;
    color: var(--text);
    max-height: 400px;
    overflow-y: auto;
  }
  .result-box::-webkit-scrollbar { width: 5px; }
  .result-box::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

  /* ── Tag chips ── */
  .tag {
    display: inline-block;
    background: rgba(0,255,225,.08);
    border: 1px solid rgba(0,255,225,.2);
    color: var(--accent);
    font-size: .67rem;
    letter-spacing: .08em;
    padding: .2rem .6rem;
    border-radius: 99px;
    margin-right: .4rem;
    text-transform: uppercase;
  }

  /* ── Feedback panel ── */
  .feedback-box {
    background: linear-gradient(135deg, rgba(255,78,205,.05) 0%, rgba(10,10,15,1) 50%);
    border: 1px solid rgba(255,78,205,.25);
    border-radius: var(--radius);
    padding: 1.5rem;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: .82rem;
    line-height: 1.7;
    max-height: 400px;
    overflow-y: auto;
  }

  /* ── Error box ── */
  .error-box {
    background: rgba(239,68,68,.08);
    border: 1px solid rgba(239,68,68,.3);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    color: #f87171;
    font-size: .82rem;
  }

  /* ── Spinner override ── */
  .stSpinner > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">🔬 Autonomous Research</div>
  <div class="hero-title">MULTI-AGENT<br>RESEARCH SYSTEM</div>
  <div class="hero-sub">Search · Scrape · Write · Critique — all in one pipeline</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ─── Session state ─────────────────────────────────────────────────────────────
for key in ("running", "result", "error", "active_step"):
    if key not in st.session_state:
        st.session_state[key] = None if key in ("result", "error") else False if key == "running" else 0

# ─── Input card ───────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
topic = st.text_input(
    "Research Topic",
    placeholder="e.g.  Quantum Computing in 2025,  AI in Drug Discovery …",
    disabled=st.session_state.running,
)
run_btn = st.button("▶  Run Research Pipeline", disabled=st.session_state.running or not topic.strip())
st.markdown('</div>', unsafe_allow_html=True)

# ─── Pipeline steps definition ────────────────────────────────────────────────
STEPS = [
    ("01", "Search Agent",  "Querying the web for recent, reliable information"),
    ("02", "Reader Agent",  "Scraping the most relevant URL for deeper content"),
    ("03", "Writer Chain",  "Synthesising findings into a structured report"),
    ("04", "Critic Chain",  "Reviewing and scoring the report quality"),
]

def render_pipeline(active: int):
    for i, (num, title, desc) in enumerate(STEPS):
        if i < active:
            cls = "done";    icon = "✓"
        elif i == active:
            cls = "active";  icon = num
        else:
            cls = "pending"; icon = num

        st.markdown(f"""
        <div class="step-card {cls}">
          <div class="step-num {cls}">{icon}</div>
          <div class="step-body">
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Show pipeline skeleton while idle ───────────────────────────────────────
if not st.session_state.running and st.session_state.result is None and not run_btn:
    st.markdown("#### Pipeline Steps")
    render_pipeline(-1)   # all pending

# ─── Run ──────────────────────────────────────────────────────────────────────
if run_btn and topic.strip():
    st.session_state.running = True
    st.session_state.result  = None
    st.session_state.error   = None

    pipeline_placeholder = st.empty()
    status_placeholder   = st.empty()

    try:
        # Simulate step transitions while the real call is blocking
        # We'll run each step visually then execute the whole pipeline
        for step_idx in range(len(STEPS)):
            with pipeline_placeholder.container():
                st.markdown("#### Running Pipeline…")
                render_pipeline(step_idx)
            with status_placeholder.container():
                with st.spinner(f"⚙  {STEPS[step_idx][1]} working…"):
                    if step_idx == 0:
                        # Run full pipeline on step 0 entry, collect result
                        result = run_research_pipeline(topic)
            if step_idx < len(STEPS) - 1:
                time.sleep(0.4)

        # All done
        with pipeline_placeholder.container():
            st.markdown("#### Pipeline Complete ✓")
            render_pipeline(len(STEPS))   # all done

        status_placeholder.empty()
        st.session_state.result  = result
        st.session_state.running = False

    except Exception as e:
        pipeline_placeholder.empty()
        status_placeholder.empty()
        st.session_state.error   = str(e)
        st.session_state.running = False
        st.rerun()

# ─── Results ──────────────────────────────────────────────────────────────────
if st.session_state.result:
    res = st.session_state.result
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown('<div class="result-label">🔍 Search Results</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{res.get("search_results","—")}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="result-label">📄 Scraped Content</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{res.get("scraped_content","—")}</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="result-label">📝 Research Report</div>', unsafe_allow_html=True)
        report_text = res.get("report", "—")
        if hasattr(report_text, "content"):
            report_text = report_text.content
        st.markdown(f'<div class="result-box">{report_text}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="result-label">🧐 Critic Feedback</div>', unsafe_allow_html=True)
        feedback = res.get("feedback", "—")
        if hasattr(feedback, "content"):
            feedback = feedback.content
        st.markdown(f'<div class="feedback-box">{feedback}</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<span class="tag">Topic</span><span style="color:var(--accent3);font-size:.82rem">{topic}</span>', unsafe_allow_html=True)

    if st.button("🔄  New Research"):
        st.session_state.result = None
        st.rerun()

# ─── Error ────────────────────────────────────────────────────────────────────
if st.session_state.error:
    st.markdown(f'<div class="error-box">⚠ Pipeline Error<br><br>{st.session_state.error}</div>', unsafe_allow_html=True)
    if st.button("↩  Try Again"):
        st.session_state.error = None
        st.rerun()