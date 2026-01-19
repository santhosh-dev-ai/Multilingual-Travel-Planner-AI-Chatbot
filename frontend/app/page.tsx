'use client';

import { useState, useMemo, useRef, useEffect, useCallback } from 'react';
import HamburgerMenu from './components/HamburgerMenu';
import ChatInterface from './components/ChatInterface';
import LanguageSelector from './components/LanguageSelector';
import DestinationCard from './components/DestinationCard';
import FeatureCard from './components/FeatureCard';
import DestinationModal from './components/DestinationModal';
import DestinationFilters, { priceRanges } from './components/DestinationFilters';
import CompareDestinations from './components/CompareDestinations';
import WeatherWidget from './components/WeatherWidget';
import ItineraryBuilder from './components/ItineraryBuilder';
import WishlistModal from './components/WishlistModal';
import { useWishlist } from './hooks/useWishlist';
import { translations } from './data/destinations';
import { destinationsAPI } from './services/api';
import {
  SparklesIcon,
  GlobeAltIcon,
  ChatBubbleBottomCenterTextIcon,
  MapPinIcon,
  HeartIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  CameraIcon,
  ScaleIcon,
  ArrowPathIcon,
  CalendarDaysIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

export default function Home() {
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en-US');
  
  // Dynamic destinations state
  const [destinations, setDestinations] = useState<any[]>([]);
  const [loadingDestinations, setLoadingDestinations] = useState(true);
  const [destinationError, setDestinationError] = useState<string | null>(null);
  
  // Destination modal state
  const [selectedDestination, setSelectedDestination] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Itinerary builder state
  const [isItineraryOpen, setIsItineraryOpen] = useState(false);
  const [itineraryDestination, setItineraryDestination] = useState<any>(null);
  
  // Track destinations with built itineraries
  const [builtItineraries, setBuiltItineraries] = useState<number[]>([]);
  
  // Wishlist modal state
  const [isWishlistOpen, setIsWishlistOpen] = useState(false);
  // Saved Itineraries modal state
  const [isItinerariesOpen, setIsItinerariesOpen] = useState(false);
  
  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [selectedPriceRange, setSelectedPriceRange] = useState('all');
  const [selectedTripType, setSelectedTripType] = useState('all');
  const [sortBy, setSortBy] = useState('popular');
  
  // AI Search state
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Compare state
  const [compareList, setCompareList] = useState<number[]>([]);
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  
  // Wishlist
  const { isInWishlist, toggleWishlist, wishlist } = useWishlist();
  
  // Chat ref for AI integration
  const chatRef = useRef<any>(null);
  const [aiPrompt, setAiPrompt] = useState<string>('');

  // Fetch destinations from API
  const fetchDestinations = async () => {
    setLoadingDestinations(true);
    setDestinationError(null);
    
    try {
      const response = await destinationsAPI.getRandomDestinations(12);
      setDestinations(response.destinations || []);
    } catch (error) {
      console.error('Failed to fetch destinations:', error);
      setDestinationError('Failed to load destinations. Please try again.');
    } finally {
      setLoadingDestinations(false);
    }
  };

  // AI-powered search with debouncing
  const performAISearch = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }
    
    setIsSearching(true);
    try {
      const response = await destinationsAPI.searchDestinations(query, 8);
      setSearchResults(response.destinations || []);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // Handle search input with debouncing
  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
    
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    // Debounce the AI search (500ms delay)
    if (query.length >= 2) {
      searchTimeoutRef.current = setTimeout(() => {
        performAISearch(query);
      }, 500);
    } else {
      setSearchResults([]);
      setIsSearching(false);
    }
  }, [performAISearch]);

  // Fetch destinations on mount
  useEffect(() => {
    fetchDestinations();
  }, []);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

  const t = (translations as Record<string, typeof translations['en-US']>)[selectedLanguage] || translations['en-US'];

  const featureIcons = [
    SparklesIcon,
    GlobeAltIcon,
    MapPinIcon,
    ChatBubbleBottomCenterTextIcon,
    HeartIcon,
    CurrencyDollarIcon,
    UserGroupIcon,
    CameraIcon,
  ];

  // Filter and sort destinations
  const filteredDestinations = useMemo(() => {
    // If we have AI search results and user is searching, prioritize those
    if (searchQuery && searchQuery.length >= 2 && searchResults.length > 0) {
      let result = [...searchResults];
      
      // Apply additional filters to search results
      if (selectedRegion !== 'all') {
        result = result.filter(d => d.region === selectedRegion);
      }
      
      if (selectedPriceRange !== 'all') {
        const range = priceRanges.find(r => r.id === selectedPriceRange);
        if (range) {
          result = result.filter(d => d.priceValue >= range.min && d.priceValue < range.max);
        }
      }
      
      if (selectedTripType !== 'all') {
        result = result.filter(d => 
          d.tags && d.tags.some((tag: string) => tag.toLowerCase() === selectedTripType)
        );
      }
      
      return result;
    }
    
    // If searching (API call in progress), show empty until results come
    if (searchQuery && searchQuery.length >= 2 && isSearching) {
      return [];
    }
    
    // Otherwise use base destinations with local filtering
    let result = [...destinations];
    
    // Local search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(d => 
        d.name.toLowerCase().includes(query) ||
        d.country.toLowerCase().includes(query) ||
        d.description.toLowerCase().includes(query) ||
        (d.tags && d.tags.some((tag: string) => tag.toLowerCase().includes(query)))
      );
    }
    
    // Region filter
    if (selectedRegion !== 'all') {
      result = result.filter(d => d.region === selectedRegion);
    }
    
    // Price range filter
    if (selectedPriceRange !== 'all') {
      const range = priceRanges.find(r => r.id === selectedPriceRange);
      if (range) {
        result = result.filter(d => d.priceValue >= range.min && d.priceValue < range.max);
      }
    }
    
    // Trip type filter
    if (selectedTripType !== 'all') {
      result = result.filter(d => 
        d.tags && d.tags.some((tag: string) => tag.toLowerCase() === selectedTripType)
      );
    }
    
    // Sorting
    switch (sortBy) {
      case 'rating':
        result.sort((a, b) => b.rating - a.rating);
        break;
      case 'price-low':
        result.sort((a, b) => a.priceValue - b.priceValue);
        break;
      case 'price-high':
        result.sort((a, b) => b.priceValue - a.priceValue);
        break;
      case 'popular':
      default:
        result.sort((a, b) => b.reviews - a.reviews);
        break;
    }
    
    return result;
  }, [searchQuery, searchResults, destinations, selectedRegion, selectedPriceRange, selectedTripType, sortBy, isSearching]);

  const clearFilters = () => {
    setSearchQuery('');
    setSearchResults([]);
    setSelectedRegion('all');
    setSelectedPriceRange('all');
    setSelectedTripType('all');
    setSortBy('popular');
  };

  // Modal handlers
  const handleExplore = (destination: any) => {
    setSelectedDestination(destination);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedDestination(null);
  };

  // AI integration
  const handleAskAI = (destination: any) => {
    const prompt = typeof destination === 'string' 
      ? destination 
      : `Tell me about ${destination.name}, ${destination.country}. What are the best things to do there?`;
    setAiPrompt(prompt);
    // Scroll to chat
    const heroSection = document.querySelector('section');
    if (heroSection) {
      heroSection.scrollIntoView({ behavior: 'smooth' });
    }
    handleCloseModal();
  };

  // Itinerary builder
  const handleBuildItinerary = (destination: any) => {
    setItineraryDestination(destination);
    setIsItineraryOpen(true);
    handleCloseModal();
  };

  // Compare handlers
  const handleToggleCompare = (destinationId: number) => {
    setCompareList(prev => {
      if (prev.includes(destinationId)) {
        return prev.filter(id => id !== destinationId);
      }
      if (prev.length >= 4) {
        alert('You can compare up to 4 destinations at a time');
        return prev;
      }
      return [...prev, destinationId];
    });
  };

  const handleClearCompare = () => {
    setCompareList([]);
  };

  // Handle footer destination links - scroll and filter by region
  const handleFooterDestinationClick = (region: string) => {
    setSelectedRegion(region);
    setSearchQuery(''); // Clear any search
    setSearchResults([]);
    // Scroll to destinations section
    const destinationsSection = document.getElementById('destinations');
    if (destinationsSection) {
      destinationsSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-(--color-dark-surface)/80 backdrop-blur-md border-b border-(--color-border)">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-(--color-primary) to-(--color-secondary) rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-(--color-text-primary)">TravelGenie</h1>
                <p className="text-xs text-(--color-text-tertiary)">{t.header.tagline}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <LanguageSelector
                selectedLanguage={selectedLanguage}
                onLanguageChange={setSelectedLanguage}
              />
              <HamburgerMenu
                onWishlistClick={() => setIsWishlistOpen(true)}
                onItinerariesClick={() => setIsItinerariesOpen(true)}
                wishlistCount={wishlist.length}
                savedItinerariesCount={builtItineraries.length}
              />
            </div>
                {/* Saved Itineraries Modal */}
                {isItinerariesOpen && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white dark:bg-(--color-dark-surface) rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto relative">
                      <button
                        className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
                        onClick={() => setIsItinerariesOpen(false)}
                        aria-label="Close"
                      >
                        <span style={{fontSize:24}}>&times;</span>
                      </button>
                      <div className="p-6">
                        <h2 className="text-2xl font-bold mb-4 text-(--color-text-primary)">Saved Itineraries</h2>
                        {builtItineraries.length === 0 ? (
                          <p className="text-(--color-text-secondary)">No itineraries saved yet. Build an itinerary to see it here!</p>
                        ) : (
                          <ul className="space-y-4">
                            {builtItineraries.map((id, idx) => (
                              <li key={id} className="p-4 bg-(--color-background-secondary) rounded-lg">
                                <span className="font-medium text-(--color-text-primary)">Itinerary #{idx + 1}</span>
                                {/* You can expand this to show more details if available */}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                  </div>
                )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-(--color-primary-50) via-(--color-background) to-(--color-accent-50) dark:from-(--color-dark-background) dark:via-(--color-dark-background-secondary) dark:to-(--color-dark-background-tertiary)">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, currentColor 1px, transparent 0)',
            backgroundSize: '32px 32px',
          }} />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="text-center lg:text-left">
              <h2 className="text-4xl lg:text-5xl xl:text-6xl font-bold text-(--color-text-primary) mb-6 leading-tight">
                {t.hero.title}
              </h2>
              
              <p className="text-lg text-(--color-text-secondary) mb-8 leading-relaxed">
                {t.hero.subtitle}
              </p>


              {/* Stats */}
              <div className="grid grid-cols-3 gap-6 mt-12 pt-12 border-t border-(--color-border)">
                <div>
                  <div className="text-3xl font-bold text-(--color-primary) mb-1">150+</div>
                  <div className="text-sm text-(--color-text-tertiary)">{t.stats.countries}</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-(--color-primary) mb-1">50K+</div>
                  <div className="text-sm text-(--color-text-tertiary)">{t.stats.travelers}</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-(--color-primary) mb-1">24/7</div>
                  <div className="text-sm text-(--color-text-tertiary)">{t.stats.support}</div>
                </div>
              </div>
            </div>

            {/* Right - Chat Interface */}
            <div className="lg:pl-8">
              <ChatInterface selectedLanguage={selectedLanguage} initialPrompt={aiPrompt} />
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section - Ready to Start Your Adventure */}
      <section className="py-16 bg-gradient-to-br from-(--color-primary) to-(--color-secondary) relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '32px 32px',
          }} />
        </div>
        
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
            {t.cta.title}
          </h2>
          <p className="text-lg text-white/90 mb-6">
            {t.cta.subtitle}
          </p>
          <button
            onClick={() => {
              const destSection = document.getElementById('destinations');
              if (destSection) destSection.scrollIntoView({ behavior: 'smooth' });
            }}
            className="px-8 py-3 bg-white text-(--color-primary) font-semibold rounded-full hover:shadow-lg transform hover:scale-105 transition-all duration-200"
          >
            Explore Destinations
          </button>
        </div>
      </section>

      {/* Destinations Section */}
      <section id="destinations" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold text-(--color-text-primary) mb-2">
                {t.destinations.title}
              </h2>
              {wishlist.length > 0 && (
                <p className="text-sm text-(--color-text-secondary)">
                  ❤️ {wishlist.length} saved to wishlist
                </p>
              )}
            </div>
            
            <div className="flex items-center gap-3 mt-4 md:mt-0">
              {/* Refresh Destinations Button */}
              <button
                onClick={fetchDestinations}
                disabled={loadingDestinations}
                className="flex items-center gap-2 px-4 py-2 bg-(--color-background-secondary) text-(--color-text-secondary) rounded-lg hover:bg-(--color-background-tertiary) transition-all disabled:opacity-50"
                title="Get new destinations"
              >
                <ArrowPathIcon className={`w-5 h-5 ${loadingDestinations ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              
              {/* Compare Button */}
              {compareList.length > 0 && (
                <button
                  onClick={() => setIsCompareOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-(--color-primary) to-(--color-secondary) text-white rounded-lg hover:shadow-lg transition-all"
                >
                  <ScaleIcon className="w-5 h-5" />
                  Compare ({compareList.length})
                </button>
              )}
            </div>
          </div>

          {/* Filters */}
          <DestinationFilters
            searchQuery={searchQuery}
            onSearchChange={handleSearchChange}
            selectedRegion={selectedRegion}
            onRegionChange={setSelectedRegion}
            selectedPriceRange={selectedPriceRange}
            onPriceRangeChange={setSelectedPriceRange}
            selectedTripType={selectedTripType}
            onTripTypeChange={setSelectedTripType}
            sortBy={sortBy}
            onSortChange={setSortBy}
            resultCount={filteredDestinations.length}
            onClearFilters={clearFilters}
            isSearching={isSearching}
          />

          {/* AI Search Indicator */}
          {isSearching && (
            <div className="flex items-center justify-center gap-2 py-4 text-(--color-primary)">
              <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
              <span className="text-sm font-medium">Searching worldwide destinations...</span>
            </div>
          )}

          {/* Search Results Info */}
          {searchQuery && searchQuery.length >= 2 && searchResults.length > 0 && !isSearching && (
            <div className="flex items-center gap-2 py-2 px-4 bg-teal-50 dark:bg-teal-900/20 text-teal-700 dark:text-teal-300 rounded-lg text-sm">
              <MagnifyingGlassIcon className="w-5 h-5" />
              <span>Found {searchResults.length} destination{searchResults.length !== 1 ? 's' : ''} for "{searchQuery}"</span>
            </div>
          )}

          {/* Loading State */}
          {loadingDestinations && (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-(--color-background-secondary) rounded-2xl overflow-hidden animate-pulse">
                  <div className="h-48 bg-(--color-background-tertiary)" />
                  <div className="p-5 space-y-3">
                    <div className="h-6 bg-(--color-background-tertiary) rounded w-3/4" />
                    <div className="h-4 bg-(--color-background-tertiary) rounded w-1/2" />
                    <div className="h-4 bg-(--color-background-tertiary) rounded w-full" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Error State */}
          {destinationError && !loadingDestinations && (
            <div className="text-center py-12">
              <p className="text-red-500 mb-4">{destinationError}</p>
              <button
                onClick={fetchDestinations}
                className="px-6 py-2 bg-(--color-primary) text-white rounded-lg hover:bg-(--color-primary-dark) transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Destinations Grid */}
          {!loadingDestinations && !destinationError && (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredDestinations.map((destination) => (
                <DestinationCard 
                  key={destination.id} 
                  destination={destination} 
                  translations={t.destinations}
                  isInWishlist={isInWishlist(destination.id)}
                  onToggleWishlist={toggleWishlist}
                  onExplore={handleExplore}
                  onAskAI={handleAskAI}
                  isInCompare={compareList.includes(destination.id)}
                  onToggleCompare={handleToggleCompare}
                />
              ))}
            </div>
          )}

          {!loadingDestinations && !destinationError && filteredDestinations.length === 0 && (
            <div className="text-center py-12">
              <p className="text-(--color-text-secondary) mb-2">No destinations found</p>
              <button
                onClick={clearFilters}
                className="text-(--color-primary) hover:underline"
              >
                Clear filters
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Features Section - Why Choose TravelGenie */}
      <section className="py-20 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary)">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-(--color-text-primary)">
              {t.features.title}
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {t.features.items.map((feature, index) => (
              <FeatureCard
                key={index}
                icon={featureIcons[index]}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Destination Modal */}
      <DestinationModal
        destination={selectedDestination}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onAskAI={handleAskAI}
        onToggleWishlist={toggleWishlist}
        isInWishlist={selectedDestination ? isInWishlist(selectedDestination.id) : false}
        translations={t.destinations}
        onBuildItinerary={handleBuildItinerary}
        hasItinerary={selectedDestination ? builtItineraries.includes(selectedDestination.id) : false}
      />

      {/* Compare Modal */}
      <CompareDestinations
        destinations={destinations}
        compareList={compareList}
        onRemoveFromCompare={(id: number) => setCompareList(prev => prev.filter(i => i !== id))}
        onClearCompare={handleClearCompare}
        onAskAI={handleAskAI}
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
      />

      {/* Itinerary Builder Modal */}
      {isItineraryOpen && (
        <ItineraryBuilder
          destination={itineraryDestination}
          onClose={() => {
            setIsItineraryOpen(false);
            setItineraryDestination(null);
          }}
          onItineraryBuilt={(destinationId: number) => {
            setBuiltItineraries(prev => [...prev, destinationId]);
          }}
        />
      )}

      {/* Wishlist Modal */}
      <WishlistModal
        isOpen={isWishlistOpen}
        onClose={() => setIsWishlistOpen(false)}
        wishlist={wishlist}
        onRemoveFromWishlist={toggleWishlist}
        onExplore={(destination: any) => {
          setSelectedDestination(destination);
          setIsModalOpen(true);
        }}
      />

      {/* Footer */}
      <footer className="py-12 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) border-t border-(--color-border)">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-(--color-primary) to-(--color-secondary) rounded-lg flex items-center justify-center">
                  <SparklesIcon className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold text-(--color-text-primary)">TravelGenie</span>
              </div>
              <p className="text-sm text-(--color-text-secondary)">
                {t.footer.description}
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-(--color-text-primary) mb-4">{t.footer.destinations}</h4>
              <ul className="space-y-2 text-sm text-(--color-text-secondary)">
                <li><button onClick={() => handleFooterDestinationClick('europe')} className="hover:text-(--color-primary) transition-colors cursor-pointer">{t.footer.europe}</button></li>
                <li><button onClick={() => handleFooterDestinationClick('asia')} className="hover:text-(--color-primary) transition-colors cursor-pointer">{t.footer.asia}</button></li>
                <li><button onClick={() => handleFooterDestinationClick('americas')} className="hover:text-(--color-primary) transition-colors cursor-pointer">{t.footer.americas}</button></li>
                <li><button onClick={() => handleFooterDestinationClick('africa')} className="hover:text-(--color-primary) transition-colors cursor-pointer">{t.footer.africa}</button></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-(--color-text-primary) mb-4">{t.footer.company}</h4>
              <ul className="space-y-2 text-sm text-(--color-text-secondary)">
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.about}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.careers}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.blog}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.contact}</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-(--color-text-primary) mb-4">{t.footer.support}</h4>
              <ul className="space-y-2 text-sm text-(--color-text-secondary)">
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.help}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.privacy}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.terms}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.cookies}</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-(--color-border) text-center text-sm text-(--color-text-tertiary)">
            <p>{t.footer.copyright}</p>
          </div>
        </div>
      </footer>
    </div>
  );
}