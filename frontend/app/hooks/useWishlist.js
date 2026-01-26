'use client';

import { useState, useEffect, useCallback } from 'react';
import { wishlistAPI, chatAPI } from '../services/api';

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
          // Transform database items to full destination objects
          const fullDestinations = response.data.map(item => ({
            id: item.destination_id,
            name: item.destination_name,
            country: item.destination_country,
            image: item.destination_image,
            price: item.destination_price,
            rating: item.destination_rating,
            reviews: 100, // Default value
            duration: '7-10 days', // Default value
            description: `Amazing destination in ${item.destination_country}`, // Default value
            tags: ['culture', 'adventure'], // Default value
            educational_notes: `This destination offers great learning opportunities for students interested in cultural exploration and adventure.`
          }));
          setWishlist(fullDestinations);
        } else {
          setWishlist([]);
        }
        setError(null);
      } catch (e) {
        console.error('Failed to load wishlist from database:', e.message);
        setError(`Failed to load wishlist: ${e.message}`);
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
    const newWishlist = [...wishlist];
    if (!newWishlist.find(d => d.id === destination.id)) {
      newWishlist.push({
        ...destination,
        educational_notes: `This destination offers great learning opportunities for students interested in ${destination.tags?.join(', ') || 'cultural exploration'}.`
      });
      setWishlist(newWishlist);
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
      setError(`Failed to add to wishlist: ${e.message}`);
      // Revert optimistic update on error
      setWishlist(prev => prev.filter(d => d.id !== destination.id));
    }
  }, [wishlist]);

  const removeFromWishlist = useCallback(async (destinationId) => {
    // Store the item for potential rollback
    const itemToRemove = wishlist.find(d => d.id === destinationId);

    // Optimistic update
    const newWishlist = wishlist.filter(d => d.id !== destinationId);
    setWishlist(newWishlist);

    try {
      // Remove from database
      const response = await wishlistAPI.removeFromWishlist(destinationId);
      if (!response.success) {
        throw new Error(response.message || 'Failed to remove from wishlist');
      }

      setError(null);
    } catch (e) {
      console.error('Failed to remove from wishlist:', e.message);
      setError(`Failed to remove from wishlist: ${e.message}`);
      // Revert optimistic update on error
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
      // Clear from database
      const response = await wishlistAPI.clearWishlist();
      if (!response.success) {
        throw new Error(response.message || 'Failed to clear wishlist');
      }

      setError(null);
    } catch (e) {
      console.error('Failed to clear wishlist:', e.message);
      setError(`Failed to clear wishlist: ${e.message}`);
      // Revert optimistic update on error
      setWishlist(previousWishlist);
    }
  }, [wishlist]);

  const refreshWishlist = useCallback(async () => {
    setIsLoading(true);
    try {
      // Refresh from database
      const response = await wishlistAPI.getWishlist();
      if (response.success && response.data) {
        // Transform database items to full destination objects
        const fullDestinations = response.data.map(item => ({
          id: item.destination_id,
          name: item.destination_name,
          country: item.destination_country,
          image: item.destination_image,
          price: item.destination_price,
          rating: item.destination_rating,
          reviews: 100, // Default value
          duration: '7-10 days', // Default value
          description: `Amazing destination in ${item.destination_country}`, // Default value
          tags: ['culture', 'adventure'], // Default value
          educational_notes: `This destination offers great learning opportunities for students interested in cultural exploration and adventure.`
        }));
        setWishlist(fullDestinations);
      } else {
        setWishlist([]);
      }

      setError(null);
    } catch (e) {
      console.error('Failed to refresh wishlist:', e.message);
      setError(`Failed to refresh wishlist: ${e.message}`);
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
