LOCATIONS_SCHEMA = """
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    description TEXT,
    activities JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

ACTIVITY_SCORES_SCHEMA = """
CREATE TABLE activity_scores (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location_id, activity_type)
);
"""

VALID_ACTIVITIES = [
    "hiking",
    "climbing",
    "biking",
    "skiing",
    "kayaking",
    "camping"
]

def get_location_template() -> dict:
    """Return a template for location data"""
    return {
        "name": "City, State",  # Example: "Bend, Oregon"
        "latitude": 0.00000000,  # 8 decimal places
        "longitude": 0.00000000,  # 8 decimal places
        "description": "Description focusing on outdoor recreation",
        "activities": {activity: 0 for activity in VALID_ACTIVITIES}  # Scores 0-100
    } 