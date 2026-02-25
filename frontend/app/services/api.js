const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001/api';
// Database API is now integrated into the main API
const DATABASE_API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_DATABASE_URL || 'http://localhost:8001/api';
const ROOT_API_URL = API_BASE_URL.endsWith('/api') ? API_BASE_URL.slice(0, -4) : API_BASE_URL;

const AUTH_STORAGE_KEY = 'travelgenie-auth-user';

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
    console.log(`[API] Calling: ${url}`);
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      console.error(`[API Error] ${url}:`, error);
      throw new Error(error.detail || error.error || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[API Error]', url, error);
    throw error;
  }
}

async function fetchRootAPI(endpoint, options = {}) {
  const url = `${ROOT_API_URL}${endpoint}`;

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
    console.log(`[Root API] Calling: ${url}`);
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      console.error(`[Root API Error] ${url}:`, error);
      throw new Error(error.detail || error.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[Root API Error]', url, error);
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
  
  getForecast: async (lat, lon, days = 7) => {
    return fetchAPI(`/weather/forecast?lat=${lat}&lon=${lon}&days=${days}`);
  },
  
  geocodeLocation: async (city, country = null) => {
    let endpoint = `/weather/geocode?city=${encodeURIComponent(city)}`;
    if (country) {
      endpoint += `&country=${encodeURIComponent(country)}`;
    }
    return fetchAPI(endpoint);
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
  
};

// Intelligent Itinerary API (Unified endpoint with AI ranking, route optimization, enrichment)
export const intelligentItineraryAPI = {
  generate: async (request) => {
    return fetchAPI('/generate/intelligent-itinerary', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },
  
  getSupportedMoods: async () => {
    return fetchAPI('/generate/intelligent-itinerary/supported-moods');
  },
  
  getSupportedTravelTypes: async () => {
    return fetchAPI('/generate/intelligent-itinerary/supported-travel-types');
  },
  
  getFeatures: async () => {
    return fetchAPI('/generate/intelligent-itinerary/features');
  },
  
  healthCheck: async () => {
    return fetchAPI('/generate/intelligent-itinerary/health');
  },
};

// Flight Search API (Amadeus integration)
export const flightsAPI = {
  searchFlights: async ({
    origin,
    destination,
    departure_date,
    return_date,
    adults = 1,
    budget,
    cabin_class = 'ECONOMY',
    max_stops = 2,
    baggage_required = false,
    ranking_preference = 'balanced',
    non_stop_only = false,
  }) => {
    return fetchRootAPI('/search/flights', {
      method: 'POST',
      body: JSON.stringify({
        origin,
        destination,
        departure_date,
        return_date,
        adults,
        budget,
        cabin_class,
        max_stops,
        baggage_required,
        ranking_preference,
        non_stop_only,
      }),
    });
  },
};

export const trainsAPI = {
  searchTrains: async ({
    origin,
    destination,
    travel_date,
    passengers = 1,
    budget,
    max_transfers = 1,
    ranking_preference = 'balanced',
  }) => {
    return fetchRootAPI('/search/trains', {
      method: 'POST',
      body: JSON.stringify({
        origin,
        destination,
        travel_date,
        passengers,
        budget,
        max_transfers,
        ranking_preference,
      }),
    });
  },
};

export const busesAPI = {
  searchBuses: async ({
    origin,
    destination,
    travel_date,
    passengers = 1,
    budget,
    max_stops = 2,
    ranking_preference = 'balanced',
  }) => {
    return fetchRootAPI('/search/buses', {
      method: 'POST',
      body: JSON.stringify({
        origin,
        destination,
        travel_date,
        passengers,
        budget,
        max_stops,
        ranking_preference,
      }),
    });
  },
};

// ============== DATABASE-BASED WISHLIST & ITINERARY APIs ==============

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
    console.log(`[Database API] Calling: ${url}`);
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      console.error(`[Database API Error] ${url}:`, error);
      throw new Error(error.detail || error.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[Database API Error]', url, error);
    throw error;
  }
}

// Database-based Wishlist API
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

// Database-based Saved Itineraries API
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

// Authentication API
export const authAPI = {
  register: async ({ username, password, email, phone_number }) => {
    return fetchAPI('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username,
        password,
        email,
        phone_number,
      }),
    });
  },

  login: async ({ username, password }) => {
    const response = await fetchAPI('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });

    if (typeof window !== 'undefined' && response?.data?.user_id) {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(response.data));
      localStorage.setItem('travelgenie-user-id', response.data.user_id);
    }

    return response;
  },

  logout: () => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem('travelgenie-user-id');
  },

  getCurrentUser: () => {
    if (typeof window === 'undefined') return null;
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },

  isAuthenticated: () => {
    return !!authAPI.getCurrentUser();
  },
};

export { getUserId };
