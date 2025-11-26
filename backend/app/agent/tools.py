from langchain_core.tools import tool

@tool
def execute_sql(query: str):
    """Executes a SQL query against the connected database."""
    # Logic to execute SQL using ConnectionManager
    return "Result of SQL query"

@tool
def generate_visualization(data: dict):
    """Generates a visualization configuration for the frontend."""
    return {"type": "bar", "data": data}

def get_tools():
    return [execute_sql, generate_visualization]
