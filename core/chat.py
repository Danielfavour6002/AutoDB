from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine

def get_analyst_agent(engine):
    db  = SQLDatabase(engine)
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0)
    return create_sql_agent(llm, db=db, verbose=False)

def query_agent(agent, question: str) -> str:
    return agent.invoke(question)["output"]

# engine = create_engine('sqlite:///school.db')

# agent = get_analyst_agent(engine)
# response = query(agent, "how many students are in the databse")
# print(response)