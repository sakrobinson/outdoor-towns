from .base_agent import BaseAgent
from typing import Dict, Any, List
import json

class ResearchAgent(BaseAgent):
    def __init__(self, anthropic_api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(anthropic_api_key=anthropic_api_key, model=model)
        self.known_locations: List[str] = []
        
    @property
    def capabilities(self) -> str:
        return """
        I can:
        - Suggest new outdoor towns to add to the database
        - Research and compile descriptions for locations
        - Identify primary outdoor activities for locations
        - Provide information about seasonal activities
        - Compare different locations
        
        I handle queries about discovering new locations, research, and analysis.
        """

    def process(self, query: str) -> str:
        """Process research-related queries"""
        # Add query to history
        self.add_to_history("user", query)
        
        prompt = f"""
        You are a knowledgeable outdoor recreation expert.
        
        {self.get_recent_history()}
        
        Current known locations: {', '.join(self.known_locations)}
        
        User query: "{query}"
        
        If they're asking about suggesting new locations:
        1. DO NOT suggest any locations already mentioned in the conversation or known locations
        2. Recommend ONE notable outdoor town that would be a good addition
        3. Include:
           - Town name and location
           - Key outdoor activities
           - Brief description of why it's notable
           - Best seasons to visit
        
        If they're asking about comparing locations or other research questions:
        Provide a detailed but concise response.
        
        Format your response in a clear, readable way.
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Add response to history
        self.add_to_history("assistant", response.content)
        
        # Extract any new locations mentioned in the response
        # This is a simple implementation - you might want more sophisticated location extraction
        words = response.content.split()
        for i, word in enumerate(words):
            if word in ["in", "at", "near"] and i + 1 < len(words):
                potential_location = words[i + 1].strip(",.!")
                if potential_location not in self.known_locations:
                    self.known_locations.append(potential_location)
        
        return response.content

    def suggest_locations(self, existing_locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest new locations to add"""
        prompt = f"""
        You are a knowledgeable outdoor recreation expert. Given this list of existing locations:
        {existing_locations}
        
        Suggest 3 additional notable outdoor towns that should be added to the database.
        Focus on locations known for multiple outdoor activities.
        
        Return your response as a JSON array with objects containing:
        - name: town name
        - state: state or province
        - country: country
        - primary_activities: list of main outdoor activities
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return json.loads(response.content)

    def compile_description(self, location_name: str) -> str:
        """Create a detailed description for a location"""
        prompt = f"""
        Create a comprehensive but concise description for {location_name} as an outdoor recreation destination.
        Focus on:
        1. Key outdoor activities and attractions
        2. Accessibility and amenities
        3. Best seasons to visit
        4. Any unique features
        
        Keep the description under 200 words.
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return response.content 