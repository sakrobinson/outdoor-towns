import streamlit as st
from agents.db_agent import DatabaseAgent
from agents.research_agent import ResearchAgent
from utils.env_loader import load_env_vars, get_api_key
import asyncio

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
db_agent = DatabaseAgent(api_key, db_config)
research_agent = ResearchAgent(api_key)

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

async def process_chat_message(message: str) -> str:
    # Route the message to the appropriate agent based on content
    if any(keyword in message.lower() for keyword in ["database", "cities", "locations", "towns"]):
        locations = await db_agent.get_existing_locations()
        return f"Database Agent: Here are the current locations: {', '.join(locations)}"
    
    elif any(keyword in message.lower() for keyword in ["suggest", "recommend", "new", "research"]):
        existing = await db_agent.get_existing_locations()
        suggestions = await research_agent.suggest_locations(existing)
        return f"Research Agent: Here are some suggestions:\n" + \
               "\n".join([f"- {s['name']}, {s['state']}: {', '.join(s['primary_activities'])}" 
                         for s in suggestions])
    
    else:
        return "I'm not sure which agent should handle this request. Try asking about database contents or requesting suggestions."

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
                    response = await process_chat_message(prompt)
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