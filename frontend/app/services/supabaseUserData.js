import { supabase } from './supabaseClient';

const AUTH_STORAGE_KEY = 'travelgenie-auth-user';

let cachedState = {
  user: null,
  wishlist: [],
  itineraries: [],
};

const listeners = new Set();

const notifyListeners = () => {
  listeners.forEach((listener) => {
    try {
      listener({ ...cachedState });
    } catch (error) {
      console.error('[Supabase] Listener error:', error);
    }
  });
};

const setCachedState = (patch) => {
  cachedState = {
    ...cachedState,
    ...patch,
  };
  notifyListeners();
};

const stableNumericId = (value = '') => {
  const text = String(value);
  let hash = 0;
  for (let index = 0; index < text.length; index += 1) {
    hash = (hash << 5) - hash + text.charCodeAt(index);
    hash |= 0;
  }
  return Math.abs(hash);
};

const normalizeItineraryFromRow = (row) => {
  const payload = row?.itinerary_json || {};
  return {
    id: row.id,
    destination: row.destination,
    destination_country: payload.destination_country || payload.country || 'Unknown',
    duration: payload.duration || 0,
    travel_style: payload.travel_style || 'balanced',
    budget: payload.budget || 'moderate',
    summary: payload.summary || `Trip plan for ${row.destination}`,
    days: payload.days || [],
    budget_estimate: payload.budget_estimate || null,
    packing_tips: payload.packing_tips || [],
    local_phrases: payload.local_phrases || [],
    is_public: Boolean(row.is_public),
    version: row.version || 1,
    created_at: row.created_at,
  };
};

const normalizeWishlistFromRow = (row) => ({
  id: stableNumericId(row.place_name),
  wishlist_row_id: row.id,
  destination_id: stableNumericId(row.place_name),
  destination_name: row.place_name,
  destination_country: 'Unknown',
  destination_image: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80',
  destination_price: '$299',
  destination_rating: 4.5,
  created_at: row.created_at,
});

const setAuthStorage = (user) => {
  if (typeof window === 'undefined') return;

  if (!user) {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem('travelgenie-user-id');
    return;
  }

  const payload = {
    user_id: user.id,
    email: user.email,
    username: user.user_metadata?.username || user.user_metadata?.name || user.email?.split('@')[0] || 'traveler',
    display_name: user.user_metadata?.full_name || user.user_metadata?.name || user.email?.split('@')[0] || 'Traveler',
  };

  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(payload));
  localStorage.setItem('travelgenie-user-id', user.id);
};

const getAuthenticatedUser = async ({ allowMissingSession = false } = {}) => {
  const { data: sessionData, error: sessionError } = await supabase.auth.getSession();

  if (sessionError) {
    throw sessionError;
  }

  if (!sessionData?.session) {
    if (allowMissingSession) {
      return null;
    }
    throw new Error('User not authenticated');
  }

  const { data: userData, error: userError } = await supabase.auth.getUser();
  if (userError) {
    throw userError;
  }
  if (!userData?.user) {
    if (allowMissingSession) {
      return null;
    }
    throw new Error('User not authenticated');
  }
  return userData.user;
};

export const subscribeUserState = (listener) => {
  listeners.add(listener);
  listener({ ...cachedState });
  return () => listeners.delete(listener);
};

export const getCachedUserState = () => ({ ...cachedState });

export const fetchWishlist = async (userIdParam = null) => {
  try {
    const user = userIdParam ? { id: userIdParam } : await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      setCachedState({ wishlist: [] });
      return { success: true, data: [], message: 'No active session' };
    }

    const userId = user.id;

    const { data, error } = await supabase
      .from('wishlist')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) throw error;

    const mapped = (data || []).map(normalizeWishlistFromRow);
    setCachedState({ wishlist: mapped });
    return { success: true, data: mapped, message: 'Wishlist retrieved' };
  } catch (error) {
    console.error('[Supabase Wishlist] fetchWishlist failed:', error);
    return { success: false, data: [], message: error.message || 'Failed to fetch wishlist' };
  }
};

export const addToWishlist = async (placeName) => {
  try {
    const user = await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      return { success: false, data: null, message: 'Please login to use wishlist' };
    }

    const safePlaceName = String(placeName || '').trim();

    if (!safePlaceName) {
      throw new Error('placeName is required');
    }

    const { data: existing, error: existingError } = await supabase
      .from('wishlist')
      .select('id')
      .eq('user_id', user.id)
      .eq('place_name', safePlaceName)
      .limit(1);

    if (existingError) throw existingError;

    if (existing?.length) {
      return { success: true, message: 'Already in wishlist', data: null };
    }

    const { data, error } = await supabase
      .from('wishlist')
      .insert({
        user_id: user.id,
        place_name: safePlaceName,
      })
      .select('*')
      .single();

    if (error) throw error;

    await fetchWishlist(user.id);
    return { success: true, data: data ? normalizeWishlistFromRow(data) : null, message: 'Added to wishlist' };
  } catch (error) {
    console.error('[Supabase Wishlist] addToWishlist failed:', error);
    return { success: false, data: null, message: error.message || 'Failed to add to wishlist' };
  }
};

export const removeFromWishlist = async (identifier) => {
  try {
    const user = await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      return { success: false, data: null, message: 'Please login to manage wishlist' };
    }

    const value = String(identifier || '').trim();

    if (!value) {
      throw new Error('Wishlist identifier is required');
    }

    let query = supabase.from('wishlist').delete().eq('user_id', user.id);
    const looksLikeUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);

    query = looksLikeUuid ? query.eq('id', value) : query.eq('place_name', value);

    const { error } = await query;
    if (error) throw error;

    await fetchWishlist(user.id);
    return { success: true, message: 'Removed from wishlist', data: null };
  } catch (error) {
    console.error('[Supabase Wishlist] removeFromWishlist failed:', error);
    return { success: false, data: null, message: error.message || 'Failed to remove wishlist item' };
  }
};

export const clearWishlist = async () => {
  try {
    const user = await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      setCachedState({ wishlist: [] });
      return { success: true, message: 'No active session', data: [] };
    }

    const { error } = await supabase
      .from('wishlist')
      .delete()
      .eq('user_id', user.id);

    if (error) throw error;

    setCachedState({ wishlist: [] });
    return { success: true, message: 'Wishlist cleared', data: [] };
  } catch (error) {
    console.error('[Supabase Wishlist] clearWishlist failed:', error);
    return { success: false, data: [], message: error.message || 'Failed to clear wishlist' };
  }
};

export const saveItinerary = async (destination, itineraryObject, isPublic = false) => {
  try {
    const user = await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      return { success: false, data: null, message: 'Please login to save itineraries' };
    }

    const safeDestination = String(destination || '').trim();

    if (!safeDestination) {
      throw new Error('destination is required');
    }

    const { data: existing, error: existingError } = await supabase
      .from('itinerary')
      .select('id')
      .eq('user_id', user.id)
      .eq('destination', safeDestination);

    if (existingError) throw existingError;

    const version = (existing || []).length + 1;

    const { data, error } = await supabase
      .from('itinerary')
      .insert({
        user_id: user.id,
        destination: safeDestination,
        itinerary_json: itineraryObject,
        is_public: Boolean(isPublic),
        version,
        created_at: new Date().toISOString(),
      })
      .select('*')
      .single();

    if (error) throw error;

    await fetchItineraries(user.id);

    return {
      success: true,
      message: 'Itinerary saved',
      data: data ? normalizeItineraryFromRow(data) : null,
    };
  } catch (error) {
    console.error('[Supabase Itinerary] saveItinerary failed:', error);
    return { success: false, data: null, message: error.message || 'Failed to save itinerary' };
  }
};

export const fetchItineraries = async (userIdParam = null) => {
  try {
    const user = userIdParam ? { id: userIdParam } : await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      setCachedState({ itineraries: [] });
      return { success: true, data: [], message: 'No active session' };
    }

    const userId = user.id;

    const { data, error } = await supabase
      .from('itinerary')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) throw error;

    const mapped = (data || []).map(normalizeItineraryFromRow);
    setCachedState({ itineraries: mapped });
    return { success: true, data: mapped, message: 'Itineraries retrieved' };
  } catch (error) {
    console.error('[Supabase Itinerary] fetchItineraries failed:', error);
    return { success: false, data: [], message: error.message || 'Failed to fetch itineraries' };
  }
};

export const deleteItinerary = async (id) => {
  try {
    const user = await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      return { success: false, data: null, message: 'Please login to delete itineraries' };
    }

    const { error } = await supabase
      .from('itinerary')
      .delete()
      .eq('id', id)
      .eq('user_id', user.id);

    if (error) throw error;

    await fetchItineraries(user.id);
    return { success: true, message: 'Itinerary deleted', data: null };
  } catch (error) {
    console.error('[Supabase Itinerary] deleteItinerary failed:', error);
    return { success: false, data: null, message: error.message || 'Failed to delete itinerary' };
  }
};

export const togglePublic = async (itineraryId, currentStatus) => {
  try {
    const user = await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      return { success: false, data: null, message: 'Please login to update visibility' };
    }

    const nextStatus = !Boolean(currentStatus);

    const { data, error } = await supabase
      .from('itinerary')
      .update({ is_public: nextStatus })
      .eq('id', itineraryId)
      .eq('user_id', user.id)
      .select('*')
      .single();

    if (error) throw error;

    await fetchItineraries(user.id);
    return {
      success: true,
      data: data ? normalizeItineraryFromRow(data) : null,
      message: nextStatus ? 'Itinerary is now public' : 'Itinerary is now private',
    };
  } catch (error) {
    console.error('[Supabase Itinerary] togglePublic failed:', error);
    return { success: false, data: null, message: error.message || 'Failed to toggle itinerary visibility' };
  }
};

export const fetchPublicItinerary = async (id) => {
  try {
    const { data, error } = await supabase
      .from('itinerary')
      .select('*')
      .eq('id', id)
      .eq('is_public', true)
      .limit(1);

    if (error) throw error;

    const itinerary = data?.length ? normalizeItineraryFromRow(data[0]) : null;
    return { success: true, data: itinerary, message: itinerary ? 'Public itinerary retrieved' : 'Not found' };
  } catch (error) {
    console.error('[Supabase Itinerary] fetchPublicItinerary failed:', error);
    return { success: false, data: null, message: error.message || 'Failed to fetch public itinerary' };
  }
};

export const addRecentlyViewed = async (destination) => {
  try {
    const user = await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      return { success: true, message: 'No active session', data: null };
    }

    const value = String(destination || '').trim();

    if (!value) {
      throw new Error('destination is required');
    }

    const { error } = await supabase
      .from('recently_viewed')
      .insert({
        user_id: user.id,
        destination: value,
      });

    if (error) throw error;

    return { success: true, message: 'Recently viewed destination added', data: null };
  } catch (error) {
    console.error('[Supabase Recently Viewed] addRecentlyViewed failed:', error);
    return { success: false, data: null, message: error.message || 'Failed to save recently viewed destination' };
  }
};

export const fetchRecentlyViewed = async () => {
  try {
    const user = await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      return { success: true, data: [], message: 'No active session' };
    }

    const { data, error } = await supabase
      .from('recently_viewed')
      .select('*')
      .eq('user_id', user.id)
      .order('viewed_at', { ascending: false })
      .limit(10);

    if (error) throw error;

    return { success: true, data: data || [], message: 'Recently viewed list retrieved' };
  } catch (error) {
    console.error('[Supabase Recently Viewed] fetchRecentlyViewed failed:', error);
    return { success: false, data: [], message: error.message || 'Failed to fetch recently viewed data' };
  }
};

export const updateLastLogin = async (userIdParam = null) => {
  try {
    const user = userIdParam ? { id: userIdParam } : await getAuthenticatedUser({ allowMissingSession: true });
    if (!user?.id) {
      return { success: true, message: 'No active session', data: null };
    }

    const userId = user.id;

    const { error } = await supabase
      .from('user_metadata')
      .upsert(
        {
          user_id: userId,
          last_login: new Date().toISOString(),
        },
        { onConflict: 'user_id' }
      );

    if (error) throw error;

    return { success: true, message: 'Last login updated', data: null };
  } catch (error) {
    console.error('[Supabase User Metadata] updateLastLogin failed:', error);
    return { success: false, data: null, message: error.message || 'Failed to update last login' };
  }
};

export const initializeUser = async () => {
  try {
    const { data, error } = await supabase.auth.getSession();
    if (error) throw error;

    const session = data?.session;
    if (!session?.user) {
      setAuthStorage(null);
      setCachedState({ user: null, wishlist: [], itineraries: [] });
      return { success: true, session: null, wishlist: [], itineraries: [] };
    }

    const user = session.user;
    setAuthStorage(user);

    const [wishlistResult, itinerariesResult] = await Promise.all([
      fetchWishlist(user.id),
      fetchItineraries(user.id),
      updateLastLogin(user.id),
    ]);

    setCachedState({
      user,
      wishlist: wishlistResult.data || [],
      itineraries: itinerariesResult.data || [],
    });

    return {
      success: true,
      session,
      user,
      wishlist: wishlistResult.data || [],
      itineraries: itinerariesResult.data || [],
    };
  } catch (error) {
    console.error('[Supabase Auth] initializeUser failed:', error);
    return {
      success: false,
      session: null,
      user: null,
      wishlist: [],
      itineraries: [],
      message: error.message || 'Failed to initialize user session',
    };
  }
};

export const onAuthStateChange = (callback) => {
  const { data } = supabase.auth.onAuthStateChange(async (event, session) => {
    if (event === 'SIGNED_OUT' || !session?.user) {
      setAuthStorage(null);
      setCachedState({ user: null, wishlist: [], itineraries: [] });
      callback?.(event, session, { user: null, wishlist: [], itineraries: [] });
      return;
    }

    const initialized = await initializeUser();
    callback?.(event, session, initialized);
  });

  return data?.subscription;
};

export const signUp = async ({ email, password, metadata = {} }) => {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: metadata },
    });

    if (error) throw error;
    return { success: true, data, message: 'Sign-up successful' };
  } catch (error) {
    return { success: false, data: null, message: error.message || 'Sign-up failed' };
  }
};

export const signIn = async ({ email, password }) => {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;

    await initializeUser();
    return { success: true, data, message: 'Login successful' };
  } catch (error) {
    return { success: false, data: null, message: error.message || 'Login failed' };
  }
};

export const signOut = async () => {
  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;

    setAuthStorage(null);
    setCachedState({ user: null, wishlist: [], itineraries: [] });
    return { success: true, message: 'Logout successful' };
  } catch (error) {
    return { success: false, message: error.message || 'Logout failed' };
  }
};

export const getCurrentUser = async () => {
  const { data, error } = await supabase.auth.getUser();
  if (error) return null;
  return data?.user || null;
};

export const getCurrentSession = async () => {
  const { data, error } = await supabase.auth.getSession();
  if (error) return null;
  return data?.session || null;
};
