'use client';

import { XMarkIcon, MapPinIcon, StarIcon, ClockIcon, TrashIcon } from '@heroicons/react/24/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';

export default function CompareDestinations({
  destinations,
  compareList,
  onRemoveFromCompare,
  onClearCompare,
  onAskAI,
  isOpen,
  onClose,
}) {
  if (!isOpen) return null;

  const compareDestinations = destinations.filter(d => compareList.includes(d.id));

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleAskAIToCompare = () => {
    const names = compareDestinations.map(d => d.name).join(', ');
    onAskAI(`Compare these destinations for me: ${names}. Which one would you recommend and why?`);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-6xl max-h-[90vh] overflow-hidden bg-(--color-surface) dark:bg-(--color-dark-surface) rounded-2xl shadow-2xl animate-slideUp">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-(--color-border)">
          <h2 className="text-xl font-bold text-(--color-text-primary)">
            Compare Destinations ({compareDestinations.length})
          </h2>
          <div className="flex items-center gap-2">
            {compareDestinations.length > 0 && (
              <button
                onClick={onClearCompare}
                className="flex items-center gap-1 px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
              >
                <TrashIcon className="w-4 h-4" />
                Clear All
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-(--color-background-secondary) rounded-full transition-colors"
            >
              <XMarkIcon className="w-6 h-6 text-(--color-text-secondary)" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-x-auto p-4">
          {compareDestinations.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-(--color-text-secondary) mb-2">No destinations to compare</p>
              <p className="text-sm text-(--color-text-tertiary)">
                Click the compare checkbox on destination cards to add them here
              </p>
            </div>
          ) : (
            <div className="min-w-max">
              {/* Comparison Grid */}
              <div className="grid gap-4" style={{ gridTemplateColumns: `200px repeat(${compareDestinations.length}, minmax(250px, 1fr))` }}>
                {/* Row Labels */}
                <div className="space-y-4">
                  <div className="h-48"></div>
                  <div className="py-3 font-semibold text-(--color-text-secondary)">Location</div>
                  <div className="py-3 font-semibold text-(--color-text-secondary)">Rating</div>
                  <div className="py-3 font-semibold text-(--color-text-secondary)">Duration</div>
                  <div className="py-3 font-semibold text-(--color-text-secondary)">Price</div>
                  <div className="py-3 font-semibold text-(--color-text-secondary)">Best Time</div>
                  <div className="py-3 font-semibold text-(--color-text-secondary)">Climate</div>
                  <div className="py-3 font-semibold text-(--color-text-secondary)">Trip Type</div>
                </div>

                {/* Destination Columns */}
                {compareDestinations.map((destination) => (
                  <div key={destination.id} className="space-y-4">
                    {/* Image & Name */}
                    <div className="relative h-48 rounded-xl overflow-hidden group">
                      <img
                        src={destination.image}
                        alt={destination.name}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
                      <button
                        onClick={() => onRemoveFromCompare(destination.id)}
                        className="absolute top-2 right-2 p-1.5 bg-black/50 hover:bg-red-500 rounded-full text-white transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <XMarkIcon className="w-4 h-4" />
                      </button>
                      <div className="absolute bottom-3 left-3 right-3">
                        <h3 className="text-lg font-bold text-white">{destination.name}</h3>
                      </div>
                    </div>

                    {/* Location */}
                    <div className="py-3 flex items-center gap-2 text-(--color-text-primary)">
                      <MapPinIcon className="w-5 h-5 text-(--color-primary)" />
                      {destination.country}
                    </div>

                    {/* Rating */}
                    <div className="py-3 flex items-center gap-2 text-(--color-text-primary)">
                      <StarSolidIcon className="w-5 h-5 text-yellow-500" />
                      {destination.rating} ({destination.reviews} reviews)
                    </div>

                    {/* Duration */}
                    <div className="py-3 flex items-center gap-2 text-(--color-text-primary)">
                      <ClockIcon className="w-5 h-5 text-(--color-primary)" />
                      {destination.duration}
                    </div>

                    {/* Price */}
                    <div className="py-3">
                      <span className="text-xl font-bold text-(--color-primary)">{destination.price}</span>
                    </div>

                    {/* Best Time */}
                    <div className="py-3 text-(--color-text-primary)">
                      {destination.bestTimeToVisit || 'Year-round'}
                    </div>

                    {/* Climate */}
                    <div className="py-3 text-(--color-text-primary)">
                      {destination.climate || 'Varied'}
                    </div>

                    {/* Trip Type */}
                    <div className="py-3">
                      <div className="flex flex-wrap gap-1">
                        {(destination.tags || ['Travel']).slice(0, 2).map((tag, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 bg-(--color-primary-50) dark:bg-(--color-primary)/20 text-(--color-primary) text-xs rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {compareDestinations.length > 0 && (
          <div className="p-4 border-t border-(--color-border) bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary)">
            <button
              onClick={handleAskAIToCompare}
              className="w-full py-3 bg-gradient-to-r from-(--color-primary) to-(--color-secondary) text-white font-semibold rounded-xl hover:shadow-lg transition-all"
            >
              Ask AI to Help Me Choose
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
