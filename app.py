import streamlit as st
from core.architect import build_sql
from my_utils.llm_handler import generate_sql_func
st.title("💬AutoDb !!!")

st.write(
    "Thus us a simple tool that converts natural language to sql queries"
)

user_input = st.text_input("enter your requirements here (be as explicit as posssible)..")
dialect = st.text_input("enter sql dialect , e.g mysql, postgres")
sql_query = generate_sql_func(user_input)
test = build_sql(sql_query, dialect)
if st.button("generate sql"):
    st.write(test)
