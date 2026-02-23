import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from  langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from my_utils.validator import DatabaseSchema
import json
import pprint
from dotenv import load_dotenv
load_dotenv()



llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

def generate_sql_func(database_schema):
    template = """
    You are a database architect. The user will describe a database table they want.
    Respond ONLY with a valid JSON object in this exact format, nothing else.use the format {table_schema}:
    User request: {question}
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["question", "table_schema"]
    )
    parser = JsonOutputParser(pydantic_object=database_schema)
    chain = prompt | llm | parser
  
    return chain

def generate_sql(prompt : str, database_schema):
    chain = generate_sql_func(database_schema)
    response = chain.invoke({
        "question" : prompt,
        "table_schema" : database_schema
    })
    
    return response

pprint.pprint(generate_sql("create tables for ecommerce website", database_schema=DatabaseSchema))