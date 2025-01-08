# Outdoor Towns Agent Framework

A modular agent-based system for managing and researching outdoor recreation locations. Built with Anthropic's Claude and Streamlit.

## Architecture

### Base Agent (`BaseAgent`)
The foundation of the agent system, providing:
- LLM integration with Claude
- Conversation history management
- Capability declaration
- Query routing logic

### Specialized Agents

#### Research Agent (`ResearchAgent`)
Handles location research and data preparation:
- Researches new locations
- Validates location data against schema
- Prepares structured data for database insertion
- Activity scoring and validation

#### Database Agent (`DatabaseAgent`)
Manages database operations:
- Location CRUD operations
- Query validation and safety checks
- Data retrieval and formatting
- Activity score management

## State Management

The system uses Streamlit's session state for persistent data between interactions:
```python
# Store data
st.session_state.pending_location = location_data

# Retrieve data
if "pending_location" in st.session_state:
    location_data = st.session_state.pending_location
```

## Data Schema

### Locations
- Name (city, state format)
- Coordinates (latitude/longitude)
- Description (outdoor recreation focus)
- Activity scores (0-100)

### Valid Activities
- Hiking
- Climbing
- Biking
- Skiing
- Kayaking
- Camping

## Usage

### Initialize Agents
```python
research_agent = ResearchAgent(anthropic_api_key=api_key)
db_agent = DatabaseAgent(anthropic_api_key=api_key, db_config=config)
```

### Research Location
```python
response = research_agent.process("research Bend, Oregon")
```

### Add to Database
```python
if "pending_location" in st.session_state:
    db_agent.process(f"add to database: {json.dumps(location_data)}")
```

## Environment Setup

Required environment variables:
```
ANTHROPIC_API_KEY=your_api_key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
```

## Development

### Adding New Agent Types
1. Inherit from `BaseAgent`
2. Implement `capabilities` property
3. Implement `process` method
4. Add routing logic in `main.py`

### Extending Functionality
- Add new activities in `database_schema.py`
- Extend database schema for new features
- Add new agent types for specialized tasks

## Error Handling

The framework includes:
- Input validation
- Schema validation
- Database safety checks
- LLM response validation
- Coordinate validation
- Activity score validation

## Best Practices

1. Always validate LLM outputs
2. Use session state for persistence
3. Implement safety checks for DB operations
4. Keep conversation history for context
5. Validate data against schema before storage 