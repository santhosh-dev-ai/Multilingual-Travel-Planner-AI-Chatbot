'use client';

import { MapPinIcon, StarIcon, ClockIcon } from '@heroicons/react/24/solid';
import { HeartIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

export default function DestinationCard({ 
  destination, 
  translations,
  isInWishlist,
  onToggleWishlist,
  onExplore,
  onAskAI,
  isInCompare,
  onToggleCompare,
  showCompare = true,
}) {
  return (
    <div className="bg-[#1E293B] rounded-xl border border-[#334155] shadow-sm hover:shadow-md transition-shadow duration-200 group overflow-hidden hover:scale-[1.02] transition-transform duration-300 relative">
      {/* Compare Checkbox */}
      {showCompare && (
        <div className="absolute top-3 left-3 z-10">
          {destination.badge ? (
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-1 px-2 py-1 bg-black/50 backdrop-blur-sm rounded-full cursor-pointer">
                <input
                  type="checkbox"
                  checked={isInCompare}
                  onChange={() => onToggleCompare(destination.id)}
                  className="w-4 h-4 rounded border-white/50 text-[#3AA8C1] focus:ring-[#3AA8C1] cursor-pointer"
                />
                <span className="text-xs text-white">Compare</span>
              </label>
              <div className="px-3 py-1 bg-[#3AA8C1] text-white text-xs font-semibold rounded-full">
                {destination.badge}
              </div>
            </div>
          ) : (
            <label className="flex items-center gap-1 px-2 py-1 bg-black/50 backdrop-blur-sm rounded-full cursor-pointer">
              <input
                type="checkbox"
                checked={isInCompare}
                onChange={() => onToggleCompare(destination.id)}
                className="w-4 h-4 rounded border-white/50 text-[#3AA8C1] focus:ring-[#3AA8C1] cursor-pointer"
              />
              <span className="text-xs text-white">Compare</span>
            </label>
          )}
        </div>
      )}

      {/* Image */}
      <div className="relative h-48 overflow-hidden cursor-pointer" onClick={() => onExplore(destination)}>
        <img
          src={destination.image}
          alt={destination.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        
        {/* Favorite Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleWishlist(destination);
          }}
          className="absolute top-3 right-3 p-2 bg-white/90 backdrop-blur-sm rounded-full hover:bg-white transition-all duration-200 z-10"
        >
          {isInWishlist ? (
            <HeartSolidIcon className="w-5 h-5 text-red-500" />
          ) : (
            <HeartIcon className="w-5 h-5 text-[#64748B]" />
          )}
        </button>

        {/* Badge - only show if no compare checkbox with badge */}
        {destination.badge && !showCompare && (
          <div className="absolute top-3 left-3 px-3 py-1 bg-[#3AA8C1] text-white text-xs font-semibold rounded-full">
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
        <h3 className="text-lg font-bold text-white mb-1">{destination.name}</h3>
        <p className="text-sm text-[#CBD5E1] mb-3 line-clamp-2">{destination.description}</p>

        {/* Stats */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-1">
            <StarIcon className="w-4 h-4 text-yellow-500" />
            <span className="text-sm font-semibold text-white">{destination.rating}</span>
            <span className="text-xs text-[#94A3B8]">({destination.reviews})</span>
          </div>
          <div className="flex items-center gap-1">
            <ClockIcon className="w-4 h-4 text-[#3AA8C1]" />
            <span className="text-sm text-[#CBD5E1]">{destination.duration}</span>
          </div>
        </div>

        {/* Price & Actions */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-[#94A3B8]">{translations?.startingFrom || 'Starting from'}</p>
            <p className="text-xl font-bold text-[#3AA8C1]">{destination.price}</p>
          </div>
          <div className="flex items-center gap-2">
            {/* Ask AI Button */}
            <button 
              onClick={() => onAskAI(destination)}
              className="p-2 border border-[#334155] text-[#CBD5E1] rounded-lg hover:border-[#3AA8C1] hover:text-[#3AA8C1] transition-all duration-200"
              title="Ask AI about this destination"
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5" />
            </button>
            {/* Explore Button */}
            <button 
              onClick={() => onExplore(destination)}
              className="px-4 py-2 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white text-sm font-semibold rounded-lg hover:shadow-lg transition-all duration-200 active:scale-95"
            >
              {translations?.explore || 'Explore'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}