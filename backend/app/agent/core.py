from typing import Dict, Any

class AnalystAgent:
    """
    Demo Analyst Agent that works without LLM API keys.
    In production, this would use LangChain/LangGraph with actual LLM integration.
    """
    def __init__(self):
        self.conversation_history = []

    async def process_query(self, query: str, context: Dict[str, Any]) -> str:
        """
        Process user query and return a response.
        Currently in demo mode - returns helpful messages without actual LLM.
        """
        self.conversation_history.append({"role": "user", "content": query})
        
        # Demo responses based on query keywords
        query_lower = query.lower()
        
        if "connect" in query_lower or "database" in query_lower:
            response = """To connect a database:
1. Go to the "Data Models" page
2. Click "Add Connection"
3. Enter your database credentials (PostgreSQL, MySQL, MS SQL, Oracle, etc.)
4. I'll automatically extract the schema and you can add business descriptions!"""
        
        elif "help" in query_lower or "what can you do" in query_lower:
            response = """I'm your Agentic Data Analyst! Here's what I can help you with:

📊 **Data Analysis**: Ask questions about your data in natural language
🔗 **Database Connections**: Connect to PostgreSQL, MySQL, MS SQL, Oracle, and more
📝 **Semantic Modeling**: Add business descriptions to your tables and columns
🤖 **Smart Queries**: I generate SQL queries based on your questions
📈 **Visualizations**: Create charts and graphs from your data
⚙️ **Process Mining**: Analyze business processes from event logs

To get started, connect a database or ask me a specific question!"""
        
        elif "sql" in query_lower or "query" in query_lower:
            response = """I can help you generate SQL queries! Once you connect a database and define your semantic model, I'll:

1. Understand your question in natural language
2. Search for relevant tables using vector search
3. Generate optimized SQL queries
4. Execute them safely and return results
5. Create visualizations if needed

Note: Currently in demo mode. Connect a database and add your OpenAI API key to enable full functionality."""
        
        else:
            response = f"""I received your question: "{query}"

🚀 **Demo Mode Active**: I'm currently running without an LLM API key. To enable full AI-powered analysis:

1. Add your OpenAI API key to `backend/.env`
2. Restart the backend server
3. I'll then be able to:
   - Generate SQL queries from natural language
   - Analyze your data intelligently
   - Create visualizations
   - Provide insights and recommendations

For now, try asking me about:
- "What can you do?"
- "How do I connect a database?"
- "Help with SQL queries" """
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
