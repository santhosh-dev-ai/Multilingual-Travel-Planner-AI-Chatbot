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
        }
        setError(null);
      } catch (e) {
        console.error('Failed to load wishlist from database:', e);
        setError(e.message);
        // Fallback to localStorage
        const saved = localStorage.getItem('travelgenie-wishlist');
        if (saved) {
          try {
            setWishlist(JSON.parse(saved));
          } catch (parseError) {
            setWishlist([]);
          }
        }
      } finally {
        setIsLoading(false);
        setIsLoaded(true);
      }
    };

    loadWishlist();
  }, []);

  // Also save to localStorage as backup
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem('travelgenie-wishlist', JSON.stringify(wishlist));
    }
  }, [wishlist, isLoaded]);

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
    } catch (e) {
      console.error('Failed to add to wishlist:', e);
      // Revert on error
      setWishlist(prev => prev.filter(d => d.id !== destination.id));
    }
  }, []);

  const removeFromWishlist = useCallback(async (destinationId) => {
    // Store the item for potential rollback
    const itemToRemove = wishlist.find(d => d.id === destinationId);
    
    // Optimistic update
    setWishlist(prev => prev.filter(d => d.id !== destinationId));

    try {
      await wishlistAPI.removeFromWishlist(destinationId);
    } catch (e) {
      console.error('Failed to remove from wishlist:', e);
      // Revert on error
      if (itemToRemove) {
        setWishlist(prev => [...prev, itemToRemove]);
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
    } catch (e) {
      console.error('Failed to clear wishlist:', e);
      // Revert on error
      setWishlist(previousWishlist);
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
      }
    } catch (e) {
      console.error('Failed to refresh wishlist:', e);
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
