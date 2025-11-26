from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from openai import OpenAI
from app.services.rag_engine import RAGEngine
from app.services.metadata import MetadataService
import json
import sqlparse


class SQLAgent:
    """
    RAG/CAG-Enhanced SQL Generation Agent
    Uses semantic context to generate better SQL queries
    """
    
    def __init__(self, connection_string: str, llm_config: Dict[str, str], rag_context: Dict[str, Any]):
        self.connection_string = connection_string
        self.engine = create_engine(connection_string)
        self.llm_config = llm_config
        self.rag_context = rag_context
        
        # Initialize OpenAI client
        if llm_config["provider"] == "openai":
            self.client = OpenAI(api_key=llm_config["api_key"])
            self.model = llm_config["model_name"]
        else:
            raise ValueError(f"Provider {llm_config['provider']} not yet supported in agent")
    
    def generate_sql(self, user_query: str) -> Dict[str, Any]:
        """
        Generate SQL query from natural language using RAG/CAG context
        
        Args:
            user_query: User's natural language question
            
        Returns:
            Dictionary with SQL query and explanation
        """
        # Build enhanced system prompt with semantic context
        system_prompt = self._build_system_prompt()
        
        # Create user prompt
        user_prompt = f"""Generate a SQL query to answer this question: {user_query}

Return a JSON object with:
{{
    "sql": "the SQL query",
    "explanation": "brief explanation of what the query does",
    "tables_used": ["list", "of", "tables"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Format SQL
            if result.get("sql"):
                result["sql"] = sqlparse.format(
                    result["sql"],
                    reindent=True,
                    keyword_case='upper'
                )
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to generate SQL: {str(e)}")
    
    def execute_query(self, sql: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Dictionary with results and metadata
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                
                # Get column names
                columns = list(result.keys())
                
                # Fetch rows
                rows = []
                for row in result:
                    rows.append(dict(zip(columns, row)))
                
                return {
                    "success": True,
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "columns": [],
                "rows": [],
                "row_count": 0
            }
    
    def chat(self, user_query: str, execute: bool = True) -> Dict[str, Any]:
        """
        Process user query end-to-end: generate SQL and optionally execute
        
        Args:
            user_query: User's natural language question
            execute: Whether to execute the generated SQL
            
        Returns:
            Dictionary with SQL, explanation, and results
        """
        # Generate SQL
        sql_result = self.generate_sql(user_query)
        
        response = {
            "user_query": user_query,
            "sql": sql_result.get("sql"),
            "explanation": sql_result.get("explanation"),
            "tables_used": sql_result.get("tables_used", [])
        }
        
        # Execute if requested
        if execute and sql_result.get("sql"):
            execution_result = self.execute_query(sql_result["sql"])
            response["execution"] = execution_result
        
        return response
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with RAG/CAG context"""
        
        prompt_parts = [
            "You are an expert SQL analyst with deep knowledge of this database.",
            "Generate accurate, efficient SQL queries based on user questions.",
            "Use the semantic context provided to understand business terminology."
        ]
        
        # Add connection info
        if self.rag_context.get("connection_name"):
            prompt_parts.append(f"\n## Database: {self.rag_context['connection_name']}")
        
        # Add table context
        if self.rag_context.get("tables"):
            prompt_parts.append("\n## Available Tables and Business Context:")
            
            for table_name, table_ctx in self.rag_context["tables"].items():
                prompt_parts.append(f"\n### Table: {table_name}")
                
                if table_ctx.get("business_description"):
                    prompt_parts.append(f"Purpose: {table_ctx['business_description']}")
                
                if table_ctx.get("column_descriptions"):
                    prompt_parts.append("Columns:")
                    for col, desc in table_ctx["column_descriptions"].items():
                        prompt_parts.append(f"  - {col}: {desc}")
                
                if table_ctx.get("relationships"):
                    prompt_parts.append("Relationships:")
                    for rel in table_ctx["relationships"]:
                        prompt_parts.append(f"  - {rel}")
        
        # Add business glossary
        all_glossary = {}
        for table_ctx in self.rag_context.get("tables", {}).values():
            if table_ctx.get("business_glossary"):
                all_glossary.update(table_ctx["business_glossary"])
        
        if all_glossary:
            prompt_parts.append("\n## Business Glossary:")
            for term, definition in all_glossary.items():
                prompt_parts.append(f"  - {term}: {definition}")
        
        # Add example queries
        all_examples = []
        for table_ctx in self.rag_context.get("tables", {}).values():
            if table_ctx.get("example_queries"):
                all_examples.extend(table_ctx["example_queries"])
        
        if all_examples:
            prompt_parts.append("\n## Example Query Patterns:")
            for example in all_examples[:3]:
                prompt_parts.append(f"  - {example}")
        
        prompt_parts.append("\n## Instructions:")
        prompt_parts.append("- Use the business context to understand user intent")
        prompt_parts.append("- Reference the glossary for domain-specific terms")
        prompt_parts.append("- Generate clean, readable SQL")
        prompt_parts.append("- Always return valid JSON with sql, explanation, and tables_used fields")
        
        return "\n".join(prompt_parts)
