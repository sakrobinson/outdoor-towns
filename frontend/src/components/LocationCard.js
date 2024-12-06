import React from 'react';

function LocationCard({ location, onSelect }) {
  return (
    <div 
      className="location-card"
      onClick={() => onSelect(location)}
    >
      <h3>{location.name}</h3>
      <p>{location.description}</p>
      <div className="location-activities">
        {/* We'll add activity icons/scores here later */}
      </div>
    </div>
  );
}

export default LocationCard; 