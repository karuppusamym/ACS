from typing import Dict, Any, List, Optional
from openai import OpenAI
import json


class ContextGenerator:
    """Service for generating semantic context using LLM (RAG/CAG)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    async def generate_table_context(self, table_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate business context for a table using LLM analysis
        
        Args:
            table_metadata: Dictionary containing table name, columns, constraints, etc.
            
        Returns:
            Dictionary with generated context including:
            - business_description
            - column_descriptions
            - suggested_relationships
            - example_queries
        """
        prompt = self._build_table_analysis_prompt(table_metadata)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analyst expert who understands database schemas and can infer business meaning from table structures. Provide detailed, business-friendly descriptions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            raise Exception(f"Failed to generate context: {str(e)}")
    
    async def suggest_column_descriptions(self, columns: List[Dict[str, Any]], table_context: str = "") -> Dict[str, str]:
        """
        Generate business-friendly descriptions for columns
        
        Args:
            columns: List of column metadata (name, type, nullable, etc.)
            table_context: Optional context about the table
            
        Returns:
            Dictionary mapping column names to descriptions
        """
        prompt = f"""Analyze these database columns and provide business-friendly descriptions for each.

Table Context: {table_context if table_context else "Not provided"}

Columns:
{json.dumps(columns, indent=2)}

Provide a JSON object with column names as keys and business descriptions as values.
Focus on what the column represents in business terms, not just technical details.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analyst who translates technical database columns into business-friendly descriptions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("column_descriptions", result)
            
        except Exception as e:
            raise Exception(f"Failed to generate column descriptions: {str(e)}")
    
    async def generate_sample_queries(self, table_metadata: Dict[str, Any], business_context: str = "") -> List[str]:
        """
        Generate sample SQL queries for a table
        
        Args:
            table_metadata: Table structure information
            business_context: Business description of the table
            
        Returns:
            List of sample SQL queries
        """
        prompt = f"""Generate 5 useful SQL queries for this table that would help users understand and analyze the data.

Table: {table_metadata.get('name')}
Business Context: {business_context if business_context else "Not provided"}

Columns:
{json.dumps(table_metadata.get('columns', []), indent=2)}

Provide a JSON object with a "queries" array containing SQL query strings.
Make queries progressively more complex and useful for business analysis.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert who creates useful example queries for data analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("queries", [])
            
        except Exception as e:
            raise Exception(f"Failed to generate sample queries: {str(e)}")
    
    async def enrich_business_context(
        self, 
        table_name: str,
        existing_context: Dict[str, Any],
        table_metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate business glossary terms based on table and existing context
        
        Args:
            table_name: Name of the table
            existing_context: Existing business descriptions and context
            table_metadata: Technical table metadata
            
        Returns:
            Dictionary of business terms and their definitions
        """
        prompt = f"""Based on this table and its context, suggest business glossary terms that would help users understand the domain.

Table: {table_name}
Existing Context: {json.dumps(existing_context, indent=2)}
Table Structure: {json.dumps(table_metadata, indent=2)}

Provide a JSON object with business terms as keys and their definitions as values.
Focus on domain-specific terminology that would help users query this data.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business analyst who creates glossaries to help users understand data domains."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("glossary", result)
            
        except Exception as e:
            raise Exception(f"Failed to enrich business context: {str(e)}")
    
    async def generate_system_prompt(self, table_metadata: Dict[str, Any], business_context: Dict[str, Any]) -> str:
        """
        Generate a custom system prompt for the agent based on table metadata and business context
        
        Args:
            table_metadata: Technical table information
            business_context: Business descriptions and context
            
        Returns:
            System prompt string
        """
        prompt = f"""Create a system prompt for an AI agent that will help users query this database table.

Table Metadata:
{json.dumps(table_metadata, indent=2)}

Business Context:
{json.dumps(business_context, indent=2)}

The system prompt should:
1. Explain what data is available
2. Include business terminology
3. Guide the agent on how to interpret user questions
4. Mention important constraints or relationships

Provide a JSON object with a "system_prompt" key containing the prompt text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating effective system prompts for AI agents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("system_prompt", "")
            
        except Exception as e:
            raise Exception(f"Failed to generate system prompt: {str(e)}")
    
    def _build_table_analysis_prompt(self, table_metadata: Dict[str, Any]) -> str:
        """Build prompt for comprehensive table analysis"""
        return f"""Analyze this database table and provide comprehensive business context.

Table Name: {table_metadata.get('name')}
Columns: {json.dumps(table_metadata.get('columns', []), indent=2)}
Primary Key: {table_metadata.get('primary_key', [])}
Foreign Keys: {json.dumps(table_metadata.get('foreign_keys', []), indent=2)}
Indexes: {json.dumps(table_metadata.get('indexes', []), indent=2)}

Provide a JSON object with:
{{
    "business_description": "What this table represents in business terms",
    "column_descriptions": {{"column_name": "business meaning"}},
    "suggested_relationships": ["Description of how this table relates to others"],
    "example_queries": ["Sample SQL queries"],
    "business_glossary": {{"term": "definition"}}
}}

Be specific and business-focused. Infer the domain from table/column names.
"""
