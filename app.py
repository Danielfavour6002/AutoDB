import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.architect import build_sql
from my_utils.llm_handler import generate_sql_func

st.set_page_config(page_title="AutoDB", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ═══ RESET ═══ */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp, [class*="css"] {
    background: #12111a !important;
    font-family: 'Inter', sans-serif;
    color: #c9c9d4;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ═══ APP SHELL ═══ */
.app-shell {
    display: flex;
    height: 100vh;
    width: 100%;
    overflow: hidden;
}

/* ═══ SIDEBAR PANEL ═══ */
.sidebar-panel {
    width: 240px;
    min-width: 240px;
    background: #0e0d16;
    border-right: 1px solid #1e1d2e;
    display: flex;
    flex-direction: column;
    padding: 20px 16px;
    gap: 6px;
}
.brand {
    display: flex; align-items: center; gap: 9px;
    padding: 4px 0 20px;
    border-bottom: 1px solid #1a1928;
    margin-bottom: 14px;
}
.brand-icon {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; color: #fff; font-weight: 700;
    box-shadow: 0 4px 14px #7c3aed30;
}
.brand-name { font-size: 0.92rem; font-weight: 600; color: #e8e8f0; letter-spacing: -0.2px; }
.brand-sub  { font-size: 0.6rem; color: #4a4860; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 1px; }

.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 12px; border-radius: 8px;
    font-size: 0.82rem; color: #4a4860; cursor: pointer;
    border: 1px solid transparent; transition: all 0.15s;
    text-decoration: none;
}
.nav-item:hover { background: #161528; color: #8884a8; border-color: #1e1d2e; }
.nav-item.active { background: #1c1a30; color: #a78bfa; border-color: #2d2a4a; }
.nav-icon { font-size: 0.9rem; width: 16px; text-align: center; }

.sidebar-bottom {
    margin-top: auto;
    padding-top: 16px;
    border-top: 1px solid #1a1928;
}
.conn-status {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 12px; border-radius: 8px;
    background: #161528; border: 1px solid #1e1d2e;
    font-size: 0.76rem; color: #4a4860;
}
.pulse { width: 7px; height: 7px; border-radius: 50%; background: #333; flex-shrink: 0; }
.pulse.on  { background: #4ade80; box-shadow: 0 0 0 2px #4ade8020; animation: pulse 2s infinite; }
.pulse.sandox { background: #7c3aed; box-shadow: 0 0 0 2px #7c3aed20; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }

/* ═══ MAIN AREA ═══ */
.main-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

/* ═══ TOPBAR ═══ */
.topbar {
    height: 52px; min-height: 52px;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 24px;
    background: #0e0d16;
    border-bottom: 1px solid #1e1d2e;
}
.topbar-title { font-size: 0.82rem; font-weight: 500; color: #6b6880; letter-spacing: 0.3px; }
.model-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: #4a4860;
    background: #161528; border: 1px solid #1e1d2e;
    padding: 3px 9px; border-radius: 20px; letter-spacing: 0.5px;
}

/* ═══ TOGGLE SWITCH ═══ */
.toggle-wrap {
    display: flex; align-items: center;
    background: #161528;
    border: 1px solid #1e1d2e;
    border-radius: 10px;
    padding: 4px; gap: 2px;
}
.toggle-opt {
    padding: 6px 18px; border-radius: 7px;
    font-size: 0.74rem; font-weight: 500;
    letter-spacing: 0.3px; cursor: pointer;
    transition: all 0.18s ease;
    color: #4a4860; border: 1px solid transparent;
}
.toggle-opt.selected {
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    color: #fff;
    box-shadow: 0 2px 12px #7c3aed30;
}

/* ═══ STREAMLIT RADIO AS TOGGLE ═══ */
div[data-testid="stRadio"] > div {
    display: flex !important;
    background: #161528 !important;
    border: 1px solid #1e1d2e !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 3px !important;
    width: fit-content !important;
}
div[data-testid="stRadio"] label {
    padding: 7px 20px !important;
    border-radius: 7px !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    color: #4a4860 !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
    border: 1px solid transparent !important;
    margin: 0 !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    color: #fff !important;
    box-shadow: 0 2px 12px #7c3aed30 !important;
}
div[data-testid="stRadio"] [data-baseweb="radio"] { display: none !important; }
div[data-testid="stRadio"] > label { display: none !important; }

/* ═══ CONTENT AREA ═══ */
.content-area { flex: 1; overflow-y: auto; padding: 28px 28px 20px; }
.content-area::-webkit-scrollbar { width: 4px; }
.content-area::-webkit-scrollbar-thumb { background: #1e1d2e; border-radius: 4px; }

/* ═══ SECTION LABELS ═══ */
.sec-label {
    font-size: 0.6rem; font-weight: 600;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: #3a3850; margin-bottom: 10px;
}
.sec-desc { font-size: 0.82rem; color: #3a3850; line-height: 1.6; margin-bottom: 18px; }

/* ═══ PROMPT AREA ═══ */
.prompt-wrap {
    background: #161528;
    border: 1px solid #1e1d2e;
    border-radius: 12px;
    padding: 2px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.prompt-wrap:focus-within { border-color: #7c3aed40; box-shadow: 0 0 0 3px #7c3aed0a; }

.stTextArea textarea {
    background: transparent !important;
    border: none !important;
    border-radius: 11px !important;
    color: #c0bfd4 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
    line-height: 1.65 !important;
    resize: none !important;
    padding: 14px 16px !important;
    box-shadow: none !important;
}
.stTextArea textarea::placeholder { color: #2e2c48 !important; }
.stTextArea textarea:focus { box-shadow: none !important; border: none !important; }
div[data-testid="stTextArea"] > div { border: none !important; background: transparent !important; }

.ai-ready-tag {
    text-align: right; font-size: 0.64rem;
    color: #2e2c48; letter-spacing: 1px;
    padding: 0 4px 4px;
}
.ai-ready-tag span { color: #7c3aed; font-weight: 500; }

/* ═══ GENERATE BUTTON ═══ */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    border-radius: 10px !important;
    height: 44px !important;
    transition: all 0.18s ease !important;
    border: none !important;
    letter-spacing: 0.2px !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    color: #fff !important;
    box-shadow: 0 4px 20px #7c3aed25 !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 28px #7c3aed40 !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: #161528 !important;
    color: #6b6880 !important;
    border: 1px solid #1e1d2e !important;
    height: 38px !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #1c1a30 !important;
    border-color: #2d2a4a !important;
    color: #8884a8 !important;
}
.stButton > button:disabled {
    background: #12111a !important;
    color: #1e1d2e !important;
    border: 1px solid #161528 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ═══ CODE OUTPUT ═══ */
.code-container {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #1e1d2e;
    margin-top: 24px;
}
.code-bar {
    background: #161528;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1e1d2e;
}
.code-dots { display: flex; gap: 6px; }
.cd { width: 10px; height: 10px; border-radius: 50%; }
.cd1 { background: #ff5f57; } .cd2 { background: #febc2e; } .cd3 { background: #28c840; }
.code-bar-right { display: flex; align-items: center; gap: 10px; }
.dialect-tag {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    color: #7c3aed; background: #7c3aed12; border: 1px solid #7c3aed25;
    padding: 2px 8px; border-radius: 4px; letter-spacing: 0.5px; text-transform: uppercase;
}
.schema-tag {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    color: #3a3850; letter-spacing: 0.3px;
}
[data-testid="stCode"] {
    border-radius: 0 !important; border: none !important; margin: 0 !important;
}
[data-testid="stCode"] pre {
    background: #0e0d16 !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.79rem !important;
    line-height: 1.75 !important;
    padding: 22px !important;
    margin: 0 !important;
}

/* ═══ ANALYST CHAT ═══ */
.analyst-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px;
}
.analyst-title { font-size: 0.9rem; font-weight: 600; color: #d0cfe0; }
.analyst-sub   { font-size: 0.72rem; color: #4a4860; margin-top: 2px; }

.connect-card {
    background: #161528;
    border: 1px solid #1e1d2e;
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}
.connect-card-left { display: flex; align-items: center; gap: 12px; }
.connect-card-icon {
    width: 34px; height: 34px;
    background: #7c3aed18; border: 1px solid #7c3aed25;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
}
.connect-card-title { font-size: 0.84rem; font-weight: 500; color: #9896b0; }
.connect-card-sub   { font-size: 0.74rem; color: #3a3850; margin-top: 2px; }

.bot-bubble {
    background: #161528;
    border: 1px solid #1e1d2e;
    border-radius: 14px 14px 14px 4px;
    padding: 16px 20px;
    margin-bottom: 20px;
    display: flex; gap: 14px; align-items: flex-start;
    max-width: 85%;
}
.bot-avatar {
    width: 32px; height: 32px; flex-shrink: 0;
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; color: #fff; box-shadow: 0 3px 10px #7c3aed30;
}
.bot-text { font-size: 0.84rem; color: #8886a8; line-height: 1.65; }
.bot-text b { color: #a78bfa; font-weight: 500; }

[data-testid="stChatMessage"] {
    background: #161528 !important; border: 1px solid #1e1d2e !important;
    border-radius: 12px !important; margin-bottom: 10px !important; padding: 14px 18px !important;
}
[data-testid="stChatInputTextArea"] {
    background: #161528 !important; border: 1px solid #1e1d2e !important;
    color: #c0bfd4 !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important; border-radius: 10px !important;
}

/* ═══ INPUTS MISC ═══ */
.stTextInput input {
    background: #161528 !important; border: 1px solid #1e1d2e !important;
    border-radius: 8px !important; color: #b0afc4 !important;
    font-size: 0.83rem !important; font-family: 'Inter', sans-serif !important;
    padding: 10px 14px !important;
}
.stTextInput input::placeholder { color: #2e2c48 !important; }
.stTextInput input:focus { border-color: #7c3aed30 !important; box-shadow: none !important; }

[data-testid="stSelectbox"] > div > div {
    background: #161528 !important; border: 1px solid #1e1d2e !important;
    border-radius: 8px !important; color: #6b6880 !important; font-size: 0.83rem !important;
}

/* ═══ ALERTS ═══ */
.stAlert, [data-testid="stAlert"] {
    background: #161528 !important; border: 1px solid #1e1d2e !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] p { color: #5a5870 !important; font-size: 0.82rem !important; }
.stSpinner > div { border-top-color: #7c3aed !important; }
hr { border-color: #1a1928 !important; margin: 14px 0 !important; }

/* ═══ HISTORY BUTTONS ═══ */
div[data-testid="stVerticalBlock"] .stButton > button[kind="secondary"] {
    height: auto !important;
    padding: 8px 12px !important;
    text-align: left !important;
    font-size: 0.76rem !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for k, v in {
    "history": [], "generated_sql": [], "db_connected": False,
    "db_url": "", "mode": "Architect", "dialect": "postgresql", "chat_messages": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

DIALECTS = {
    "PostgreSQL": "postgresql", "MySQL": "mysql", "SQLite": "sqlite",
    "SQL Server": "mssql", "Oracle": "oracle", "MariaDB": "mariadb",
}

# ══════════════════════════════════════════════════
# LAYOUT: SIDEBAR | MAIN
# ══════════════════════════════════════════════════
sidebar_col, main_col = st.columns([0.85, 3.4], gap="small")

# ════════════════════════════════
# SIDEBAR
# ════════════════════════════════
with sidebar_col:
    # Brand
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">◈</div>
        <div>
            <div class="brand-name">AutoDB</div>
            <div class="brand-sub">Architect Mode</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label" style="margin-bottom:10px;">Settings</div>', unsafe_allow_html=True)

    # Mode in sidebar (dialect / db url)
    if st.session_state.mode == "Architect":
        st.markdown('<div class="sec-label">Dialect</div>', unsafe_allow_html=True)
        chosen = st.selectbox("dialect", list(DIALECTS.keys()), label_visibility="collapsed")
        st.session_state.dialect = DIALECTS[chosen]
    else:
        st.markdown('<div class="sec-label">Database URL</div>', unsafe_allow_html=True)
        db_input = st.text_input(
            "url", placeholder="postgresql://user:pass@host/db",
            type="password", label_visibility="collapsed"
        )
        if st.button("Connect", type="primary", use_container_width=True):
            if db_input.strip():
                st.session_state.db_url = db_input
                st.session_state.db_connected = True
            else:
                st.warning("Enter a database URL")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:#1a1928;margin-bottom:14px;"></div>', unsafe_allow_html=True)

    # History
    st.markdown('<div class="sec-label">History</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown('<p style="font-size:0.74rem;color:#2a2840;margin:0;">No queries yet.</p>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history[-7:])):
            lbl = item["prompt"][:30] + "…" if len(item["prompt"]) > 30 else item["prompt"]
            if st.button(f"↩  {lbl}", key=f"h{i}", use_container_width=True, type="secondary"):
                st.session_state.generated_sql = item["sql"]
                st.session_state.dialect = item["dialect"]

    # Connection status at bottom
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.mode == "Analyst" and st.session_state.db_connected:
        st.markdown('<div class="conn-status"><div class="pulse on"></div>Database connected</div>', unsafe_allow_html=True)
    elif st.session_state.mode == "Analyst":
        st.markdown('<div class="conn-status"><div class="pulse"></div>Not connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="conn-status"><div class="pulse sandox"></div>Sandbox mode</div>', unsafe_allow_html=True)

# ════════════════════════════════
# MAIN AREA
# ════════════════════════════════
with main_col:

    # ── TOPBAR ──
    top_l, top_r = st.columns([3, 1])
    with top_l:
        mode_label = "Architect — Build Schema" if st.session_state.mode == "Architect" else "Analyst — Query Data"
        st.markdown(f'<div style="padding:14px 0 10px;font-size:0.78rem;color:#3a3850;font-weight:500;letter-spacing:0.3px;">{mode_label}</div>', unsafe_allow_html=True)
    with top_r:
        st.markdown('<div style="padding-top:8px;"></div>', unsafe_allow_html=True)
        mode = st.radio("view", ["Architect", "Analyst"], horizontal=True, label_visibility="collapsed", key="mode_toggle")
        st.session_state.mode = mode

    st.markdown('<div style="height:1px;background:#1e1d2e;margin-bottom:24px;"></div>', unsafe_allow_html=True)

    # ══════════════════════
    # ARCHITECT VIEW
    # ══════════════════════
    if st.session_state.mode == "Architect":

        st.markdown('<div class="sec-label">Natural Language Prompt</div>', unsafe_allow_html=True)

        st.markdown('<div class="prompt-wrap">', unsafe_allow_html=True)
        prompt = st.text_area(
            "prompt", height=150, label_visibility="collapsed",
            placeholder="Describe your database schema... e.g. 'Create a marketplace with users, products, and a review system.'"
        )
        st.markdown('<div class="ai-ready-tag">⚡ <span>AI READY</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        gen = st.button("✦  Generate SQL", type="primary", use_container_width=True)

        if gen:
            if not prompt.strip():
                st.warning("Describe your schema first.")
            else:
                with st.spinner("Analyzing and generating schema..."):
                    try:
                        raw   = generate_sql_func(prompt)
                        stmts = build_sql(raw, st.session_state.dialect)
                        st.session_state.generated_sql = stmts
                        st.session_state.history.append({
                            "prompt": prompt, "sql": stmts, "dialect": st.session_state.dialect
                        })
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

        # SQL Output
        if st.session_state.generated_sql:
            full_sql = "\n\n".join(st.session_state.generated_sql)
            n = len(st.session_state.generated_sql)

            st.markdown('<div style="margin-top:24px;">', unsafe_allow_html=True)
            st.markdown('<div class="sec-label">Generated Schema</div>', unsafe_allow_html=True)

            st.markdown(f"""
            <div class="code-container">
                <div class="code-bar">
                    <div class="code-dots">
                        <div class="cd cd1"></div>
                        <div class="cd cd2"></div>
                        <div class="cd cd3"></div>
                    </div>
                    <div class="code-bar-right">
                        <span class="dialect-tag">{st.session_state.dialect}</span>
                        <span class="schema-tag">schema.sql</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.code(full_sql, language="sql")
            st.markdown('</div>', unsafe_allow_html=True)

            # Table count below
            st.markdown(f'<div style="font-size:0.7rem;color:#2e2c48;margin-top:8px;text-align:right;">{n} table{"s" if n!=1 else ""} generated</div>', unsafe_allow_html=True)

    # ══════════════════════
    # ANALYST VIEW
    # ══════════════════════
    else:
        # Connect card if not connected
        if not st.session_state.db_connected:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown("""
                <div class="connect-card-left" style="padding:14px 0;">
                    <div class="connect-card-icon">◈</div>
                    <div>
                        <div class="connect-card-title">Ready to Connect</div>
                        <div class="connect-card-sub">Link your database to start querying.</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown('<div style="padding-top:10px;"></div>', unsafe_allow_html=True)
                if st.button("Connect", type="primary", use_container_width=True, key="analyst_connect_btn"):
                    st.info("Enter your database URL in the left panel.")

            st.markdown('<div style="height:1px;background:#1e1d2e;margin:16px 0;"></div>', unsafe_allow_html=True)

        # Bot greeting
        st.markdown("""
        <div class="bot-bubble">
            <div class="bot-avatar">◈</div>
            <div class="bot-text">
                Hello! I'm your <b>AutoDB Analyst</b>. I can help you analyze your database using plain English.<br><br>
                Once connected, just ask me anything!
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Chat messages
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Input
        user_msg = st.chat_input(
            "Connect a database first…" if not st.session_state.db_connected else "Ask your data...",
            disabled=not st.session_state.db_connected
        )
        if user_msg:
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            st.session_state.chat_messages.append({"role": "assistant", "content": "Analyst agent coming in next build — wire core/chat.py here."})
            st.rerun()
