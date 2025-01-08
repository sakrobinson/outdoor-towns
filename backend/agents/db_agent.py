from .base_agent import BaseAgent
import psycopg2
from typing import Dict, Any, List, Tuple

class DatabaseAgent(BaseAgent):
    def __init__(self, anthropic_api_key: str, db_config: dict, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(anthropic_api_key=anthropic_api_key, model=model)
        self.db_config = db_config
        
    @property
    def capabilities(self) -> str:
        return """
        I can:
        - List all locations in the database
        - Add new locations with their details
        - Remove locations by ID or name
        - Update existing location information
        - Query location details
        - Manage activity scores for locations
        
        I handle queries about existing data, database operations, and data management.
        """
    
    def get_existing_locations(self) -> List[Dict[str, Any]]:
        """Get all locations with their details"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, name, latitude, longitude, description, activities 
                FROM locations
                ORDER BY name
            """)
            columns = [desc[0] for desc in cur.description]
            locations = [dict(zip(columns, row)) for row in cur.fetchall()]
            return locations
        finally:
            cur.close()
            conn.close()
    
    def process(self, query: str) -> str:
        """Process the query and return a response"""
        # Use the LLM to determine what operation is needed
        operation_prompt = f"""
        Given this user query: "{query}"
        
        Determine what database operation is needed. Options are:
        1. list_locations (show all locations)
        2. get_location_details (show details for a specific location)
        3. add_location (add a new location)
        4. remove_location (remove a location)
        
        Return just the operation name.
        """
        
        operation = self.llm.invoke([{"role": "user", "content": operation_prompt}])
        operation_type = operation.content.strip().lower()
        
        if operation_type == 'list_locations':
            locations = self.get_existing_locations()
            if not locations:
                return "The database is currently empty."
            
            location_list = "\n".join([f"- {loc['name']}" for loc in locations])
            return f"Here are the locations in the database:\n{location_list}"
            
        # Add other operations as needed
        return f"Operation {operation_type} not yet implemented" 