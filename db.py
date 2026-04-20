import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from langchain_core.tools import tool
from datetime import datetime

load_dotenv()

def connect_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@tool
def query_database(query: str):
    """Run a SELECT query on the database and return results."""
    if not query.upper().startswith("SELECT"):
        return [{"error": "Only SELECT queries are allowed."}]
    
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        
        # Convert datetime
        result = []
        for row in data:
            row_dict = dict(row)
            for key, val in row_dict.items():
                if isinstance(val, datetime):
                    row_dict[key] = val.isoformat()
            result.append(row_dict)
        return result
    except Exception as e:
        return [{"error": str(e)}]

@tool
def list_tables():
    """Return names of all tables in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

@tool
def describe_table(table_name: str) :
    """Return column details for a table."""
    conn = connect_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = %s",
        (table_name.lower(),)
    )
    columns = cursor.fetchall()
    conn.close()
    return [dict(col) for col in columns]