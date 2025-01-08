# OutdoorTowns Backend

## API Testing

### Prerequisites
- Install a REST client like [Postman](https://www.postman.com/) or use `curl` in terminal
- Ensure the backend server is running (`npm run dev`)
- Base URL: `http://localhost:5000`

### Available Endpoints

#### Get All Locations 

`bash`
curl http://localhost:5000/api/locations

#### Get Single Location
`bash`
curl http://localhost:5000/api/locations/1

#### Create New Location
`bash`
curl -X POST http://localhost:5000/api/locations \
-H "Content-Type: application/json" \
-d '{
"name": "Squamish, BC",
"latitude": 49.7016,
"longitude": -123.1558,
"description": "World-class climbing destination with amazing hiking trails"
}'

#### Update Location
`bash`
curl -X PUT http://localhost:5000/api/locations/1 \
-H "Content-Type: application/json" \
-d '{
"name": "Updated Name",
"latitude": 49.7016,
"longitude": -123.1558,
"description": "Updated description"
}'


## Database Queries

### Connect to Database
sudo -u postgres psql outdoor_towns

### List all tables 
\dt

### View table structure
\d locations
\d activity scores
### Useful PostgreSQL Queries

#### Basic Queries. Examples:
`sql`
-- Get all locations
SELECT * FROM locations;
-- Get location with specific activities
SELECT l., a.activity_type, a.score
FROM locations l
JOIN activity_scores a ON l.id = a.location_id
WHERE l.id = 1;
-- Get top locations for specific activity
SELECT l.name, a.score
FROM locations l
JOIN activity_scores a ON l.id = a.location_id
WHERE a.activity_type = 'climbing'
ORDER BY a.score DESC
LIMIT 5;


## Troubleshooting

### Database Connection Issues
1. Verify PostgreSQL is running:
`bash`
sudo systemctl status postgresql

2. Check database credentials:
`bash`
sudo -u postgres psql -c "\l" | grep outdoor_towns