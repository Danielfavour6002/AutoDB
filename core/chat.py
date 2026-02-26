import os
import re
import warnings
from typing import Tuple, Optional

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Static fallback list — used if API fetch fails
_FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "qwen/qwen-3-32b",
    "gemma2-9b-it",
    "llama3-70b-8192",
]

# Prefer these model families for SQL tasks (ranked by quality/speed)
_PREFERRED_PREFIXES = [
    "llama-3.3", "llama-3.1", "llama-4",
    "qwen", "gemma", "llama3",
]

_MODELS_CACHE: list = []


def _get_models() -> list:
    """
    Fetch active models from Groq API at runtime.
    Falls back to static list if fetch fails.
    Cached after first call.
    """
    global _MODELS_CACHE
    if _MODELS_CACHE:
        return _MODELS_CACHE

    try:
        import requests
        resp = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json",
            },
            timeout=5,
        )
        if resp.status_code == 200:
            all_models = [
                m["id"] for m in resp.json().get("data", [])
                # Only text chat models — skip whisper, tts, guard, image
                if not any(x in m["id"].lower() for x in [
                    "whisper", "tts", "guard", "safeguard", "image", "vision"
                ])
            ]
            # Sort by preferred prefix order
            def rank(m):
                for i, prefix in enumerate(_PREFERRED_PREFIXES):
                    if m.lower().startswith(prefix):
                        return i
                return len(_PREFERRED_PREFIXES)

            _MODELS_CACHE = sorted(all_models, key=rank)
            return _MODELS_CACHE
    except Exception:
        pass

    _MODELS_CACHE = _FALLBACK_MODELS
    return _MODELS_CACHE

# ── One-time cache per engine ──────────────────────────────────────
# Schema is reflected ONCE on first query, stored in memory.
# Every subsequent query reads from cache — zero DB round trips.
_SCHEMA_CACHE: dict = {}   # engine id → full schema string
_TABLES_CACHE: dict = {}   # engine id → list of table names
_DB_CACHE: dict     = {}   # engine id → SQLDatabase (for db.run())

DESCRIBE_PATTERNS = re.compile(
    r"\b(describe|overview|summarize|summarise|what tables|list tables|"
    r"what('s| is) in (the |this )?db|database structure|schema|"
    r"what (does|do) (the |this )?db|tell me about (the |this )?db|"
    r"what (can|should) i ask|what data)\b",
    re.IGNORECASE
)


def _is_rate_limit(err: str) -> bool:
    return any(x in err.lower() for x in [
        "rate_limit_exceeded", "429",
        "decommissioned", "no longer supported", "rate limit",
    ])


def _clean_sql(text: str) -> str:
    text = re.sub(r"```sql|```", "", text, flags=re.IGNORECASE)
    text = re.sub(r"SQLQuery\s*:\s*", "", text, flags=re.IGNORECASE)
    for keyword in ("SELECT", "INSERT", "UPDATE", "DELETE", "WITH"):
        if keyword in text.upper():
            text = text[text.upper().find(keyword):]
            break
    text = text.split(";")[0]
    return text.strip()


def _warm_cache(engine):
    """
    Reflect schema once and store everything in memory.
    Called on first query — subsequent calls return instantly.
    """
    eid = id(engine)
    if eid in _SCHEMA_CACHE:
        return

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        db = SQLDatabase(engine, sample_rows_in_table_info=0)
        _DB_CACHE[eid]     = db
        _TABLES_CACHE[eid] = db.get_usable_table_names()
        _SCHEMA_CACHE[eid] = db.get_table_info()   # full schema: tables + columns + types


def _execute_with_fix(engine, sql, llm, max_retries=2) -> str:
    db = _DB_CACHE[id(engine)]
    FIX = ChatPromptTemplate.from_template(
        "This SQL failed:\n{sql}\n\nError:\n{error}\n\n"
        "Available tables (use EXACT names, always double-quoted): {tables}\n\n"
        "Fix the SQL. Rules:\n"
        "- Wrap every table name and column name in double quotes\n"
        "- Use only exact table/column names from the schema\n"
        "- PostgreSQL is case-sensitive — double quotes are required\n"
        "Return ONLY the corrected SQL — no explanation, no markdown, no semicolons."
    )
    for attempt in range(max_retries + 1):
        try:
            return db.run(sql)
        except Exception as e:
            err = str(e)
            if attempt < max_retries:
                tables = ", ".join(_TABLES_CACHE[id(engine)])
                fixed = (FIX | llm | StrOutputParser()).invoke({"sql": sql, "error": err, "tables": tables})
                sql   = _clean_sql(fixed)
            else:
                raise Exception(err)


# ── Prompts ────────────────────────────────────────────────────────

DESCRIBE_PROMPT = ChatPromptTemplate.from_template("""You are a sharp data analyst explaining a database to a colleague.

- Group related tables naturally, explain what they do
- Mention obvious relationships
- Conversational tone — not documentation
- Don't list every column

Tables: {tables}
Question: {question}

Answer:""")

SQL_PROMPT = ChatPromptTemplate.from_template("""You are a SQL expert. Write a single SQL query to answer the question.

STRICT RULES:
- Use ONLY the exact table names from "Available tables" — do not shorten, rename, or guess
- Always wrap table names AND column names in double quotes e.g. "Bookings_booking", "Users_user"
- This is critical for PostgreSQL where identifiers are case-sensitive
- Use ONLY columns that exist in the schema — do not invent column names
- Return ONLY the raw SQL — no explanation, no markdown, no semicolons

Available tables (use these EXACT names, always double-quoted):
{tables}

Schema:
{schema}

Question: {question}

SQL:""")

ANSWER_PROMPT = ChatPromptTemplate.from_template("""You are a sharp, direct data analyst. Talk like a real person.

- Get straight to the point
- Use actual numbers and names from the results
- Flag anything interesting naturally  
- If empty: "Nothing came back for that"
- Short sentences. No "Based on the data..." filler
- Never mention SQL or tables

Question: {question}
Data: {results}

Answer:""")


def query_agent(engine, question: str) -> Tuple[str, Optional[str]]:
    # Warm cache on first call — one-time cost
    _warm_cache(engine)

    last_error = ""

    for model in _get_models():
        try:
            llm = ChatGroq(
                model=model,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.3,
            )

            # Describe intent — answer from schema, no SQL
            if DESCRIBE_PATTERNS.search(question):
                chain  = DESCRIBE_PROMPT | llm | StrOutputParser()
                answer = chain.invoke({
                    "tables":   ", ".join(_TABLES_CACHE[id(engine)]),
                    "question": question,
                })
                return answer.strip(), model

            # Full schema from cache — no DB calls, no filtering that drops tables
            schema = _SCHEMA_CACHE[id(engine)]

            # Step 1: Generate SQL — custom prompt, no LangChain internals
            # create_sql_query_chain avoided: it runs UNION ALL MAX(id) across all
            # tables before every query which hallucnates tables and wastes tokens
            raw_sql = (SQL_PROMPT | llm | StrOutputParser()).invoke({
                "tables":   ", ".join(_TABLES_CACHE[id(engine)]),
                "schema":   schema,
                "question": question,
            })
            clean_sql = _clean_sql(raw_sql)

            if not clean_sql:
                return "Couldn't figure out what to query — try rephrasing?", model

            # Step 2: Execute with auto-fix
            db_result = _execute_with_fix(engine, clean_sql, llm)

            # Step 3: Human answer
            answer = (ANSWER_PROMPT | llm | StrOutputParser()).invoke({
                "question": question,
                "results":  db_result,
            })
            return answer.strip(), model

        except Exception as e:
            err = str(e)
            if _is_rate_limit(err):
                last_error = err
                continue
            return f"Error: {err}", model

    retry_match = re.search(r"Please try again in (\d+m[\d.]+s|\d+s)", last_error)
    retry_str   = retry_match.group(1) if retry_match else "a few minutes"
    return f"All models are rate-limited right now. Try again in {retry_str}.", None


def invalidate_cache(engine):
    eid = id(engine)
    _SCHEMA_CACHE.pop(eid, None)
    _TABLES_CACHE.pop(eid, None)
    _DB_CACHE.pop(eid, None)