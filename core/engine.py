from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def get_engine(db_url: str):
    engine = create_engine(db_url)
    # Test the connection immediately
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return engine

def execute_sql(engine, sql: str):
    with engine.connect() as conn:
        for statement in sql.strip().split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()