'use client';

import { useState } from 'react';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

const regions = [
  { id: 'all', name: 'All Regions' },
  { id: 'europe', name: 'Europe' },
  { id: 'asia', name: 'Asia' },
  { id: 'americas', name: 'Americas' },
  { id: 'africa', name: 'Africa' },
  { id: 'oceania', name: 'Oceania' },
];

const priceRanges = [
  { id: 'all', name: 'Any Budget', min: 0, max: Infinity },
  { id: 'budget', name: 'Budget ($0-$1000)', min: 0, max: 1000 },
  { id: 'mid', name: 'Mid-Range ($1000-$2000)', min: 1000, max: 2000 },
  { id: 'luxury', name: 'Luxury ($2000+)', min: 2000, max: Infinity },
];

const tripTypes = [
  { id: 'all', name: 'All Types' },
  { id: 'adventure', name: 'Adventure' },
  { id: 'relaxation', name: 'Relaxation' },
  { id: 'culture', name: 'Culture' },
  { id: 'nature', name: 'Nature' },
  { id: 'romantic', name: 'Romantic' },
  { id: 'family', name: 'Family' },
];

const sortOptions = [
  { id: 'popular', name: 'Most Popular' },
  { id: 'rating', name: 'Highest Rated' },
  { id: 'price-low', name: 'Price: Low to High' },
  { id: 'price-high', name: 'Price: High to Low' },
];

export default function DestinationFilters({
  searchQuery,
  onSearchChange,
  selectedRegion,
  onRegionChange,
  selectedPriceRange,
  onPriceRangeChange,
  selectedTripType,
  onTripTypeChange,
  sortBy,
  onSortChange,
  resultCount,
  onClearFilters,
  isSearching = false,
}) {
  const [showFilters, setShowFilters] = useState(false);

  const hasActiveFilters = 
    searchQuery || 
    selectedRegion !== 'all' || 
    selectedPriceRange !== 'all' || 
    selectedTripType !== 'all';

  return (
    <div className="mb-8">
      {/* Search Bar */}
      <div className="flex flex-col md:flex-row gap-4 mb-4">
        <div className="relative flex-1">
          {isSearching ? (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 border-2 border-(--color-primary) border-t-transparent rounded-full animate-spin" />
          ) : (
            <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-(--color-text-tertiary)" />
          )}
          <input
            type="text"
            placeholder="Search any destination worldwide..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-(--color-surface) dark:bg-(--color-dark-surface) border border-(--color-border) rounded-xl text-(--color-text-primary) placeholder:text-(--color-text-tertiary) focus:outline-none focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--color-primary) transition-all"
          />
          {searchQuery && !isSearching && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-(--color-text-tertiary) hover:text-(--color-text-primary)"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          )}
        </div>

        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-4 py-3 border rounded-xl transition-all ${
            showFilters || hasActiveFilters
              ? 'bg-(--color-primary) text-white border-(--color-primary)'
              : 'bg-(--color-surface) dark:bg-(--color-dark-surface) border-(--color-border) text-(--color-text-secondary) hover:border-(--color-primary)'
          }`}
        >
          <FunnelIcon className="w-5 h-5" />
          <span>Filters</span>
          {hasActiveFilters && (
            <span className="w-2 h-2 bg-white rounded-full"></span>
          )}
        </button>

        {/* Sort Dropdown */}
        <div className="relative">
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="appearance-none w-full md:w-48 px-4 py-3 pr-10 bg-(--color-surface) dark:bg-(--color-dark-surface) border border-(--color-border) rounded-xl text-(--color-text-primary) focus:outline-none focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--color-primary) transition-all cursor-pointer"
          >
            {sortOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
          <ChevronDownIcon className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-(--color-text-tertiary) pointer-events-none" />
        </div>
      </div>

      {/* Filter Options */}
      {showFilters && (
        <div className="p-4 bg-(--color-surface) dark:bg-(--color-dark-surface) border border-(--color-border) rounded-xl mb-4 animate-slideDown">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Region Filter */}
            <div>
              <label className="block text-sm font-medium text-(--color-text-secondary) mb-2">
                Region
              </label>
              <select
                value={selectedRegion}
                onChange={(e) => onRegionChange(e.target.value)}
                className="w-full px-4 py-2 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) border border-(--color-border) rounded-lg text-(--color-text-primary) focus:outline-none focus:ring-2 focus:ring-(--color-primary)/20"
              >
                {regions.map((region) => (
                  <option key={region.id} value={region.id}>
                    {region.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Price Range Filter */}
            <div>
              <label className="block text-sm font-medium text-(--color-text-secondary) mb-2">
                Budget
              </label>
              <select
                value={selectedPriceRange}
                onChange={(e) => onPriceRangeChange(e.target.value)}
                className="w-full px-4 py-2 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) border border-(--color-border) rounded-lg text-(--color-text-primary) focus:outline-none focus:ring-2 focus:ring-(--color-primary)/20"
              >
                {priceRanges.map((range) => (
                  <option key={range.id} value={range.id}>
                    {range.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Trip Type Filter */}
            <div>
              <label className="block text-sm font-medium text-(--color-text-secondary) mb-2">
                Trip Type
              </label>
              <select
                value={selectedTripType}
                onChange={(e) => onTripTypeChange(e.target.value)}
                className="w-full px-4 py-2 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) border border-(--color-border) rounded-lg text-(--color-text-primary) focus:outline-none focus:ring-2 focus:ring-(--color-primary)/20"
              >
                {tripTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <button
              onClick={onClearFilters}
              className="mt-4 text-sm text-(--color-primary) hover:underline"
            >
              Clear all filters
            </button>
          )}
        </div>
      )}

      {/* Results Count */}
      <div className="text-sm text-(--color-text-secondary)">
        Showing {resultCount} destination{resultCount !== 1 ? 's' : ''}
        {hasActiveFilters && ' (filtered)'}
      </div>
    </div>
  );
}

// Export filter utilities
export { regions, priceRanges, tripTypes, sortOptions };
