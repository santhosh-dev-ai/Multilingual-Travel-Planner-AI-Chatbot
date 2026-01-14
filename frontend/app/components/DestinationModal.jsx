'use client';

import { Fragment, useState } from 'react';
import {
  XMarkIcon,
  MapPinIcon,
  StarIcon,
  ClockIcon,
  CalendarIcon,
  SunIcon,
  CurrencyDollarIcon,
  HeartIcon,
  ShareIcon,
  CheckCircleIcon,
  CalendarDaysIcon,
  CheckBadgeIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon, StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';
import WeatherWidget from './WeatherWidget';

export default function DestinationModal({
  destination,
  isOpen,
  onClose,
  onAskAI,
  onToggleWishlist,
  isInWishlist,
  translations,
  onBuildItinerary,
  hasItinerary = false,
}) {
  const [showItineraryAlert, setShowItineraryAlert] = useState(false);
  if (!isOpen || !destination) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `TravelGenie - ${destination.name}`,
          text: `Check out ${destination.name}, ${destination.country}!`,
          url: window.location.href,
        });
      } catch (err) {
        console.log('Share cancelled');
      }
    } else {
      // Fallback - copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden bg-(--color-surface) dark:bg-(--color-dark-surface) rounded-2xl shadow-2xl animate-slideUp">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
        >
          <XMarkIcon className="w-6 h-6" />
        </button>

        <div className="overflow-y-auto max-h-[90vh]">
          {/* Hero Image */}
          <div className="relative h-64 md:h-80">
            <img
              src={destination.image}
              alt={destination.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
            
            {/* Badge */}
            {destination.badge && (
              <div className="absolute top-4 left-4 px-3 py-1 bg-(--color-accent) text-white text-sm font-semibold rounded-full">
                {destination.badge}
              </div>
            )}

            {/* Title Overlay */}
            <div className="absolute bottom-0 left-0 right-0 p-6">
              <div className="flex items-center gap-2 text-white/80 mb-2">
                <MapPinIcon className="w-5 h-5" />
                <span>{destination.country}</span>
              </div>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">
                {destination.name}
              </h2>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <StarSolidIcon className="w-5 h-5 text-yellow-400" />
                  <span className="text-white font-semibold">{destination.rating}</span>
                  <span className="text-white/70">({destination.reviews} reviews)</span>
                </div>
                <div className="flex items-center gap-1 text-white/80">
                  <ClockIcon className="w-5 h-5" />
                  <span>{destination.duration}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 mb-6">
              <button
                onClick={() => onToggleWishlist(destination)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                  isInWishlist
                    ? 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700 text-red-600 dark:text-red-400'
                    : 'bg-(--color-background-secondary) border-(--color-border) text-(--color-text-secondary) hover:border-(--color-primary)'
                }`}
              >
                {isInWishlist ? (
                  <HeartSolidIcon className="w-5 h-5 text-red-500" />
                ) : (
                  <HeartIcon className="w-5 h-5" />
                )}
                <span>{isInWishlist ? 'Saved' : 'Save'}</span>
              </button>
              
              {onBuildItinerary && (
                <button
                  onClick={() => onBuildItinerary(destination)}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all"
                >
                  <CalendarDaysIcon className="w-5 h-5" />
                  <span>Build Itinerary</span>
                </button>
              )}

              <button
                onClick={handleShare}
                className="flex items-center gap-2 px-4 py-2 bg-(--color-background-secondary) border border-(--color-border) text-(--color-text-secondary) rounded-lg hover:border-(--color-primary) transition-all"
              >
                <ShareIcon className="w-5 h-5" />
                <span>Share</span>
              </button>
            </div>

            {/* Description */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-(--color-text-primary) mb-2">About</h3>
              <p className="text-(--color-text-secondary) leading-relaxed">
                {destination.fullDescription || destination.description}
              </p>
            </div>

            {/* Quick Info Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) rounded-xl">
                <div className="flex items-center gap-2 text-(--color-primary) mb-1">
                  <CalendarIcon className="w-5 h-5" />
                  <span className="text-sm font-medium">Best Time</span>
                </div>
                <p className="text-(--color-text-primary) font-semibold">
                  {destination.bestTimeToVisit || 'Year-round'}
                </p>
              </div>
              
              <div className="p-4 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) rounded-xl">
                <div className="flex items-center gap-2 text-(--color-primary) mb-1">
                  <SunIcon className="w-5 h-5" />
                  <span className="text-sm font-medium">Climate</span>
                </div>
                <p className="text-(--color-text-primary) font-semibold">
                  {destination.climate || 'Varied'}
                </p>
              </div>
              
              <div className="p-4 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) rounded-xl">
                <div className="flex items-center gap-2 text-(--color-primary) mb-1">
                  <CurrencyDollarIcon className="w-5 h-5" />
                  <span className="text-sm font-medium">Starting From</span>
                </div>
                <p className="text-(--color-text-primary) font-semibold">{destination.price}</p>
              </div>
              
              <div className="p-4 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) rounded-xl">
                <div className="flex items-center gap-2 text-(--color-primary) mb-1">
                  <ClockIcon className="w-5 h-5" />
                  <span className="text-sm font-medium">Duration</span>
                </div>
                <p className="text-(--color-text-primary) font-semibold">{destination.duration}</p>
              </div>
            </div>

            {/* Highlights */}
            {destination.highlights && destination.highlights.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-(--color-text-primary) mb-3">Highlights</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {destination.highlights.map((highlight, index) => (
                    <div key={index} className="flex items-center gap-2 text-(--color-text-secondary)">
                      <CheckCircleIcon className="w-5 h-5 text-(--color-primary) flex-shrink-0" />
                      <span>{highlight}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tags */}
            {destination.tags && destination.tags.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-(--color-text-primary) mb-3">Trip Type</h3>
                <div className="flex flex-wrap gap-2">
                  {destination.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-(--color-primary-50) dark:bg-(--color-primary)/20 text-(--color-primary) text-sm rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Weather Widget */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-(--color-text-primary) mb-3">Current Weather</h3>
              <WeatherWidget 
                destination={destination.name} 
                coordinates={destination.coordinates}
              />
            </div>

            {/* Itinerary Alert */}
            {showItineraryAlert && !hasItinerary && (
              <div className="mb-4 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-xl animate-slideDown">
                <div className="flex items-start gap-3">
                  <CalendarDaysIcon className="w-6 h-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-amber-800 dark:text-amber-300 mb-1">
                      Build Your Itinerary First!
                    </h4>
                    <p className="text-sm text-amber-700 dark:text-amber-400 mb-3">
                      Create a personalized itinerary before planning your trip. This helps you organize your activities and make the most of your visit to {destination.name}.
                    </p>
                    <button
                      onClick={() => {
                        setShowItineraryAlert(false);
                        onBuildItinerary(destination);
                      }}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium rounded-lg transition-colors"
                    >
                      <CalendarDaysIcon className="w-4 h-4" />
                      Build Itinerary Now
                    </button>
                  </div>
                  <button
                    onClick={() => setShowItineraryAlert(false)}
                    className="text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-200"
                  >
                    <XMarkIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}

            {/* Itinerary Ready Status */}
            {hasItinerary && (
              <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl">
                <div className="flex items-center gap-3">
                  <CheckBadgeIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
                  <div>
                    <h4 className="font-semibold text-green-800 dark:text-green-300">
                      Itinerary Ready!
                    </h4>
                    <p className="text-sm text-green-700 dark:text-green-400">
                      Your personalized itinerary for {destination.name} is ready. You can now proceed with your trip!
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* CTA */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-(--color-border)">
              <button
                onClick={() => {
                  if (hasItinerary) {
                    // Proceed to next phase - open booking or trip details
                    onAskAI(destination);
                  } else {
                    // Show alert to build itinerary first
                    setShowItineraryAlert(true);
                  }
                }}
                className={`flex-1 py-3 font-semibold rounded-xl transition-all flex items-center justify-center gap-2 ${
                  hasItinerary
                    ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-lg'
                    : 'bg-gradient-to-r from-(--color-primary) to-(--color-secondary) text-white hover:shadow-lg'
                }`}
              >
                {hasItinerary ? (
                  <>
                    <ArrowRightIcon className="w-5 h-5" />
                    Continue to Trip Details
                  </>
                ) : (
                  <>Plan My Trip to {destination.name}</>
                )}
              </button>
              <button
                onClick={onClose}
                className="px-6 py-3 border border-(--color-border) text-(--color-text-secondary) rounded-xl hover:bg-(--color-background-secondary) transition-all"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
