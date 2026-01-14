const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const DATABASE_API_URL = process.env.NEXT_PUBLIC_DATABASE_URL || 'http://localhost:8001/api';

// Generate a structured user ID if not exists
const getUserId = () => {
  if (typeof window === 'undefined') return 'guest_anonymous';
  let userId = localStorage.getItem('travelgenie-user-id');
  if (!userId) {
    // Generate structured user ID: tg_user_YYYYMMDD_XXXXXX
    const now = new Date();
    const datePart = now.getFullYear().toString() + 
                     String(now.getMonth() + 1).padStart(2, '0') + 
                     String(now.getDate()).padStart(2, '0');
    const randomPart = String(Math.floor(100000 + Math.random() * 900000)); // 6-digit number
    userId = `tg_user_${datePart}_${randomPart}`;
    localStorage.setItem('travelgenie-user-id', userId);
  }
  return userId;
};

async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || error.error || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Chat API
export const chatAPI = {
  sendMessage: async (message, language = 'en-US', conversationHistory = []) => {
    return fetchAPI('/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        message,
        language,
        conversation_history: conversationHistory,
      }),
    });
  },
};

// Destinations API
export const destinationsAPI = {
  getRandomDestinations: async (count = 9) => {
    return fetchAPI(`/destinations/random?count=${count}`);
  },
  
  getAllDestinations: async () => {
    return fetchAPI('/destinations/all');
  },
  
  searchDestinations: async (query, limit = 6) => {
    return fetchAPI(`/destinations/search?query=${encodeURIComponent(query)}&limit=${limit}`);
  },
};

// Weather API
export const weatherAPI = {
  getCurrentByCoords: async (lat, lon) => {
    return fetchAPI(`/weather/current?lat=${lat}&lon=${lon}`);
  },
  
  getCurrentByCity: async (city, country = null) => {
    let endpoint = `/weather/by-city?city=${encodeURIComponent(city)}`;
    if (country) {
      endpoint += `&country=${encodeURIComponent(country)}`;
    }
    return fetchAPI(endpoint);
  },
  
  getForecast: async (lat, lon, days = 5) => {
    return fetchAPI(`/weather/forecast?lat=${lat}&lon=${lon}&days=${days}`);
  },
};

// Itinerary API
export const itineraryAPI = {
  generate: async (destination, duration, interests, budget, travelStyle, language = 'en-US') => {
    return fetchAPI('/itinerary/generate', {
      method: 'POST',
      body: JSON.stringify({
        destination,
        duration,
        interests,
        budget,
        travel_style: travelStyle,
        language,
      }),
    });
  },
  
  customize: async (itinerary, modifications, language = 'en-US') => {
    return fetchAPI('/itinerary/customize', {
      method: 'POST',
      body: JSON.stringify({
        itinerary,
        modifications,
        language,
      }),
    });
  },
};

// ============== DATABASE APIs (Supabase) ==============

async function fetchDatabaseAPI(endpoint, options = {}) {
  const url = `${DATABASE_API_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || error.message || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Database API Error:', error);
    throw error;
  }
}

// Wishlist Database API
export const wishlistAPI = {
  getWishlist: async () => {
    const userId = getUserId();
    return fetchDatabaseAPI(`/wishlist/${userId}`);
  },
  
  addToWishlist: async (destination) => {
    const userId = getUserId();
    return fetchDatabaseAPI('/wishlist', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        destination_id: destination.id,
        destination_name: destination.name,
        destination_country: destination.country,
        destination_image: destination.image,
        destination_price: destination.price,
        destination_rating: destination.rating,
      }),
    });
  },
  
  removeFromWishlist: async (destinationId) => {
    const userId = getUserId();
    return fetchDatabaseAPI(`/wishlist/${userId}/destination/${destinationId}`, {
      method: 'DELETE',
    });
  },
  
  checkInWishlist: async (destinationId) => {
    const userId = getUserId();
    return fetchDatabaseAPI(`/wishlist/${userId}/check/${destinationId}`);
  },
  
  clearWishlist: async () => {
    const userId = getUserId();
    return fetchDatabaseAPI(`/wishlist/${userId}/clear`, {
      method: 'DELETE',
    });
  },
};

// Saved Itineraries Database API
export const savedItineraryAPI = {
  getAll: async () => {
    const userId = getUserId();
    return fetchDatabaseAPI(`/itinerary/${userId}`);
  },
  
  getById: async (itineraryId) => {
    return fetchDatabaseAPI(`/itinerary/detail/${itineraryId}`);
  },
  
  save: async (itineraryData) => {
    const userId = getUserId();
    return fetchDatabaseAPI('/itinerary', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        destination: itineraryData.destination,
        destination_country: itineraryData.destination_country || null,
        duration: itineraryData.duration,
        travel_style: itineraryData.travel_style || 'balanced',
        budget: itineraryData.budget || 'moderate',
        summary: itineraryData.summary,
        days: itineraryData.days,
        budget_estimate: itineraryData.budget_estimate,
        packing_tips: itineraryData.packing_tips,
        local_phrases: itineraryData.local_phrases,
      }),
    });
  },
  
  update: async (itineraryId, updateData) => {
    return fetchDatabaseAPI(`/itinerary/${itineraryId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  },
  
  delete: async (itineraryId) => {
    return fetchDatabaseAPI(`/itinerary/${itineraryId}`, {
      method: 'DELETE',
    });
  },
  
  getCount: async () => {
    const userId = getUserId();
    return fetchDatabaseAPI(`/itinerary/${userId}/count`);
  },
};

export { getUserId };
