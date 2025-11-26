from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger
from sqlalchemy.orm import Session
from app.models.models import SemanticModel, ChatMessage as ChatMessageModel

logger = get_logger(__name__)

class LLMOrchestrator:
    """Orchestrates LLM calls for SQL generation and analysis"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    def generate_sql(
        self,
        user_question: str,
        connection_id: int,
        session_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Generate SQL from natural language question"""
        
        if not self.client:
            return {
                "sql": "-- OpenAI API key not configured",
                "explanation": "Please add your OpenAI API key to enable SQL generation",
                "trace": [{"step": "error", "message": "No API key configured"}]
            }
        
        try:
            # Get schema context
            schema_context = self._get_schema_context(connection_id, db)
            
            # Get conversation history
            history = self._get_conversation_history(session_id, db)
            
            # Build prompt
            prompt = self._build_sql_prompt(user_question, schema_context, history)
            
            # Call OpenAI
            trace = []
            trace.append({"step": "schema_retrieval", "tables_found": len(schema_context)})
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate SQL queries based on the schema and user questions. Return only the SQL query without explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql = response.choices[0].message.content.strip()
            
            # Clean SQL (remove markdown code blocks if present)
            if sql.startswith("```sql"):
                sql = sql.replace("```sql", "").replace("```", "").strip()
            elif sql.startswith("```"):
                sql = sql.replace("```", "").strip()
            
            trace.append({"step": "sql_generation", "model": "gpt-4", "tokens": response.usage.total_tokens})
            
            return {
                "sql": sql,
                "explanation": f"Generated SQL query for: {user_question}",
                "trace": trace
            }
        
        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            return {
                "sql": f"-- Error: {str(e)}",
                "explanation": f"Failed to generate SQL: {str(e)}",
                "trace": [{"step": "error", "message": str(e)}]
            }
    
    def _get_schema_context(self, connection_id: int, db: Session) -> List[Dict[str, Any]]:
        """Get relevant schema information for the connection"""
        semantic_models = db.query(SemanticModel).filter(
            SemanticModel.connection_id == connection_id
        ).all()
        
        schema = []
        for sm in semantic_models:
            schema.append({
                "table_name": sm.table_name,
                "description": sm.business_description,
                "columns": sm.column_descriptions or {}
            })
        
        return schema
    
    def _get_conversation_history(self, session_id: int, db: Session) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.session_id == session_id
        ).order_by(ChatMessageModel.created_at.desc()).limit(5).all()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
    
    def _build_sql_prompt(
        self,
        question: str,
        schema: List[Dict[str, Any]],
        history: List[Dict[str, str]]
    ) -> str:
        """Build the prompt for SQL generation"""
        
        schema_text = "Available tables:\n"
        for table in schema:
            schema_text += f"\nTable: {table['table_name']}\n"
            schema_text += f"Description: {table['description']}\n"
            schema_text += "Columns:\n"
            for col, dtype in table['columns'].items():
                schema_text += f"  - {col} ({dtype})\n"
        
        prompt = f"""{schema_text}

User question: {question}

Generate a SQL query to answer this question. Return ONLY the SQL query, no explanations."""
        
        return prompt
    
    def suggest_chart_type(self, columns: List[str], row_count: int) -> Dict[str, Any]:
        """Suggest appropriate chart type based on data"""
        
        if row_count == 0:
            return {"type": "table", "reason": "No data to visualize"}
        
        if len(columns) == 1:
            return {"type": "table", "reason": "Single column data"}
        
        if len(columns) == 2:
            # Check if one column looks like a category and one like a number
            return {
                "type": "bar",
                "x_axis": columns[0],
                "y_axis": columns[1],
                "reason": "Two columns - category and value"
            }
        
        if len(columns) >= 3:
            return {
                "type": "line",
                "x_axis": columns[0],
                "y_axis": columns[1],
                "series": columns[2] if len(columns) > 2 else None,
                "reason": "Multiple columns - time series or grouped data"
            }
        
        return {"type": "table", "reason": "Default to table view"}
