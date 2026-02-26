import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.architect import build_sql
from my_utils.llm_handler import generate_sql_func
from core.engine import get_engine, execute_sql
from core.chat import query_agent

st.set_page_config(
    page_title="AutoDB",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force sidebar open on desktop only — don't force on mobile (it covers screen)
components.html("""
<script>
(function() {
    const isMobile = window.innerWidth <= 768;
    if (!isMobile) {
        for (let key of Object.keys(localStorage)) {
            if (key.toLowerCase().includes('sidebar')) {
                localStorage.removeItem(key);
            }
        }
    }
})();
</script>
""", height=0)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, .stApp, [class*="css"] {
    background: #0d0c14 !important;
    font-family: 'Inter', sans-serif;
    color: #c9c9d4;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; }

/* ── Hide collapse arrow on DESKTOP only ── */
@media (min-width: 769px) {
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] { display: none !important; }
}

/* ── On MOBILE: style the open toggle nicely ── */
@media (max-width: 768px) {
    [data-testid="collapsedControl"] {
        background: #12111e !important;
        border: 1px solid #1e1d2e !important;
        border-radius: 8px !important;
        top: 1rem !important;
        left: 0.75rem !important;
    }
    [data-testid="collapsedControl"] svg { color: #a78bfa !important; }
    .block-container { padding: 1rem !important; }
    .section-head { font-size: 1.2rem !important; }
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0a0914 !important;
    border-right: 1px solid #1e1d2e !important;
    min-width: 240px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1rem !important; }

/* ── All sidebar text explicitly bright ── */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #c9c9d4 !important; }

.brand {
    font-size: 1.1rem; font-weight: 700; color: #a78bfa !important;
    display: flex; align-items: center; gap: 8px;
    padding-bottom: 1.2rem; border-bottom: 1px solid #1e1d2e;
    margin-bottom: 1.4rem;
}
.brand-icon {
    width: 26px; height: 26px;
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    border-radius: 6px; display: flex; align-items: center;
    justify-content: center; font-size: 0.72rem; color: #fff !important;
}
.sb-label {
    font-size: 0.6rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: #a78bfa !important; margin-bottom: 8px;
}

/* ── TOGGLE ── */
[data-testid="stToggle"] > label { color: #c9c9d4 !important; font-size: 0.83rem !important; }
[data-testid="stToggle"] > label > div { color: #c9c9d4 !important; }

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: #12111e !important; border: 1px solid #1e1d2e !important;
    border-radius: 8px !important; color: #c9c9d4 !important; font-size: 0.83rem !important;
}
[data-testid="stSelectbox"] svg { color: #a78bfa !important; }

/* ── TEXT INPUT ── */
.stTextInput input {
    background: #12111e !important; border: 1px solid #1e1d2e !important;
    border-radius: 8px !important; color: #c0bfd4 !important;
    font-size: 0.83rem !important; padding: 10px 13px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input::placeholder { color: #666 !important; opacity: 1 !important; }
.stTextInput input:focus { border-color: #7c3aed50 !important; box-shadow: none !important; }

/* ── CONN PILL ── */
.conn-pill {
    display: flex; align-items: center; gap: 7px;
    padding: 9px 12px; border-radius: 8px;
    background: #12111e; border: 1px solid #1e1d2e;
    font-size: 0.76rem; color: #c9c9d4 !important; margin-top: 8px;
}
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-sandbox { background: #7c3aed; }
.dot-on      { background: #4ade80; animation: blink 2.5s infinite; }
.dot-off     { background: #444; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ── MAIN HEADINGS ── */
.section-head {
    font-size: 1.6rem; font-weight: 700; color: #e8e8f0;
    letter-spacing: -0.5px; margin-bottom: 0.3rem;
}
.section-sub { font-size: 0.88rem; color: #aaa; margin-bottom: 2rem; line-height: 1.6; }

/* ── DIALECT BADGE (auto-detected) ── */
.dialect-badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.7rem; color: #a78bfa;
    background: #7c3aed15; border: 1px solid #7c3aed30;
    padding: 3px 10px; border-radius: 6px; margin-bottom: 1rem;
    font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px;
}

/* ── TEXTAREA ── */
.stTextArea textarea {
    background: #12111e !important; border: 1px solid #1e1d2e !important;
    border-radius: 12px !important; color: #d0cfe0 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.9rem !important;
    line-height: 1.65 !important; resize: none !important; padding: 18px 20px !important;
}
.stTextArea textarea::placeholder { color: #9ca3af !important; opacity: 1 !important; }
.stTextArea textarea:focus {
    border-color: #7c3aed50 !important; box-shadow: 0 0 0 3px #7c3aed0a !important;
}
div[data-testid="stTextArea"] > div { border: none !important; background: transparent !important; }

/* ── BUTTONS ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 0.86rem !important; border-radius: 10px !important;
    height: 46px !important; transition: all 0.15s ease !important; border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    color: #fff !important; box-shadow: 0 4px 18px #7c3aed25 !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 26px #7c3aed45 !important; transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: #12111e !important; color: #c9c9d4 !important;
    border: 1px solid #1e1d2e !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #16132a !important; border-color: #2a2450 !important; color: #a78bfa !important;
}
.stButton > button:disabled {
    background: #0d0c14 !important; color: #2a2a3a !important;
    border: 1px solid #12111e !important; box-shadow: none !important; transform: none !important;
}

/* ── CODE BLOCK ── */
.code-wrap { border-radius: 12px; overflow: hidden; border: 1px solid #1e1d2e; margin-top: 20px; }
.code-bar {
    background: #12111e; border-bottom: 1px solid #1e1d2e;
    padding: 10px 16px; display: flex; align-items: center; justify-content: space-between;
}
.code-dots { display: flex; gap: 6px; }
.cd { width: 10px; height: 10px; border-radius: 50%; }
.cd1{background:#ff5f57} .cd2{background:#febc2e} .cd3{background:#28c840}
.code-right { display: flex; align-items: center; gap: 10px; }
.dialect-tag {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    color: #a78bfa; background: #7c3aed15; border: 1px solid #7c3aed25;
    padding: 2px 8px; border-radius: 4px; letter-spacing: 0.5px; text-transform: uppercase;
}
.schema-name { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #aaa; }
[data-testid="stCode"] { border-radius: 0 !important; border: none !important; margin: 0 !important; }
[data-testid="stCode"] pre {
    background: #0a0914 !important; border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important; line-height: 1.75 !important;
    padding: 22px !important; margin: 0 !important;
}

/* ── ANALYST ── */
.locked-card {
    background: #12111e; border: 1px solid #1e1d2e;
    border-left: 2px solid #7c3aed; border-radius: 12px;
    padding: 18px 22px; margin-bottom: 24px;
}
.locked-title {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: #a78bfa; margin-bottom: 6px;
}
.locked-body { font-size: 0.84rem; color: #bbb; line-height: 1.6; }

.bot-bubble {
    background: #12111e; border: 1px solid #1e1d2e;
    border-radius: 14px 14px 14px 4px; padding: 16px 20px;
    margin-bottom: 24px; display: flex; gap: 14px; max-width: 75%;
}
.bot-avatar {
    width: 32px; height: 32px; flex-shrink: 0;
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    border-radius: 9px; display: flex; align-items: center;
    justify-content: center; font-size: 0.78rem; color: #fff;
}
.bot-text { font-size: 0.84rem; color: #bbb; line-height: 1.65; }
.bot-text b { color: #a78bfa; font-weight: 500; }

[data-testid="stChatMessage"] {
    background: #12111e !important; border: 1px solid #1e1d2e !important;
    border-radius: 12px !important; margin-bottom: 10px !important;
    padding: 14px 18px !important;
}
[data-testid="stChatMessage"] p { color: #d0cfe0 !important; font-size: 0.88rem !important; line-height: 1.6 !important; }

/* ── CHAT INPUT — styled like the textarea ── */
[data-testid="stChatInput"] {
    background: #12111e !important;
    border: 1px solid #2a2450 !important;
    border-radius: 14px !important;
    padding: 4px 8px !important;
    box-shadow: 0 0 0 3px #7c3aed0a !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #7c3aed80 !important;
    box-shadow: 0 0 0 3px #7c3aed15 !important;
}
[data-testid="stChatInputTextArea"] {
    background: transparent !important;
    border: none !important;
    color: #d0cfe0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 10px 12px !important;
}
[data-testid="stChatInputTextArea"]::placeholder { color: #666 !important; opacity: 1 !important; }
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    border-radius: 9px !important; border: none !important;
    color: #fff !important; margin: 4px !important;
}
[data-testid="stChatInput"] button:hover { opacity: 0.85 !important; }

/* ── ALERTS ── */
.stAlert, [data-testid="stAlert"] {
    background: #12111e !important; border: 1px solid #1e1d2e !important; border-radius: 10px !important;
}
[data-testid="stAlert"] p { color: #c9c9d4 !important; font-size: 0.83rem !important; }
.stSpinner > div { border-top-color: #7c3aed !important; }
hr { border-color: #1e1d2e !important; margin: 14px 0 !important; }
.stCaptionContainer p { color: #aaa !important; font-size: 0.78rem !important; }

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
    .bot-bubble { max-width: 100% !important; }
    .section-sub { font-size: 0.82rem !important; }
    [data-testid="stChatInput"] { border-radius: 12px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for k, v in {
    "generated_sql":   [],
    "db_connected":    False,
    "engine":          None,
    "db_url":          "",
    "chat_messages":   [],
    "history":         [],
    "analyst_history": [],
    "analyst_agent":   None,
    "menu":            "DB Architect",
    "detected_dialect": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

DIALECTS = {
    "PostgreSQL": "postgresql", "MySQL": "mysql",
    "SQLite":     "sqlite",     "SQL Server": "mssql",
    "Oracle":     "oracle",     "MariaDB": "mariadb",
}

DIALECT_FROM_URL = {
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "mysql":      "MySQL",      "sqlite":   "SQLite",
    "mssql":      "SQL Server", "oracle":   "Oracle",
    "mariadb":    "MariaDB",
}

def detect_dialect_from_url(url: str) -> str | None:
    """Auto-detect dialect name from connection string prefix."""
    if not url:
        return None
    prefix = url.split("://")[0].split("+")[0].lower()
    return DIALECT_FROM_URL.get(prefix)

dialect   = "postgresql"
live_mode = False
menu      = st.session_state.get("menu", "DB Architect")

# ════════════════════════════════
# SIDEBAR
# ════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">◈</div>
        AutoDB
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-label">Navigation</div>', unsafe_allow_html=True)
    nav_c1, nav_c2 = st.columns(2, gap="small")
    with nav_c1:
        if st.button("Architect", key="nav_arch", use_container_width=True,
                     type="primary" if st.session_state.menu == "DB Architect" else "secondary"):
            st.session_state.menu = "DB Architect"
            st.rerun()
    with nav_c2:
        if st.button("Analyst", key="nav_anal", use_container_width=True,
                     type="primary" if st.session_state.menu == "DB Analyst" else "secondary"):
            st.session_state.menu = "DB Analyst"
            st.rerun()
    menu = st.session_state.menu

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sb-label">Environment</div>', unsafe_allow_html=True)
    live_mode = st.toggle("Live Mode", value=False)

    if live_mode:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sb-label">Connection String</div>', unsafe_allow_html=True)
        db_url_input = st.text_input(
            "db_url", type="password",
            placeholder="postgresql://user:password@host/db",
            label_visibility="collapsed"
        )

        # Auto-detect dialect from URL
        detected = detect_dialect_from_url(db_url_input)
        if detected:
            st.markdown(f'<div class="dialect-badge">◈ &nbsp;{detected} detected</div>', unsafe_allow_html=True)
            dialect_name = detected
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="sb-label">SQL Dialect</div>', unsafe_allow_html=True)
            dialect_name = st.selectbox("Dialect", list(DIALECTS.keys()), label_visibility="collapsed")
        dialect = DIALECTS[dialect_name]

        if st.button("Connect", type="primary", use_container_width=True):
            if db_url_input.strip():
                with st.spinner("Connecting..."):
                    try:
                        engine = get_engine(db_url_input)
                        st.session_state.engine         = engine
                        st.session_state.db_url         = db_url_input
                        st.session_state.db_connected   = True
                        st.session_state.analyst_agent  = None
                        st.session_state.detected_dialect = dialect_name
                        st.success("Connected successfully")
                    except Exception as e:
                        st.session_state.db_connected = False
                        st.session_state.engine       = None
                        st.error(str(e))
            else:
                st.warning("Enter a connection string first.")

        if st.session_state.db_connected:
            st.markdown('<div class="conn-pill"><div class="dot dot-on"></div>Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="conn-pill"><div class="dot dot-off"></div>Not connected</div>', unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sb-label">SQL Dialect</div>', unsafe_allow_html=True)
        dialect_name = st.selectbox("Dialect", list(DIALECTS.keys()), label_visibility="collapsed")
        dialect = DIALECTS[dialect_name]
        st.session_state.db_connected  = False
        st.session_state.engine        = None
        st.session_state.analyst_agent = None
        st.markdown('<div class="conn-pill"><div class="dot dot-sandbox"></div>Sandbox mode</div>', unsafe_allow_html=True)

    has_arch    = bool(st.session_state.history)
    has_analyst = bool(st.session_state.analyst_history)

    if has_arch or has_analyst:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sb-label">History</div>', unsafe_allow_html=True)

    if has_arch:
        st.markdown('<div style="font-size:0.6rem;color:#888;margin-bottom:6px;margin-top:2px;letter-spacing:1px;">SCHEMAS</div>', unsafe_allow_html=True)
        for i, item in enumerate(reversed(st.session_state.history[-4:])):
            lbl = item["prompt"][:28] + "…" if len(item["prompt"]) > 28 else item["prompt"]
            if st.button(f"◫  {lbl}", key=f"h{i}", use_container_width=True, type="secondary"):
                st.session_state.generated_sql = item["sql"]
                st.session_state.menu = "DB Architect"
                st.rerun()

    if has_analyst:
        st.markdown('<div style="font-size:0.6rem;color:#888;margin-bottom:6px;margin-top:10px;letter-spacing:1px;">CONVERSATIONS</div>', unsafe_allow_html=True)
        for i, convo in enumerate(reversed(st.session_state.analyst_history[-4:])):
            first_user = next((m["content"] for m in convo if m["role"] == "user"), "Chat")
            lbl = first_user[:28] + "…" if len(first_user) > 28 else first_user
            if st.button(f"◈  {lbl}", key=f"c{i}", use_container_width=True, type="secondary"):
                st.session_state.chat_messages = list(convo)
                st.session_state.menu = "DB Analyst"
                st.rerun()

# ════════════════════════════════
# DB ARCHITECT
# ════════════════════════════════
if menu == "DB Architect":
    st.markdown('<div class="section-head">DB Architect</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Describe your database in plain English — tables, relationships, constraints. AutoDB handles the SQL.</div>',
        unsafe_allow_html=True
    )

    prompt = st.text_area(
        "prompt", height=180, label_visibility="collapsed",
        placeholder="e.g. 'Create a ride-hailing app with drivers, passengers, trips, payments, and ratings.'"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.3, 0.9], gap="small")
    with c1:
        gen_click = st.button("✦  Generate SQL", type="primary", use_container_width=True)
    with c2:
        push_ready = live_mode and st.session_state.db_connected
        push_click = st.button("🗄  Push to DB", type="secondary",
                               disabled=not push_ready, use_container_width=True)
    with c3:
        if st.button("✕  Clear", type="secondary", use_container_width=True):
            st.session_state.generated_sql = []
            st.rerun()

    if gen_click:
        if not prompt.strip():
            st.warning("Describe your schema first.")
        else:
            with st.spinner("Generating schema..."):
                try:
                    raw   = generate_sql_func(prompt)
                    stmts = build_sql(raw, dialect)
                    st.session_state.generated_sql = stmts
                    st.session_state.history.append({
                        "prompt": prompt, "sql": stmts, "dialect": dialect
                    })
                except Exception as e:
                    st.error(f"Generation failed: {e}")

    if push_click and push_ready:
        if st.session_state.generated_sql:
            with st.spinner("Pushing schema to database..."):
                try:
                    execute_sql(st.session_state.engine, st.session_state.generated_sql)
                    st.success("Schema pushed successfully.")
                except Exception as e:
                    st.error(f"Push failed: {e}")
        else:
            st.warning("Generate a schema first.")

    if st.session_state.generated_sql:
        full_sql = "\n\n".join(st.session_state.generated_sql)
        n = len(st.session_state.generated_sql)
        st.markdown(f"""
        <div class="code-wrap">
            <div class="code-bar">
                <div class="code-dots">
                    <div class="cd cd1"></div><div class="cd cd2"></div><div class="cd cd3"></div>
                </div>
                <div class="code-right">
                    <span class="dialect-tag">{dialect}</span>
                    <span class="schema-name">schema.sql &nbsp;·&nbsp; {n} table{"s" if n != 1 else ""}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.code(full_sql, language="sql")

# ════════════════════════════════
# DB ANALYST
# ════════════════════════════════
if menu == "DB Analyst":
    st.markdown('<div class="section-head">DB Analyst</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Query your database in plain English. No SQL knowledge required.</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.db_connected:
        st.markdown("""
        <div class="locked-card">
            <div class="locked-title">Connection Required</div>
            <div class="locked-body">
                Enable <b>Live Mode</b> in the sidebar, enter your database connection string, and click Connect.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="bot-bubble">
        <div class="bot-avatar">◈</div>
        <div class="bot-text">
            Hello! I'm your <b>AutoDB Analyst</b>. Connect your database and ask me anything in plain English.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.db_connected:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_msg = st.chat_input("Ask your data... e.g. 'Show top 5 customers by revenue this month'")
        if user_msg:
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            with st.spinner("Thinking..."):
                answer, model_used = query_agent(st.session_state.engine, user_msg)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})

            if st.session_state.analyst_history and \
               st.session_state.analyst_history[-1][0]["content"] == st.session_state.chat_messages[0]["content"]:
                st.session_state.analyst_history[-1] = list(st.session_state.chat_messages)
            else:
                st.session_state.analyst_history.append(list(st.session_state.chat_messages))
            st.rerun()

        if st.session_state.chat_messages:
            if st.button("Clear chat", type="secondary"):
                st.session_state.chat_messages = []
                st.rerun()