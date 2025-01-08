from .base_agent import BaseAgent
import psycopg2
from typing import Dict, Any, List, Tuple
import json
from decimal import Decimal
from schema.database_schema import LOCATIONS_SCHEMA, ACTIVITY_SCORES_SCHEMA, VALID_ACTIVITIES

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class DatabaseAgent(BaseAgent):
    def __init__(self, anthropic_api_key: str, db_config: dict, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__(anthropic_api_key=anthropic_api_key, model=model)
        self.db_config = db_config
        self.schema = self._get_schema()
        
    def get_location_names(self) -> List[str]:
        """Get just the names of all locations"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        try:
            cur.execute("SELECT DISTINCT name FROM locations ORDER BY name")
            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()
    
    def _get_schema(self) -> str:
        """Get the database schema"""
        return f"""
        Locations Table:
        {LOCATIONS_SCHEMA}
        
        Activity Scores Table:
        {ACTIVITY_SCORES_SCHEMA}
        
        Valid Activities:
        {', '.join(VALID_ACTIVITIES)}
        """

    def execute_query(self, query: str) -> Tuple[List[Dict[str, Any]], str]:
        """Execute a query and return results and message"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        try:
            # First, have the LLM verify the query is safe
            safety_prompt = f"""
            Analyze this SQL query for safety:
            {query}
            
            Check for:
            1. Potential SQL injection
            2. Destructive operations (verify they're intended)
            3. Performance issues with large datasets
            
            Reply with either:
            SAFE: <explanation>
            or
            UNSAFE: <explanation>
            """
            
            safety_check = self.llm.invoke([{"role": "user", "content": safety_prompt}])
            if safety_check.content.startswith("UNSAFE"):
                return [], f"Query rejected: {safety_check.content}"
            
            cur.execute(query)
            
            # Handle different query types
            if cur.description:  # SELECT query
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
            else:  # INSERT, UPDATE, DELETE
                results = []
                
            conn.commit()
            return results, "Query executed successfully"
            
        except psycopg2.Error as e:
            conn.rollback()
            return [], f"Database error: {str(e)}"
        finally:
            cur.close()
            conn.close()

    @property
    def capabilities(self) -> str:
        return """
        - Query database contents
        - List all locations
        - Get specific location details
        - Check if location exists
        """
    
    def process(self, query: str) -> str:
        """Process database-related queries"""
        query = query.lower()
        
        # Add location to database
        if "add" in query and "to the database" in query:
            try:
                # Extract JSON data from query
                start = query.find('{')
                end = query.rfind('}') + 1
                if start == -1 or end == -1:
                    return "No valid JSON data found in the query"
                
                json_str = query[start:end]
                location_data = json.loads(json_str)
                
                # Insert into database
                success = self.add_location(location_data)
                if success:
                    return f"Successfully added {location_data['name']} to the database!"
                else:
                    return "Failed to add location to database"
            except json.JSONDecodeError:
                return "Invalid JSON data provided"
            except Exception as e:
                return f"Error adding location: {str(e)}"
        
        # List all locations
        if any(phrase in query for phrase in ["what cities", "list all", "show all", "select * from"]):
            locations = self.get_location_names()
            if not locations:
                return "The database is currently empty."
            return "Current locations in database:\n" + "\n".join(f"• {loc}" for loc in locations)
        
        # Get specific location details
        if "what is" in query or "details for" in query or "tell me about" in query:
            for loc in self.get_location_names():
                if loc.lower() in query:
                    return self.get_location_details(loc)
            return "Location not found in database."
        
        return "I don't understand that database query. Try asking about what cities are included or details about a specific location."
    
    def get_location_details(self, location_name: str) -> str:
        """Get formatted details for a specific location"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT name, latitude, longitude, description, activities 
                FROM locations 
                WHERE name = %s
            """, (location_name,))
            result = cur.fetchone()
            
            if not result:
                return f"No details found for {location_name}"
            
            name, lat, lon, desc, activities = result
            activities_str = "\n".join(
                f"• {act}: {score}/100" 
                for act, score in activities.items()
            )
            
            return f"""
Location: {name}
Coordinates: {lat}, {lon}

Description:
{desc}

Activities:
{activities_str}
"""
        finally:
            cur.close()
            conn.close() 
    
    def add_location(self, data: Dict[str, Any]) -> bool:
        """Add a new location to the database"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        try:
            # Insert into locations table
            cur.execute("""
                INSERT INTO locations (name, latitude, longitude, description, activities)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["name"],
                data["latitude"],
                data["longitude"],
                data["description"],
                json.dumps(data["activities"])
            ))
            
            location_id = cur.fetchone()[0]
            
            # Insert activity scores
            for activity, score in data["activities"].items():
                cur.execute("""
                    INSERT INTO activity_scores (location_id, activity_type, score)
                    VALUES (%s, %s, %s)
                """, (location_id, activity, score))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close() 