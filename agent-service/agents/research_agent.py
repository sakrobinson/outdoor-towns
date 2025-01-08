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
    def __init__(self, anthropic_api_key: str, db_agent=None, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(anthropic_api_key=anthropic_api_key, model=model)
        self.known_locations = []
        self.schema = self._get_schema()
        self.db_agent = db_agent  # Store reference to database agent
    
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
        - Suggest new locations to add
        """
    
    @property
    def available_commands(self) -> str:
        return """
        Available Commands:
        1. research [city, state]
           Example: research Bend, Oregon
        
        2. suggest location
           Example: suggest location
           Aliases: what city should I add, recommend location
        
        3. show locations
           Example: show locations
           Aliases: list cities, what cities are included
        
        4. help
           Show this command list
        """
    
    def interpret_intent(self, query: str) -> tuple[str, str]:
        """Convert natural language to command and parameters"""
        prompt = f"""
        Convert this user query into one of our supported commands:
        "{query}"
        
        Available commands:
        1. research [city] - Research a specific city
        2. suggest - Suggest a new location
        3. show - Show current locations
        4. help - Show available commands
        
        Return ONLY the command and any parameters in this format:
        command: parameter
        
        Examples:
        "what cities do we have?" -> "show:"
        "tell me about Boulder" -> "research: Boulder, Colorado"
        "what should we add next?" -> "suggest:"
        "how do I use this?" -> "help:"
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        result = response.content.strip().split(":", 1)
        command = result[0].strip().lower()
        parameter = result[1].strip() if len(result) > 1 else ""
        return command, parameter

    def suggest_next_location(self) -> Dict[str, Any]:
        """Suggest a new location that isn't in the known_locations list"""
        prompt = f"""
        You are a location recommendation expert. Suggest ONE outdoor recreation destination that is NOT in this list:
        {', '.join(self.known_locations)}
        
        Consider:
        1. Diverse geographic distribution
        2. Strong outdoor recreation opportunities
        3. Different types of activities
        4. Year-round accessibility
        
        Return ONLY the name in "City, State" format.
        """
        
        try:
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            suggested_location = response.content.strip()
            return suggested_location
        except Exception as e:
            raise ValueError(f"Error suggesting location: {str(e)}")

    def process(self, query: str) -> str:
        """Process research-related queries"""
        query = query.lower()
        
        # Show help if requested
        if query in ["help", "commands", "how does this work", "what can you do"]:
            return self.available_commands
        
        # Interpret natural language into command
        command, parameter = self.interpret_intent(query)
        
        # Handle commands
        if command == "help":
            return self.available_commands
            
        elif command == "show":
            try:
                self.known_locations = self.db_agent.get_location_names()
                return f"Current locations ({len(self.known_locations)}):\n" + "\n".join(f"• {loc}" for loc in self.known_locations)
            except Exception as e:
                return f"Error retrieving locations: {str(e)}"
            
        elif command == "suggest":
            # Update known locations from DB first
            try:
                self.known_locations = self.db_agent.get_location_names()
            except:
                pass  # Continue with existing known_locations if DB call fails
                
            try:
                suggested_location = self.suggest_next_location()
                return f"Based on the current database of {len(self.known_locations)} locations, I suggest researching {suggested_location}. Would you like me to research this location?"
            except Exception as e:
                return f"Error suggesting location: {str(e)}"
            
        elif command == "research":
            location_name = parameter if parameter else query.replace("research", "").replace("and add", "").strip()
            if not location_name:
                return "Please specify a location to research."
            
            # Update known locations from DB first
            try:
                self.known_locations = self.db_agent.get_location_names()
            except:
                pass
            
            # Check if location is already in database
            if location_name.lower() in [loc.lower() for loc in self.known_locations]:
                return f"{location_name} is already in the database. Would you like me to suggest a different location?"
                
            try:
                data = self.prepare_location_data(location_name)
                formatted_json = json.dumps(data, indent=2)
                
                # Store in session state
                import streamlit as st
                st.session_state.pending_location = data
                
                return f"""I've researched {location_name}. Here's what I found:\n\n{formatted_json}\n\nWould you like me to add this to the database?"""
            except Exception as e:
                return f"Error researching location: {str(e)}"
        
        # Handle confirmation responses
        if any(word in query for word in ["yes", "sure", "okay", "add", "confirm"]):
            import streamlit as st
            if "pending_location" in st.session_state:
                location_data = st.session_state.pending_location
                return f"Added {location_data['name']} to the database."
            else:
                return "No pending location to add. Try researching a location first."
        
        return "I don't understand that command. Type 'help' to see available commands."
    
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