const express = require('express');
const router = express.Router();
const { 
  getLocations, 
  getLocationById, 
  createLocation, 
  updateLocation, 
  deleteLocation 
} = require('../controllers/locationController');

router.get('/', getLocations);
router.get('/:id', getLocationById);
router.post('/', createLocation);
router.put('/:id', updateLocation);
router.delete('/:id', deleteLocation);

module.exports = router; 