const pool = require('../config/db');

// Get all locations
const getLocations = async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM locations');
        res.json({
            status: 'success',
            data: result.rows
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({
            status: 'error',
            message: 'Error fetching locations'
        });
    }
};

// Get single location by ID
const getLocationById = async (req, res) => {
    try {
        const { id } = req.params;
        const result = await pool.query('SELECT * FROM locations WHERE id = $1', [id]);
        
        if (result.rows.length === 0) {
            return res.status(404).json({
                status: 'error',
                message: 'Location not found'
            });
        }

        res.json({
            status: 'success',
            data: result.rows[0]
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({
            status: 'error',
            message: 'Error fetching location'
        });
    }
};

// Create new location
const createLocation = async (req, res) => {
    try {
        const { name, latitude, longitude, description } = req.body;
        const result = await pool.query(
            'INSERT INTO locations (name, latitude, longitude, description) VALUES ($1, $2, $3, $4) RETURNING *',
            [name, latitude, longitude, description]
        );

        res.status(201).json({
            status: 'success',
            data: result.rows[0]
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({
            status: 'error',
            message: 'Error creating location'
        });
    }
};

// Update location
const updateLocation = async (req, res) => {
    try {
        const { id } = req.params;
        const { name, latitude, longitude, description } = req.body;
        
        const result = await pool.query(
            'UPDATE locations SET name = $1, latitude = $2, longitude = $3, description = $4 WHERE id = $5 RETURNING *',
            [name, latitude, longitude, description, id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({
                status: 'error',
                message: 'Location not found'
            });
        }

        res.json({
            status: 'success',
            data: result.rows[0]
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({
            status: 'error',
            message: 'Error updating location'
        });
    }
};

// Delete location
const deleteLocation = async (req, res) => {
    try {
        const { id } = req.params;
        const result = await pool.query('DELETE FROM locations WHERE id = $1 RETURNING *', [id]);

        if (result.rows.length === 0) {
            return res.status(404).json({
                status: 'error',
                message: 'Location not found'
            });
        }

        res.json({
            status: 'success',
            message: 'Location deleted successfully'
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({
            status: 'error',
            message: 'Error deleting location'
        });
    }
};

module.exports = {
    getLocations,
    getLocationById,
    createLocation,
    updateLocation,
    deleteLocation
}; 