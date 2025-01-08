from langchain_anthropic import ChatAnthropic
from typing import Dict, Any, List
from datetime import datetime

class BaseAgent:
    def __init__(self, anthropic_api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        self.llm = ChatAnthropic(
            anthropic_api_key=anthropic_api_key,
            model=model
        )
        self.conversation_history: List[Dict[str, Any]] = []
        
    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_recent_history(self, limit: int = 5) -> str:
        """Get recent conversation history formatted as string"""
        recent = self.conversation_history[-limit:] if self.conversation_history else []
        if not recent:
            return ""
            
        history = "\nRecent conversation:\n"
        for msg in recent:
            history += f"{msg['role']}: {msg['content']}\n"
        return history
    
    @property
    def capabilities(self) -> str:
        """Define what this agent can do - to be overridden by subclasses"""
        return ""
    
    def can_handle(self, query: str) -> bool:
        """Determine if this agent can handle the given query"""
        prompt = f"""
        Given this user query: "{query}"
        
        And these agent capabilities:
        {self.capabilities}
        
        Should this agent handle this query? Reply with just 'yes' or 'no'.
        Explain your reasoning in a second line.
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return response.content.lower().startswith('yes')
    
    def process(self, query: str) -> str:
        """Process the query - to be overridden by subclasses"""
        raise NotImplementedError 