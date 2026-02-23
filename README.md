# 🏗️ AutoDB

**AutoDB** is an AI-powered database companion that bridges the gap between **natural language** and **database management**. Whether you are drafting a new schema from scratch or chatting with live data to uncover insights, AutoDB acts as your Senior DBA and Data Analyst in one interface.

---

## 🚀 Core Features

### 1. The Architect (Structure)
Design and modify your database using plain English. 
* **Intelligent Drafting:** Generates structured JSON schemas before converting them to dialect-specific SQL.
* **Reflective Context:** Scans your existing database to suggest `ALTER` commands instead of creating redundant tables.
* **Sandbox Mode:** No DB? No problem. Generate raw SQL scripts for any major dialect (Postgres, MySQL, SQLite) without a connection.

### 2. The Analyst (Query)
Stop writing complex `JOINs` and start asking questions.
* **NL-to-SQL:** Powered by a self-correcting LangChain SQL Agent.
* **Safety First:** Operates in a **read-only** mode for data querying, protected by a keyword-scanning validator.
* **Explainable AI:** The analyst explains its logic and the SQL it wrote before showing you the results.

---

## 📁 Project Structure

```text
/autodb
├── app.py                  # Streamlit UI & Multi-tab Navigation
├── core/
│   ├── engine.py           # DB Connection & SQLAlchemy Reflection
│   ├── architect.py        # Schema Generation Logic (Prompt -> JSON)
│   └── analyst.py          # SQL Agent Implementation (NL -> Query)
├── utils/
│   ├── validator.py        # Safety Guardrails & SQL Sanitization
│   └── prompts.py          # ChatPromptTemplates & System Prefixes
├── requirements.txt        # Dependencies (LangChain, SQLAlchemy, OpenAI)
└── .env                    # API Keys and Configuration
