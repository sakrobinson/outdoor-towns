from .base_agent import BaseAgent
import psycopg2
from typing import Dict, Any, List

class DatabaseAgent(BaseAgent):
    def __init__(self, api_key: str, db_config: dict):
        super().__init__(api_key)
        self.db_config = db_config
        
    async def get_existing_locations(self) -> List[str]:
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        cur.execute("SELECT name FROM locations")
        locations = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return locations
        
    async def add_location(self, location_data: dict) -> bool:
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO locations (name, latitude, longitude, description, activities)
                VALUES (%(name)s, %(latitude)s, %(longitude)s, %(description)s, %(activities)s)
            """, location_data)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding location: {e}")
            return False
        finally:
            cur.close()
            conn.close() 