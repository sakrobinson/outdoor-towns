import streamlit as st
from agents.db_agent import DatabaseAgent
from agents.research_agent import ResearchAgent
from agents.base_agent import BaseAgent
import json

# Initialize agents
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]
db_config = {
    "dbname": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"]
}

# Initialize agents with shared knowledge
base_agent = BaseAgent(anthropic_api_key=anthropic_api_key)
db_agent = DatabaseAgent(anthropic_api_key=anthropic_api_key, db_config=db_config)
research_agent = ResearchAgent(anthropic_api_key=anthropic_api_key, db_agent=db_agent)

# Define available agents
agents = {
    'database': db_agent,
    'research': research_agent
}

# Initialize known locations
research_agent.known_locations = db_agent.get_location_names()

# Initialize chat history if not exists
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Outdoor Towns Database Manager")

# Sidebar for mode selection
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Chat Interface", "View Existing", "Add Suggestions"]
)

def route_query(query: str) -> str:
    """Route the query to the appropriate agent"""
    query = query.lower()
    
    # Database queries
    db_phrases = ["what cities", "list all", "show all", "in the database", "locations", "cities included"]
    if any(phrase in query for phrase in db_phrases):
        return db_agent.process(query)
    
    # Handle update/replace requests
    replace_phrases = ["replace", "update", "redo", "refresh"]
    if any(phrase in query for phrase in replace_phrases):
        # Extract location name
        location = query
        for phrase in replace_phrases + ["entry", "with", "new", "research"]:
            location = location.replace(phrase, "")
        location = location.strip()
        
        # If no location specified, check if there's a pending operation
        if not location and "last_location" in st.session_state:
            location = st.session_state.last_location
        
        if location:
            # Store for potential follow-up
            st.session_state.last_location = location
            
            # First delete the existing entry
            delete_result = db_agent.process(f"delete {location}")
            if "not found" in delete_result.lower() or "error" in delete_result.lower():
                return delete_result
                
            # Then research and add as new
            return research_agent.process(f"research {location}")
            
        return "Please specify which location to replace/update."
    
    # Direct routing for research patterns
    if query.startswith("research") or "research" in query:
        # Store the location being researched
        location = query.replace("research", "").strip()
        if location:
            st.session_state.last_location = location
        return research_agent.process(query)
        
    # Handle confirmation and database addition
    if any(word in query.lower() for word in ["yes", "add", "confirm"]):
        if "pending_location" in st.session_state:
            data = st.session_state.pending_location
            # Clean up session state after use
            del st.session_state.pending_location
            return db_agent.process(f"add to the database: {json.dumps(data)}")
        else:
            return research_agent.process(query)  # Let research agent handle suggestions
    
    # Handle delete/remove requests
    if any(cmd in query for cmd in ["delete", "remove"]):
        return db_agent.process(query)
    
    # Route to research agent for suggestions
    suggestion_phrases = ["what city should", "what town should", "suggest", "recommendation"]
    if any(phrase in query for phrase in suggestion_phrases):
        return research_agent.process(query)
    
    # Default routing through LLM
    routing_prompt = f"""
    Given this user query: "{query}"
    
    Which agent should handle this request?
    
    Available agents:
    1. database: {db_agent.capabilities}
    2. research: {research_agent.capabilities}
    
    Reply with just the agent name (database or research).
    """
    
    response = base_agent.llm.invoke([{"role": "user", "content": routing_prompt}])
    selected_agent = response.content.strip().lower()
    
    if selected_agent not in agents:
        return f"I'm sorry, I couldn't determine how to handle: '{query}'. Try asking about cities in the database or researching a specific location."
    
    return agents[selected_agent].process(query)

if mode == "Chat Interface":
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = route_query(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

elif mode == "View Existing":
    locations = db_agent.get_existing_locations()
    st.write("Current locations in database:", locations)

elif mode == "Add Suggestions":
    if st.button("Get New Suggestions"):
        with st.spinner("Researching new locations..."):
            existing = db_agent.get_existing_locations()
            suggestions = research_agent.suggest_locations(existing)
            
            for suggestion in suggestions:
                st.subheader(f"{suggestion['name']}, {suggestion['state']}")
                st.write("Primary activities:", ", ".join(suggestion['primary_activities']))
                
                if st.button(f"Generate description for {suggestion['name']}"):
                    description = research_agent.compile_description(suggestion['name'])
                    st.write("Generated description:", description)
                    
                    if st.button("Add to database"):
                        location_data = {
                            "name": suggestion['name'],
                            "description": description,
                            # You'd need to add logic to get lat/long
                            "activities": {}  # Add logic to format activities
                        }
                        success = db_agent.add_location(location_data)
                        if success:
                            st.success("Location added!")
                        else:
                            st.error("Failed to add location")