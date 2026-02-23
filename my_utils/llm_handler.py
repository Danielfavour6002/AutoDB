from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from my_utils.validator import TableSchema
import os
from dotenv import load_dotenv
load_dotenv()
import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def generate_sql():
    llm = ChatOpenAI(api_key=os.getenv("API_KEY"), temperature=0.0)
    parser = JsonOutputParser(pydantic_object=TableSchema)
    format_instructions = parser.get_format_instructions()

    system_message = """
    You are a senior database archutect. When a user provides a prompt analyse,
    you must provide the sql query only, using this schema {TableSchema}.Always return json using that format

    {format_instructions}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", "{user_question}")
    ])

    # Inject format instructions properly
    prompt = prompt.partial(format_instructions=format_instructions)

    chain = prompt | llm | parser
    return chain


def generate_sql_func(message: str, table_schema):
    chain = generate_sql()
    response = chain.invoke({"user_question": message, "TableSchema" : table_schema})
    return response
