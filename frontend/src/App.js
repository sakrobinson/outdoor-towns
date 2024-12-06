import { useState, useEffect } from 'react';
import MapComponent from './components/Map';
import LocationCard from './components/LocationCard';
import SearchBar from './components/SearchBar';
import { locationService } from './services/locationService';
import './App.css';

function App() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      setLoading(true);
      const data = await locationService.getLocations();
      setLocations(data);
    } catch (err) {
      setError('Failed to fetch locations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSelect = (location) => {
    console.log('Selected:', location);
  };

  const handleSearch = (searchTerm) => {
    console.log('Searching for:', searchTerm);
    // implement search filtering later
  };

  if (loading) return <div>Loading locations...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="App">
      <header className="App-header">
        <h1>OutdoorTowns</h1>
        <SearchBar onSearch={handleSearch} />
      </header>
      <div className="main-content">
        <div className="locations-list">
          {locations.map(location => (
            <LocationCard 
              key={location.id}
              location={location}
              onSelect={handleLocationSelect}
            />
          ))}
        </div>
        <div className="map-container">
          <MapComponent locations={locations} />
        </div>
      </div>
    </div>
  );
}

export default App;