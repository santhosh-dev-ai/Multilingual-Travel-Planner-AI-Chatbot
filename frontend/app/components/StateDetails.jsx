'use client';

import { useMemo } from 'react';

function inferPlaceImage(placeName, category) {
  const query = encodeURIComponent(`${placeName} ${category || ''} india`);
  return `https://source.unsplash.com/1200x800/?${query}`;
}

export default function StateDetails({ stateName, data, loading, error }) {
  const places = useMemo(() => data?.popular_places || [], [data]);

  if (loading) {
    return (
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-[#1E293B] rounded-xl border border-[#334155] overflow-hidden animate-pulse">
            <div className="h-44 bg-[#334155]" />
            <div className="p-4 space-y-3">
              <div className="h-5 bg-[#334155] rounded w-2/3" />
              <div className="h-4 bg-[#334155] rounded w-1/2" />
              <div className="h-4 bg-[#334155] rounded w-full" />
              <div className="h-4 bg-[#334155] rounded w-5/6" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-14">
        <p className="text-red-400 font-medium mb-4">{error}</p>
      </div>
    );
  }

  return (
    <div className="animate-fadeIn">
      <div className="mb-8 bg-[#1E293B] border border-[#334155] rounded-2xl p-6">
        <h1 className="text-3xl font-bold text-white mb-3">{stateName}</h1>
        <p className="text-[#CBD5E1] leading-relaxed">{data?.overview || 'No overview available.'}</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {places.map((place, index) => {
          const image = inferPlaceImage(place.name, place.category);
          return (
            <div
              key={`${place.name}-${index}`}
              className="bg-[#1E293B] rounded-xl border border-[#334155] shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden group hover:scale-[1.02]"
            >
              <div className="relative h-44 overflow-hidden">
                <img
                  src={image}
                  alt={place.name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                <span className="absolute top-3 left-3 px-2.5 py-1 bg-[#3AA8C1] text-white text-xs font-semibold rounded-full">
                  {place.category}
                </span>
              </div>

              <div className="p-4">
                <h3 className="text-lg font-bold text-white mb-2">{place.name}</h3>
                <p className="text-sm text-[#CBD5E1] line-clamp-3 mb-4">{place.summary}</p>
                <button
                  onClick={() => window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${place.name}, ${stateName}`)}`, '_blank')}
                  className="px-4 py-2 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white text-sm font-semibold rounded-lg hover:shadow-lg transition-all duration-200 active:scale-95"
                >
                  Explore
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
