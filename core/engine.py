from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy import inspect


def get_engine(db_url: str):
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except OperationalError as e:
        raise ConnectionError(f"Could not connect to database: {e.orig}")
    except Exception as e:
        raise ConnectionError(f"Invalid connection string or unreachable host: {e}")


def execute_sql(engine, statements: list[str]):
    """
    Execute a list of SQL statements. Each item is executed as its own
    statement — no semicolon splitting needed, avoids syntax errors.
    """
    try:
        with engine.connect() as conn:
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
    except SQLAlchemyError as e:
        raise RuntimeError(f"SQL execution failed: {e}")



def database_context(engine) -> list[str]:
    inspector = inspect(engine)
    try:
        table_names = inspector.get_table_names()
        print("Tables:", table_names)
        #return table names
        for table_name in table_names:
            print(f"\n--- Columns for table '{table_name}': ---")
            #return column details for each table
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f"  Column: {column['name']}, Type: {column['type']}, Nullable: {column['nullable']}")
            #return primary key constraints
            pk_constraints = inspector.get_pk_constraint(table_name)
            print(f"\n--- Primary Key for table '{table_name}': ---")
            print(f"  Columns: {pk_constraints['constrained_columns']}")
            #return forein key constraints
            foreign_keys = inspector.get_foreign_keys(table_name)
            print(f"\n--- Foreign Keys for table '{table_name}': ---")
            for fk in foreign_keys:
                print(f"  Constrained columns: {fk['constrained_columns']} -> Referred table: {fk['referred_table']} (Referred columns: {fk['referred_columns']})")
    except Exception as e:
        print(f"an error occured: {e}")
