from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from  langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from my_utils.validator import TableSchema
import os
import json
from dotenv import load_dotenv
load_dotenv()



llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

def generate_sql_func(table_schema):
    template = """
    You are a database architect. The user will describe a database table they want.
    Respond ONLY with a valid JSON object in this exact format, nothing else.use the schema variable 
    {table_schema}:
    User request: {question}
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["question", "table_schema"]
    )
    parser = JsonOutputParser(pydantic_object=table_schema)
    chain = prompt | llm | parser
  
    return chain

def generate_sql(prompt : str, table_schema):
    chain = generate_sql_func(table_schema)
    response = chain.invoke({
        "question" : prompt,
        "table_schema" : table_schema
    })
    
    return response

print(generate_sql("create schema for table users", table_schema=TableSchema))