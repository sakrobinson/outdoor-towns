from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
from schema.database_schema import (
    LOCATIONS_SCHEMA,
    ACTIVITY_SCORES_SCHEMA,
    VALID_ACTIVITIES,
    get_location_template
)

class ResearchAgent(BaseAgent):
    def __init__(self, anthropic_api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(anthropic_api_key=anthropic_api_key, model=model)
        self.known_locations = []
        self.schema = self._get_schema()
    
    def _get_schema(self) -> str:
        """Get the database schema to ensure research matches required format"""
        return f"""
        Database Schema:
        {LOCATIONS_SCHEMA}
        
        Activity Scores:
        {ACTIVITY_SCORES_SCHEMA}
        
        Valid Activities:
        {', '.join(VALID_ACTIVITIES)}
        """
    
    @property
    def capabilities(self) -> str:
        return """
        - Research new locations
        - Prepare location data for database
        - Validate location information
        """
    
    def process(self, query: str) -> str:
        """Process research-related queries"""
        query = query.lower()
        
        if "research" in query:
            # Extract location name
            location_name = query.replace("research", "").replace("and add", "").strip()
            if not location_name:
                return "Please specify a location to research."
                
            try:
                data = self.prepare_location_data(location_name)
                formatted_json = json.dumps(data, indent=2)
                
                # Store in session state instead of instance variable
                import streamlit as st
                st.session_state.pending_location = data
                
                return f"""I've researched {location_name}. Here's what I found:\n\n{formatted_json}\n\nWould you like me to add this to the database?"""
            except Exception as e:
                return f"Error researching location: {str(e)}"
        
        # Check for various forms of add confirmation
        add_phrases = ["add", "yes", "please add", "add this", "add it"]
        if any(phrase in query.lower() for phrase in add_phrases):
            # Check session state instead of instance variable
            import streamlit as st
            if "pending_location" in st.session_state:
                location_data = st.session_state.pending_location
                # TODO: Add database insertion logic here
                return f"Added {location_data['name']} to the database."
            else:
                return "Please research a location first before trying to add it."
            
        return "I can help research locations. Try asking me to 'research [city name]'"
    
    def prepare_location_data(self, location_name: str) -> Dict[str, Any]:
        """Prepare complete location data for database insertion"""
        template = get_location_template()
        
        prompt = f"""
        You are a data preparation expert. Research {location_name} and return ONLY a JSON object.
        
        The data MUST match this database schema:
        {self.schema}
        
        Use this template format:
        {json.dumps(template, indent=2)}

        CRITICAL REQUIREMENTS:
        1. Return ONLY the JSON object
        2. All fields must match the database schema exactly
        3. Use real coordinates for the town center with 8 decimal places
        4. Score activities from 0 to 100 based on quality and availability
        5. Description should focus on outdoor recreation opportunities
        6. Only include activities from the Valid Activities list
        """
        
        try:
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            data = json.loads(response.content)
            
            # Add response to history
            self.add_to_history("assistant", json.dumps(data, indent=2))
            
            # Validate against schema requirements
            if not all(key in data for key in template.keys()):
                raise ValueError(f"Missing required fields. Required: {list(template.keys())}")
            
            # Validate activities
            for activity in data["activities"].keys():
                if activity not in VALID_ACTIVITIES:
                    raise ValueError(f"Invalid activity: {activity}")
                if not 0 <= data["activities"][activity] <= 100:
                    raise ValueError(f"Activity score must be 0-100: {activity}")
            
            # Validate coordinates
            if not isinstance(data["latitude"], (int, float)):
                raise ValueError("Latitude must be a number")
            if not isinstance(data["longitude"], (int, float)):
                raise ValueError("Longitude must be a number")
            if not (-90 <= data["latitude"] <= 90):
                raise ValueError("Invalid latitude")
            if not (-180 <= data["longitude"] <= 180):
                raise ValueError("Invalid longitude")
            
            return data
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from LLM: {str(e)}"
            self.add_to_history("error", error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error preparing location data: {str(e)}"
            self.add_to_history("error", error_msg)
            raise ValueError(error_msg)