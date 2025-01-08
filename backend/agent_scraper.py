import streamlit as st
from agents.db_agent import DatabaseAgent
from agents.research_agent import ResearchAgent
from agents.base_agent import BaseAgent

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
research_agent = ResearchAgent(anthropic_api_key=anthropic_api_key)

# Update known locations
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
    # Update research agent's known locations before processing
    research_agent.known_locations = db_agent.get_location_names()
    
    agents = {
        'database': db_agent,
        'research': research_agent
    }
    
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
        return f"I'm sorry, I couldn't determine which agent should handle: '{query}'"
    
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