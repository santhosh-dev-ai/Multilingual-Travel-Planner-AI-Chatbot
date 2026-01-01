'use client';

import { MapPinIcon, StarIcon, ClockIcon } from '@heroicons/react/24/solid';
import { HeartIcon } from '@heroicons/react/24/outline';
import { useState } from 'react';

export default function DestinationCard({ destination, translations }) {
  const [isFavorite, setIsFavorite] = useState(false);

  const handleExplore = () => {
    const ctaSection = document.getElementById('cta-section');
    if (ctaSection) {
      ctaSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="card group overflow-hidden hover:scale-[1.02] transition-transform duration-300">
      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        <img
          src={destination.image}
          alt={destination.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        
        {/* Favorite Button */}
        <button
          onClick={() => setIsFavorite(!isFavorite)}
          className="absolute top-3 right-3 p-2 bg-white/90 backdrop-blur-sm rounded-full hover:bg-white transition-all duration-200"
        >
          <HeartIcon className={`w-5 h-5 ${isFavorite ? 'fill-red-500 text-red-500' : 'text-(--color-text-secondary)'}`} />
        </button>

        {/* Badge */}
        {destination.badge && (
          <div className="absolute top-3 left-3 px-3 py-1 bg-(--color-accent) text-white text-xs font-semibold rounded-full">
            {destination.badge}
          </div>
        )}

        {/* Location */}
        <div className="absolute bottom-3 left-3 flex items-center gap-1 text-white">
          <MapPinIcon className="w-4 h-4" />
          <span className="text-sm font-medium">{destination.country}</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="text-lg font-bold text-(--color-text-primary) mb-1">{destination.name}</h3>
        <p className="text-sm text-(--color-text-secondary) mb-3 line-clamp-2">{destination.description}</p>

        {/* Stats */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-1">
            <StarIcon className="w-4 h-4 text-yellow-500" />
            <span className="text-sm font-semibold text-(--color-text-primary)">{destination.rating}</span>
            <span className="text-xs text-(--color-text-tertiary)">({destination.reviews})</span>
          </div>
          <div className="flex items-center gap-1">
            <ClockIcon className="w-4 h-4 text-(--color-primary)" />
            <span className="text-sm text-(--color-text-secondary)">{destination.duration}</span>
          </div>
        </div>

        {/* Price & CTA */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-(--color-text-tertiary)">{translations?.startingFrom || 'Starting from'}</p>
            <p className="text-xl font-bold text-(--color-primary)">{destination.price}</p>
          </div>
          <button 
            onClick={handleExplore}
            className="px-4 py-2 bg-gradient-to-r from-(--color-primary) to-(--color-secondary) text-white text-sm font-semibold rounded-lg hover:shadow-lg transition-all duration-200 active:scale-95"
          >
            {translations?.explore || 'Explore'}
          </button>
        </div>
      </div>
    </div>
  );
}