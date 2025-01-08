from langchain_anthropic import ChatAnthropic
from typing import Dict, Any

class BaseAgent:
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240307"):
        self.llm = ChatAnthropic(
            api_key=api_key,
            model=model
        )
        
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError 