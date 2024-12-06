const API_URL = 'http://localhost:5000/api';

export const locationService = {
  async getLocations() {
    try {
      const response = await fetch(`${API_URL}/locations`);
      const data = await response.json();
      return data.data; // Assuming your API returns { data: [...locations] }
    } catch (error) {
      console.error('Error fetching locations:', error);
      return [];
    }
  },

  async getLocationById(id) {
    try {
      const response = await fetch(`${API_URL}/locations/${id}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching location:', error);
      throw error;
    }
  }
}; 