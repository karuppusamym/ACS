from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.models import SemanticModel, DatabaseConnection, LLMConfiguration
from app.services.metadata import MetadataService
from app.core.encryption import encryption_service


class RAGEngine:
    """
    Retrieval Augmented Generation Engine
    Retrieves semantic context for enhancing agent prompts
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_connection_context(self, connection_id: int) -> Dict[str, Any]:
        """
        Get all semantic context for a database connection
        
        Args:
            connection_id: Database connection ID
            
        Returns:
            Dictionary containing all semantic models and their context
        """
        # Get connection
        connection = self.db.query(DatabaseConnection).filter(
            DatabaseConnection.id == connection_id
        ).first()
        
        if not connection:
            return {}
        
        # Get all semantic models for this connection
        models = self.db.query(SemanticModel).filter(
            SemanticModel.connection_id == connection_id
        ).all()
        
        # Build context dictionary
        context = {
            "connection_name": connection.name,
            "connection_type": connection.type,
            "tables": {}
        }
        
        for model in models:
            context["tables"][model.table_name] = {
                "business_description": model.business_description,
                "column_descriptions": model.column_descriptions or {},
                "relationships": model.relationships or [],
                "business_glossary": model.business_glossary or {},
                "example_queries": model.example_queries or [],
                "system_prompt": model.system_prompt,
                "user_prompt_template": model.user_prompt_template
            }
        
        return context
    
    def get_table_context(self, connection_id: int, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get semantic context for a specific table
        
        Args:
            connection_id: Database connection ID
            table_name: Name of the table
            
        Returns:
            Dictionary containing semantic model context
        """
        model = self.db.query(SemanticModel).filter(
            SemanticModel.connection_id == connection_id,
            SemanticModel.table_name == table_name
        ).first()
        
        if not model:
            return None
        
        return {
            "table_name": model.table_name,
            "business_description": model.business_description,
            "column_descriptions": model.column_descriptions or {},
            "relationships": model.relationships or [],
            "business_glossary": model.business_glossary or {},
            "example_queries": model.example_queries or [],
            "system_prompt": model.system_prompt,
            "user_prompt_template": model.user_prompt_template
        }
    
    def build_enhanced_system_prompt(self, connection_id: int, base_prompt: str = "") -> str:
        """
        Build an enhanced system prompt with semantic context
        
        Args:
            connection_id: Database connection ID
            base_prompt: Base system prompt to enhance
            
        Returns:
            Enhanced system prompt with business context
        """
        context = self.get_connection_context(connection_id)
        
        if not context.get("tables"):
            return base_prompt or "You are a helpful SQL assistant."
        
        # Start with base prompt
        prompt_parts = [base_prompt or "You are an expert SQL analyst with deep knowledge of this database."]
        
        # Add database context
        prompt_parts.append(f"\n\n## Database: {context['connection_name']} ({context['connection_type']})")
        
        # Add table descriptions
        prompt_parts.append("\n## Available Tables:")
        for table_name, table_ctx in context["tables"].items():
            prompt_parts.append(f"\n### {table_name}")
            if table_ctx.get("business_description"):
                prompt_parts.append(f"{table_ctx['business_description']}")
            
            # Add column descriptions
            if table_ctx.get("column_descriptions"):
                prompt_parts.append("\nColumns:")
                for col, desc in table_ctx["column_descriptions"].items():
                    prompt_parts.append(f"- {col}: {desc}")
        
        # Add business glossary
        all_glossary = {}
        for table_ctx in context["tables"].values():
            if table_ctx.get("business_glossary"):
                all_glossary.update(table_ctx["business_glossary"])
        
        if all_glossary:
            prompt_parts.append("\n## Business Glossary:")
            for term, definition in all_glossary.items():
                prompt_parts.append(f"- **{term}**: {definition}")
        
        # Add example queries
        all_examples = []
        for table_ctx in context["tables"].values():
            if table_ctx.get("example_queries"):
                all_examples.extend(table_ctx["example_queries"])
        
        if all_examples:
            prompt_parts.append("\n## Example Queries:")
            for example in all_examples[:5]:  # Limit to 5 examples
                prompt_parts.append(f"- {example}")
        
        prompt_parts.append("\n\nUse this context to help users query and understand their data.")
        
        return "\n".join(prompt_parts)
    
    def get_relevant_context(self, connection_id: int, user_query: str) -> Dict[str, Any]:
        """
        Get relevant semantic context based on user query
        
        Args:
            connection_id: Database connection ID
            user_query: User's natural language query
            
        Returns:
            Relevant context for the query
        """
        # For now, return all context
        # In future, could use embeddings to find most relevant tables
        return self.get_connection_context(connection_id)
    
    def get_active_llm_config(self) -> Optional[Dict[str, str]]:
        """
        Get the active LLM configuration
        
        Returns:
            Dictionary with provider, model, and decrypted API key
        """
        config = self.db.query(LLMConfiguration).filter(
            LLMConfiguration.is_active == True
        ).first()
        
        if not config:
            return None
        
        try:
            api_key = encryption_service.decrypt(config.api_key)
            return {
                "provider": config.provider,
                "model_name": config.model_name,
                "api_key": api_key
            }
        except Exception:
            return None
