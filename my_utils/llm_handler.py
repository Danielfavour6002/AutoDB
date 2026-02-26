import os
import re
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
    "llama3-70b-8192",
]

SYSTEM_PROMPT = """You are a database schema expert. Convert natural language descriptions into structured JSON representing a relational database schema.

Return ONLY valid JSON matching this exact structure — no explanation, no markdown, no extra text:
{
  "tables": [
    {
      "name": "table_name",
      "columns": [
        {
          "name": "column_name",
          "type": "INTEGER | VARCHAR(255) | TEXT | BOOLEAN | TIMESTAMP | DECIMAL(10,2)",
          "primary_key": true | false,
          "nullable": true | false,
          "unique": true | false,
          "foreign_key": {"table": "other_table", "column": "id"} | null
        }
      ]
    }
  ]
}

Rules:
- Every table must have an 'id' INTEGER primary_key column
- Use snake_case for all names
- Foreign key columns must be named <table>_id
- foreign_key field must reference a table that exists in the schema
- nullable is false for primary keys, true for optional fields
"""


def _is_rate_limit(err: str) -> bool:
    return any(x in str(err) for x in [
        "rate_limit_exceeded", "429",
        "decommissioned", "no longer supported"
    ])


def _clean_json(raw: str) -> str:
    raw = re.sub(r"```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```", "", raw)
    return raw.strip()


def generate_sql_func(prompt: str) -> dict:
    """
    Architect: send natural language prompt, return parsed JSON schema dict.
    Uses LangChain ChatGroq with model fallback chain.
    """
    last_error = ""

    for model in MODELS:
        try:
            llm = ChatGroq(
                model=model,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0,
                max_tokens=2048,
            )

            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])

            clean = _clean_json(response.content)
            return json.loads(clean)

        except json.JSONDecodeError as e:
            raise ValueError(f"Model returned invalid JSON: {e}\n\nRaw:\n{response.content}")

        except Exception as e:
            err = str(e)
            if _is_rate_limit(err):
                last_error = err
                continue
            raise RuntimeError(f"LLM error: {err}")

    retry_match = re.search(r"Please try again in (\d+m[\d.]+s|\d+s)", last_error)
    retry_str   = retry_match.group(1) if retry_match else "a few minutes"
    raise RuntimeError(f"All models are rate-limited. Try again in {retry_str}.")