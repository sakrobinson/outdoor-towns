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

    def process(self, query: str) -> str:
        """Process the query using LLM to generate SQL"""
        sql_generation_prompt = f"""
        Given this database schema:
        {self.schema}
        
        And this user request:
        "{query}"
        
        Generate a SQL query to fulfill this request. Consider:
        1. The appropriate SQL operation (SELECT, INSERT, UPDATE, DELETE)
        2. Necessary table joins
        3. Proper WHERE clauses
        4. Data integrity
        
        Return only the SQL query, no explanation.
        """
        
        generated_sql = self.llm.invoke([{"role": "user", "content": sql_generation_prompt}])
        sql_query = generated_sql.content.strip()
        
        results, message = self.execute_query(sql_query)
        
        # Have the LLM format the response
        response_prompt = f"""
        Given these query results:
        {json.dumps(results, indent=2, cls=DecimalEncoder)}
        
        Format a CONCISE response that lists ONLY the relevant information.
        No explanations or summaries.
        No "I can provide" or similar phrases.
        Just the facts in a clean format.
        
        Query: "{query}"
        """
        
        response = self.llm.invoke([{"role": "user", "content": response_prompt}])
        return response.content 