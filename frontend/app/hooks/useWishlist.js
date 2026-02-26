'use client';

import { useState, useEffect, useCallback } from 'react';
import { wishlistAPI, chatAPI, authAPI } from '../services/api';

const WISHLIST_LOCAL_KEY = 'travelgenie-local-wishlist';

const normalizeDestination = (destination) => ({
  ...destination,
  educational_notes:
    destination.educational_notes ||
    `This destination offers great learning opportunities for students interested in ${destination.tags?.join(', ') || 'cultural exploration'}.`,
});

const mapDatabaseWishlist = (items = []) =>
  items.map(item => ({
    id: item.destination_id || item.id,
    wishlist_row_id: item.wishlist_row_id || item.id,
    name: item.destination_name || item.place_name || 'Unknown Destination',
    country: item.destination_country || 'Unknown',
    image: item.destination_image || 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80',
    price: item.destination_price || '$299',
    rating: item.destination_rating || 4.5,
    reviews: 100,
    duration: '7-10 days',
    description: `Amazing destination in ${item.destination_country}`,
    tags: ['culture', 'adventure'],
    educational_notes: `This destination offers great learning opportunities for students interested in cultural exploration and adventure.`
  }));

const loadLocalWishlist = () => {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(WISHLIST_LOCAL_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    return [];
  }
};

const saveLocalWishlist = (items) => {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(WISHLIST_LOCAL_KEY, JSON.stringify(items));
  } catch (error) {
    console.warn('Could not persist wishlist locally:', error);
  }
};

export function useWishlist() {
  const [wishlist, setWishlist] = useState([]); // Array of full destination objects
  const [isLoaded, setIsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load wishlist from database on mount
  useEffect(() => {
    const loadWishlist = async () => {
      setIsLoading(true);

      const localWishlist = loadLocalWishlist();
      if (localWishlist.length > 0) {
        setWishlist(localWishlist);
      }

      try {
        const response = await wishlistAPI.getWishlist();
        if (response.success && response.data) {
          const fullDestinations = mapDatabaseWishlist(response.data);
          setWishlist(fullDestinations);
          saveLocalWishlist(fullDestinations);
        } else {
          setWishlist(localWishlist);
        }
        setError(null);
      } catch (e) {
        console.error('Failed to load wishlist from database:', e.message);
        setError('Wishlist sync issue: using local saved wishlist.');
        setWishlist(localWishlist);
      } finally {
        setIsLoading(false);
        setIsLoaded(true);
      }
    };

    loadWishlist();

    const unsubscribe = authAPI.onAuthStateChange(async (_event, _session, payload) => {
      if (!payload?.user) {
        setWishlist([]);
        setError(null);
        setIsLoaded(true);
        return;
      }

      await loadWishlist();
    });

    return () => {
      unsubscribe?.();
    };
  }, []);

  const addToWishlist = useCallback(async (destination) => {
    // Optimistic update
    const newWishlist = [...wishlist];
    if (!newWishlist.find(d => d.id === destination.id)) {
      newWishlist.push(normalizeDestination(destination));
      setWishlist(newWishlist);
      saveLocalWishlist(newWishlist);
    }

    try {
      // Save to database
      const response = await wishlistAPI.addToWishlist(destination);
      if (!response.success) {
        throw new Error(response.message || 'Failed to add to wishlist');
      }

      setError(null);
    } catch (e) {
      console.error('Failed to add to wishlist:', e.message);
      setError('Saved locally. Cloud sync will retry when connection is stable.');
    }
  }, [wishlist]);

  const removeFromWishlist = useCallback(async (destinationId) => {
    // Store the item for potential rollback
    const itemToRemove = wishlist.find(d => d.id === destinationId);

    // Optimistic update
    const newWishlist = wishlist.filter(d => d.id !== destinationId);
    setWishlist(newWishlist);
    saveLocalWishlist(newWishlist);

    try {
      // Remove from database
      const identifier = itemToRemove?.wishlist_row_id || itemToRemove?.name || destinationId;
      const response = await wishlistAPI.removeFromWishlist(identifier);
      if (!response.success) {
        throw new Error(response.message || 'Failed to remove from wishlist');
      }

      setError(null);
    } catch (e) {
      console.error('Failed to remove from wishlist:', e.message);
      setError('Removed locally. Cloud sync will retry when connection is stable.');
    }
  }, [wishlist]);

  const toggleWishlist = useCallback(async (destination) => {
    if (isInWishlist(destination.id)) {
      await removeFromWishlist(destination.id);
    } else {
      await addToWishlist(destination);
    }
  }, [addToWishlist, removeFromWishlist]);

  const isInWishlist = useCallback((destinationId) => {
    return wishlist.some(d => d.id === destinationId);
  }, [wishlist]);

  const clearWishlist = useCallback(async () => {
    const previousWishlist = [...wishlist];
    setWishlist([]);
    saveLocalWishlist([]);

    try {
      // Clear from database
      const response = await wishlistAPI.clearWishlist();
      if (!response.success) {
        throw new Error(response.message || 'Failed to clear wishlist');
      }

      setError(null);
    } catch (e) {
      console.error('Failed to clear wishlist:', e.message);
      setError('Wishlist cleared locally. Cloud sync will retry when connection is stable.');
      // Revert optimistic update on error
      setWishlist(previousWishlist);
      saveLocalWishlist(previousWishlist);
    }
  }, [wishlist]);

  const refreshWishlist = useCallback(async () => {
    setIsLoading(true);
    try {
      // Refresh from database
      const response = await wishlistAPI.getWishlist();
      if (response.success && response.data) {
        const fullDestinations = mapDatabaseWishlist(response.data);
        setWishlist(fullDestinations);
        saveLocalWishlist(fullDestinations);
      } else {
        const localWishlist = loadLocalWishlist();
        setWishlist(localWishlist);
      }

      setError(null);
    } catch (e) {
      console.error('Failed to refresh wishlist:', e.message);
      setError('Using local wishlist due to temporary sync issue.');
      setWishlist(loadLocalWishlist());
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    wishlist,
    isLoaded,
    isLoading,
    error,
    addToWishlist,
    removeFromWishlist,
    toggleWishlist,
    isInWishlist,
    clearWishlist,
    refreshWishlist,
  };
}
