import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import json

from dotenv import load_dotenv
load_dotenv()


def generate_sql_func(user_prompt:str):
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)
    template = """
    You are a database architect. Respond ONLY with valid JSON, no explanation, no markdown.

    ALWAYS follow this EXACT format:
    {{
        "tables": [
            {{
                "name": "table_name",
                "columns": [
                    {{
                        "name": "id",
                        "type": "int",
                        "primary_key": true,
                        "nullable": false,
                        "unique": false,
                        "default": null,
                        "foreign_key": null
                    }},
                    {{
                        "name": "user_id",
                        "type": "int",
                        "primary_key": false,
                        "nullable": true,
                        "unique": false,
                        "default": null,
                        "foreign_key": {{"table": "users", "column": "id"}}
                    }}
                ]
            }}
        ]
    }}

    RULES:
    - foreign_key must ALWAYS be {{"table": "...", "column": "..."}} or null, never a string
    - type must be one of: int, varchar(n), text, decimal(n,n), timestamp, boolean
    - always include all fields for every column even if null or false

    User request: {question}
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]
    )
    chain = prompt | llm
    response = chain.invoke({
        "question" : user_prompt,
    })
    text = response.content.strip()
    return json.loads(text)

