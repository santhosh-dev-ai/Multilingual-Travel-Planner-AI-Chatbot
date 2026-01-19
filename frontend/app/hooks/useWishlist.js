'use client';

import { useState, useEffect, useCallback } from 'react';
import { wishlistAPI } from '../services/api';

export function useWishlist() {
  const [wishlist, setWishlist] = useState([]); // Array of full destination objects
  const [isLoaded, setIsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load wishlist from database on mount
  useEffect(() => {
    const loadWishlist = async () => {
      setIsLoading(true);
      try {
        const response = await wishlistAPI.getWishlist();
        if (response.success && response.data) {
          // Transform database format to frontend format
          const items = response.data.map(item => ({
            id: item.destination_id,
            name: item.destination_name,
            country: item.destination_country,
            image: item.destination_image,
            price: item.destination_price,
            rating: item.destination_rating,
            wishlistId: item.id, // Keep the database ID for deletion
          }));
          setWishlist(items);
          setError(null);
        } else {
          // Empty wishlist response
          setWishlist([]);
          setError(null);
        }
      } catch (e) {
        // For network errors (server not running), don't set error state - just log a warning
        // This prevents error messages from showing when the server is intentionally not running
        if (e.isNetworkError || e.name === 'NetworkError') {
          // Only log to console, don't set error state for initial load
          // This way the app works normally even if database server isn't running
          console.debug('Database API server is not running. Wishlist features will be unavailable until the server is started.');
        } else {
          // Only set error for actual failures, not network errors
          console.error('Failed to load wishlist from database:', e.message);
          setError(`Failed to load wishlist: ${e.message}`);
        }
        
        // Set empty wishlist on error
        setWishlist([]);
      } finally {
        setIsLoading(false);
        setIsLoaded(true);
      }
    };

    loadWishlist();
  }, []);

  const addToWishlist = useCallback(async (destination) => {
    // Optimistic update
    setWishlist(prev => {
      if (!prev.find(d => d.id === destination.id)) {
        return [...prev, destination];
      }
      return prev;
    });

    try {
      await wishlistAPI.addToWishlist(destination);
      setError(null);
    } catch (e) {
      // Revert on error
      setWishlist(prev => prev.filter(d => d.id !== destination.id));
      
      // Set error message only for non-network errors
      if (e.isNetworkError || e.name === 'NetworkError') {
        console.warn('Database service unavailable. Please start the database API server to save wishlist items.');
        // Don't set error state for network errors - user can still use the app
      } else {
        console.error('Failed to add to wishlist:', e.message);
        setError(`Failed to add to wishlist: ${e.message}`);
      }
    }
  }, []);

  const removeFromWishlist = useCallback(async (destinationId) => {
    // Store the item for potential rollback
    const itemToRemove = wishlist.find(d => d.id === destinationId);
    
    // Optimistic update
    setWishlist(prev => prev.filter(d => d.id !== destinationId));

    try {
      await wishlistAPI.removeFromWishlist(destinationId);
      setError(null);
    } catch (e) {
      // Revert on error
      if (itemToRemove) {
        setWishlist(prev => [...prev, itemToRemove]);
      }
      
      // Set error message only for non-network errors
      if (e.isNetworkError || e.name === 'NetworkError') {
        console.warn('Database service unavailable. Please start the database API server to manage wishlist items.');
        // Don't set error state for network errors
      } else {
        console.error('Failed to remove from wishlist:', e.message);
        setError(`Failed to remove from wishlist: ${e.message}`);
      }
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

    try {
      await wishlistAPI.clearWishlist();
      setError(null);
    } catch (e) {
      // Revert on error
      setWishlist(previousWishlist);
      
      // Set error message only for non-network errors
      if (e.isNetworkError || e.name === 'NetworkError') {
        console.warn('Database service unavailable. Please start the database API server to manage wishlist items.');
        // Don't set error state for network errors
      } else {
        console.error('Failed to clear wishlist:', e.message);
        setError(`Failed to clear wishlist: ${e.message}`);
      }
    }
  }, [wishlist]);

  const refreshWishlist = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await wishlistAPI.getWishlist();
      if (response.success && response.data) {
        const items = response.data.map(item => ({
          id: item.destination_id,
          name: item.destination_name,
          country: item.destination_country,
          image: item.destination_image,
          price: item.destination_price,
          rating: item.destination_rating,
          wishlistId: item.id,
        }));
        setWishlist(items);
        setError(null);
      } else {
        setWishlist([]);
        setError(null);
      }
    } catch (e) {
      // For network errors, don't set error state
      if (e.isNetworkError || e.name === 'NetworkError') {
        console.debug('Database API server is not running. Wishlist refresh unavailable.');
        // Don't set error state for network errors
      } else {
        console.error('Failed to refresh wishlist:', e.message);
        setError(`Failed to refresh wishlist: ${e.message}`);
      }
      // Set empty wishlist on error
      setWishlist([]);
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
