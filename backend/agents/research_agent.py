from .base_agent import BaseAgent
from typing import Dict, Any
import json

class ResearchAgent(BaseAgent):
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

    async def suggest_locations(self, existing_locations: list) -> list:
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
        
        response = await self.llm.invoke([{"role": "user", "content": prompt}])
        return json.loads(response.content)

    async def compile_description(self, location_name: str) -> str:
        prompt = f"""
        Create a comprehensive but concise description for {location_name} as an outdoor recreation destination.
        Focus on:
        1. Key outdoor activities and attractions
        2. Accessibility and amenities
        3. Best seasons to visit
        4. Any unique features
        
        Keep the description under 200 words.
        """
        
        response = await self.llm.invoke([{"role": "user", "content": prompt}])
        return response.content 