import streamlit as st
from agents.db_agent import DatabaseAgent
from agents.research_agent import ResearchAgent
from utils.env_loader import load_env_vars, get_api_key
import asyncio
from agents.base_agent import BaseAgent

# Load environment variables
load_env_vars()
api_key = get_api_key("ANTHROPIC_API_KEY")

# Database configuration
db_config = {
    "dbname": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"]
}

# Initialize agents
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]  # Get from secrets
db_agent = DatabaseAgent(anthropic_api_key=anthropic_api_key, db_config=db_config)
research_agent = ResearchAgent(anthropic_api_key=anthropic_api_key)

# Initialize chat history if not exists
if "messages" not in st.session_state:
    st.session_state.messages = []

# Page setup
st.title("Outdoor Towns Database Manager")

# Sidebar for mode selection
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Chat Interface", "View Existing", "Add Suggestions"]
)

def route_query(query: str) -> str:
    """Route the query to the appropriate agent"""
    agents = [db_agent, research_agent]
    
    # Ask each agent if they can handle the query
    capable_agents = []
    for agent in agents:
        if agent.can_handle(query):
            capable_agents.append(agent)
    
    if not capable_agents:
        return "I'm sorry, none of our agents are equipped to handle this query."
    
    if len(capable_agents) > 1:
        # Let the LLM decide which agent is best suited
        selection_prompt = f"""
        Given this user query: "{query}"
        
        Multiple agents can handle this. Their capabilities are:
        
        {[f"Agent {i+1}: {agent.capabilities}" for i, agent in enumerate(capable_agents)]}
        
        Which agent (1-{len(capable_agents)}) would be best suited to handle this query?
        Reply with just the number and a brief explanation.
        """
        
        response = base_agent.llm.invoke([{"role": "user", "content": selection_prompt}])
        selected_agent = capable_agents[int(response.content.split()[0]) - 1]
    else:
        selected_agent = capable_agents[0]
    
    # Process the query with the selected agent
    return selected_agent.process(query)

# Update the chat interface
def process_chat_message(prompt: str) -> str:
    return route_query(prompt)

async def main():
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
                    response = process_chat_message(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

    elif mode == "View Existing":
        locations = await db_agent.get_existing_locations()
        st.write("Current locations in database:", locations)

    elif mode == "Add Suggestions":
        if st.button("Get New Suggestions"):
            with st.spinner("Researching new locations..."):
                existing = await db_agent.get_existing_locations()
                suggestions = await research_agent.suggest_locations(existing)
                
                for suggestion in suggestions:
                    st.subheader(f"{suggestion['name']}, {suggestion['state']}")
                    st.write("Primary activities:", ", ".join(suggestion['primary_activities']))
                    
                    if st.button(f"Generate description for {suggestion['name']}"):
                        description = await research_agent.compile_description(suggestion['name'])
                        st.write("Generated description:", description)
                        
                        if st.button("Add to database"):
                            location_data = {
                                "name": suggestion['name'],
                                "description": description,
                                # You'd need to add logic to get lat/long
                                "activities": {}  # Add logic to format activities
                            }
                            success = await db_agent.add_location(location_data)
                            if success:
                                st.success("Location added!")
                            else:
                                st.error("Failed to add location")

if __name__ == "__main__":
    asyncio.run(main())