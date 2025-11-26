from typing import Dict, Any, List
import sqlparse
from sqlalchemy import create_engine, text
from app.core.logging import get_logger
from app.models.models import DatabaseConnection

logger = get_logger(__name__)

class SQLEngine:
    """Execute SQL queries safely with validation"""
    
    def __init__(self):
        self.max_rows = 1000
    
    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """Validate SQL query (only SELECT allowed)"""
        try:
            # Parse SQL
            parsed = sqlparse.parse(sql)
            
            if not parsed:
                return {"valid": False, "error": "Empty SQL query"}
            
            # Get first statement
            statement = parsed[0]
            
            # Check if it's a SELECT statement
            first_token = statement.token_first(skip_ws=True, skip_cm=True)
            if not first_token or first_token.ttype is not sqlparse.tokens.Keyword.DML:
                return {"valid": False, "error": "Invalid SQL statement"}
            
            if first_token.value.upper() != "SELECT":
                return {"valid": False, "error": "Only SELECT queries are allowed"}
            
            # Check for dangerous keywords
            dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
            sql_upper = sql.upper()
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return {"valid": False, "error": f"Dangerous keyword '{keyword}' not allowed"}
            
            return {"valid": True}
        
        except Exception as e:
            logger.error(f"SQL validation error: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    def execute_sql(
        self,
        sql: str,
        connection: DatabaseConnection
    ) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        
        # Validate first
        validation = self.validate_sql(sql)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "columns": [],
                "rows": []
            }
        
        try:
            # Create engine for this connection
            engine = create_engine(connection.connection_string)
            
            # Add LIMIT if not present
            sql_upper = sql.upper()
            if "LIMIT" not in sql_upper:
                sql = f"{sql} LIMIT {self.max_rows}"
            
            # Execute query
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                
                # Get column names
                columns = list(result.keys())
                
                # Fetch rows
                rows = []
                for row in result:
                    rows.append(dict(zip(columns, row)))
                
                logger.info(f"SQL executed successfully: {len(rows)} rows returned")
                
                return {
                    "success": True,
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }
        
        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "columns": [],
                "rows": []
            }
    
    def format_results_for_display(self, results: Dict[str, Any]) -> str:
        """Format SQL results as a readable string"""
        if not results["success"]:
            return f"Error: {results['error']}"
        
        if results["row_count"] == 0:
            return "Query executed successfully. No rows returned."
        
        return f"Query returned {results['row_count']} rows with columns: {', '.join(results['columns'])}"
