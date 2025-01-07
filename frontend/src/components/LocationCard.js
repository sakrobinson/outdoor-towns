import React from 'react';
import { ACTIVITY_LABELS } from '../types/location';

function ActivityScore({ activity, score }) {
  return (
    <div className="activity-score">
      <span className="activity-label">{ACTIVITY_LABELS[activity]}</span>
      <div className="score-bar">
        <div 
          className="score-fill" 
          style={{ width: `${score * 20}%` }} // Convert 1-5 to percentage
        />
      </div>
      <span className="score-number">{score}/5</span>
    </div>
  );
}

function LocationCard({ location, onSelect }) {
  return (
    <div 
      className="location-card"
      onClick={() => onSelect(location)}
    >
      <h3>{location.name}</h3>
      <p>{location.description}</p>
      <div className="activities-grid">
        {Object.entries(location.activities || {}).map(([activity, score]) => (
          <ActivityScore 
            key={activity} 
            activity={activity} 
            score={score}
          />
        ))}
      </div>
    </div>
  );
}

export default LocationCard; 