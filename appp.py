import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.architect import build_sql
from my_utils.llm_handler import generate_sql_func

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="AutoDB",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── BASE ── */
.stApp { background-color: #050505 !important; color: #d1d1d1; font-family: 'Inter', sans-serif; }
[data-testid="stHeader"] { visibility: hidden; }
.block-container { padding: 2rem 3.5rem !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: #080808 !important;
    border-right: 1px solid #111 !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem !important; }

/* ── BRAND ── */
.brand { font-size: 1.4rem; font-weight: 700; color: #6366f1; margin-bottom: 2rem; display: flex; align-items: center; gap: 8px; }

/* ── SIDEBAR SECTION LABELS ── */
.sidebar-label {
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #555; margin-bottom: 12px; margin-top: 4px;
}

/* ── NAV RADIO (pill toggle style) ── */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
div[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    border-radius: 9px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #444 !important;
    cursor: pointer !important;
    border: 1px solid transparent !important;
    transition: all 0.15s ease !important;
    margin: 0 !important;
    background: transparent !important;
}
div[data-testid="stRadio"] label:hover {
    background: #111 !important;
    color: #888 !important;
    border-color: #181818 !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: #0f0f1a !important;
    color: #a78bfa !important;
    border-color: #1e1c35 !important;
}
div[data-testid="stRadio"] [data-baseweb="radio"] { display: none !important; }

/* ── LIVE TOGGLE ── */
[data-testid="stToggle"] > div > div {
    background-color: #6366f1 !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: #0a0a0a !important;
    border: 1px solid #181818 !important;
    border-radius: 8px !important;
    color: #888 !important;
    font-size: 0.83rem !important;
}

/* ── TEXT INPUTS ── */
.stTextInput input {
    background: #080808 !important;
    border: 1px solid #181818 !important;
    border-radius: 9px !important;
    color: #d1d1d1 !important;
    font-size: 0.86rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 14px !important;
}
.stTextInput input::placeholder { color: #9ca3af !important; opacity: 1 !important; }
.stTextInput input:focus { border-color: #6366f130 !important; box-shadow: none !important; }

/* ── MAIN HEADINGS ── */
.section-head {
    font-size: 1.75rem; font-weight: 700;
    color: #fff; letter-spacing: -0.5px;
    margin-bottom: 0.3rem;
}
.sub-head { font-size: 0.92rem; color: #888; margin-bottom: 2rem; line-height: 1.5; }

/* ── PROMPT TEXTAREA ── */
.stTextArea textarea {
    background: #080808 !important;
    border: 1px solid #181818 !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
    font-size: 0.92rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 18px 20px !important;
    line-height: 1.65 !important;
    resize: none !important;
    min-height: 220px !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea::placeholder { color: #9ca3af !important; opacity: 1 !important; }
.stTextArea textarea:focus {
    border-color: #6366f140 !important;
    box-shadow: 0 0 0 3px #6366f10c !important;
}
div[data-testid="stTextArea"] > div { border: none !important; background: transparent !important; }

/* ── BUTTONS ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    height: 46px !important;
    border-radius: 10px !important;
    border: none !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"] {
    background: #6366f1 !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: #7577f3 !important;
    box-shadow: 0 4px 20px #6366f130 !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: #0e0e0e !important;
    color: #ccc !important;
    border: 1px solid #1a1a1a !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #141414 !important;
    border-color: #252525 !important;
    color: #eee !important;
}
.stButton > button:disabled {
    background: #0a0a0a !important;
    color: #222 !important;
    border: 1px solid #111 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── CODE BLOCK ── */
.code-wrap { border-radius: 12px; overflow: hidden; border: 1px solid #141414; margin-top: 20px; }
.code-bar {
    background: #0a0a0a;
    border-bottom: 1px solid #141414;
    padding: 10px 16px;
    display: flex; align-items: center; justify-content: space-between;
}
.code-dots { display: flex; gap: 7px; align-items: center; }
.dot-r { width: 11px; height: 11px; border-radius: 50%; background: #ff5f57; }
.dot-y { width: 11px; height: 11px; border-radius: 50%; background: #febc2e; }
.dot-g { width: 11px; height: 11px; border-radius: 50%; background: #28c840; }
.code-meta { display: flex; align-items: center; gap: 10px; }
.dialect-badge {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    color: #6366f1; background: #6366f112; border: 1px solid #6366f122;
    padding: 2px 9px; border-radius: 4px; letter-spacing: 0.5px; text-transform: uppercase;
}
.filename { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #555; }

[data-testid="stCode"] {
    border-radius: 0 !important; border: none !important; margin: 0 !important;
}
[data-testid="stCode"] pre {
    background: #080808 !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.81rem !important;
    line-height: 1.75 !important;
    padding: 22px !important;
    margin: 0 !important;
}

/* ── ANALYST CARD ── */
.analyst-locked {
    background: #080808;
    border: 1px solid #141414;
    border-left: 2px solid #6366f1;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 24px;
}
.analyst-locked-title { font-size: 0.72rem; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: #6366f1; margin-bottom: 6px; }
.analyst-locked-body  { font-size: 0.85rem; color: #777; line-height: 1.6; }

/* ── CHAT ── */
[data-testid="stChatMessage"] {
    background: #080808 !important;
    border: 1px solid #141414 !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
}
[data-testid="stChatInputTextArea"] {
    background: #080808 !important;
    border: 1px solid #181818 !important;
    color: #d1d1d1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.86rem !important;
    border-radius: 10px !important;
}

/* ── ALERTS ── */
.stAlert, [data-testid="stAlert"] {
    background: #080808 !important;
    border: 1px solid #181818 !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] p { color: #555 !important; font-size: 0.84rem !important; }
.stSpinner > div { border-top-color: #6366f1 !important; }

/* ── DIVIDERS ── */
hr { border-color: #111 !important; margin: 16px 0 !important; }

/* ── CAPTION / SMALL TEXT ── */
.stCaptionContainer p { color: #666 !important; font-size: 0.78rem !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for k, v in {
    "generated_sql": "",
    "db_connected":  False,
    "chat_messages": [],
    "history":       [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

DIALECTS = {
    "PostgreSQL": "postgresql",
    "MySQL":      "mysql",
    "SQLite":     "sqlite",
    "SQL Server": "mssql",
    "Oracle":     "oracle",
    "MariaDB":    "mariadb",
}

# ════════════════════════════════
# SIDEBAR
# ════════════════════════════════
with st.sidebar:
    st.markdown('<div class="brand">◈ AutoDB</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Main Console</div>', unsafe_allow_html=True)
    menu = st.radio("nav", ["DB Architect", "DB Analyst"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Environment</div>', unsafe_allow_html=True)

    live_mode = st.toggle("Live Mode", value=False)

    if live_mode:
        dialect_name = st.selectbox("Dialect", list(DIALECTS.keys()), label_visibility="collapsed")
        dialect = DIALECTS[dialect_name]
        db_url = st.text_input(
            "Connection String", type="password",
            placeholder="postgresql://user:password@localhost/db",
            label_visibility="collapsed"
        )
        st.session_state.db_connected = bool(db_url.strip())
        if st.session_state.db_connected:
            st.success("Ready to connect")
    else:
        dialect_name = st.selectbox("Dialect", list(DIALECTS.keys()), label_visibility="collapsed")
        dialect = DIALECTS[dialect_name]
        st.caption("Sandbox — generates SQL preview only")
        st.session_state.db_connected = False

    # History
    if st.session_state.history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sidebar-label">History</div>', unsafe_allow_html=True)
        for i, item in enumerate(reversed(st.session_state.history[-6:])):
            lbl = item["prompt"][:32] + "…" if len(item["prompt"]) > 32 else item["prompt"]
            if st.button(f"↩  {lbl}", key=f"h{i}", use_container_width=True, type="secondary"):
                st.session_state.generated_sql = item["sql"]

# ════════════════════════════════
# DB ARCHITECT
# ════════════════════════════════
if menu == "DB Architect":
    st.markdown('<div class="section-head">DB Architect</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-head">Map out your database structure using plain English. Describe tables, fields, and how they connect.</div>',
        unsafe_allow_html=True
    )

    prompt = st.text_area(
        "prompt",
        placeholder="Start building your schema...\ne.g. 'Create a multi-vendor marketplace. I need users, products with categories, and an orders table with status tracking.'",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1], gap="small")

    with c1:
        gen_click = st.button("⚡  Generate SQL", type="primary", use_container_width=True)
    with c2:
        push_ready = live_mode and st.session_state.db_connected
        push_click = st.button(
            "🗄  Push to DB", type="secondary",
            disabled=not push_ready, use_container_width=True
        )
    with c3:
        if st.button("✕  Clear", type="secondary", use_container_width=True):
            st.session_state.generated_sql = ""
            st.rerun()

    # Generate
    if gen_click:
        if not prompt.strip():
            st.warning("Describe your schema first.")
        else:
            with st.spinner("Architect at work..."):
                try:
                    raw  = generate_sql_func(prompt)
                    sql  = "\n\n".join(build_sql(raw, dialect))
                    st.session_state.generated_sql = sql
                    st.session_state.history.append({"prompt": prompt, "sql": sql, "dialect": dialect})
                except Exception as e:
                    st.error(f"Generation failed: {e}")

    if push_click and push_ready:
        st.info("Push to DB — wire core/engine.py in next build.")

    # SQL Output
    if st.session_state.generated_sql:
        n = st.session_state.generated_sql.count("CREATE TABLE")
        st.markdown(f"""
        <div class="code-wrap">
            <div class="code-bar">
                <div class="code-dots">
                    <div class="dot-r"></div>
                    <div class="dot-y"></div>
                    <div class="dot-g"></div>
                </div>
                <div class="code-meta">
                    <span class="dialect-badge">{dialect}</span>
                    <span class="filename">schema.sql · {n} table{"s" if n != 1 else ""}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.code(st.session_state.generated_sql, language="sql")

# ════════════════════════════════
# DB ANALYST
# ════════════════════════════════
elif menu == "DB Analyst":
    st.markdown('<div class="section-head">DB Analyst</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-head">Query your database in plain English. No SQL knowledge required.</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.db_connected:
        st.markdown("""
        <div class="analyst-locked">
            <div class="analyst-locked-title">Connection Required</div>
            <div class="analyst-locked-body">
                Switch to Live Mode in the sidebar and provide a database connection string to unlock the Analyst.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Chat messages
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_msg = st.chat_input("Ask your data... e.g. 'Show top 5 customers by revenue this month'")
        if user_msg:
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": "Analyst agent coming in next build — wire core/chat.py here."
            })
            st.rerun()
