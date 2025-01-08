# Connect as postgres user
sudo -u postgres psql

# In the PostgreSQL prompt, create the database and user:
CREATE DATABASE outdoor_towns;
CREATE USER outdoor_admin WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE outdoor_towns TO outdoor_admin;

# Connect to the new database
\c outdoor_towns

# Create the initial tables.
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

CREATE TABLE activity_scores (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location_id, activity_type)
);

# Grant privileges to the new user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO outdoor_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO outdoor_admin;

# Exit PostgreSQL
\q