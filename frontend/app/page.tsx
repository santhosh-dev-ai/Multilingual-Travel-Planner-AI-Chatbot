'use client';

import { useState, useMemo, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import HamburgerMenu from './components/HamburgerMenu';
import ChatInterface from './components/ChatInterface';
import LanguageSelector from './components/LanguageSelector';
import DestinationCard from './components/DestinationCard';
import DestinationModal from './components/DestinationModal';
import DestinationFilters, { priceRanges } from './components/DestinationFilters';
import CompareDestinations from './components/CompareDestinations';
import WeatherWidget from './components/WeatherWidget';
import ItineraryBuilder from './components/ItineraryBuilder';
import WishlistModal from './components/WishlistModal';
import SavedItineraries from './components/SavedItineraries';
import { useWishlist } from './hooks/useWishlist';
import { translations, destinations } from './data/destinations-new';
import { savedItineraryAPI, destinationsAPI, authAPI } from './services/api';
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
  MagnifyingGlassIcon,
  PaperAirplaneIcon,
  TruckIcon,
  BuildingOffice2Icon,
  HomeModernIcon,
  BriefcaseIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

export default function Home() {
  const [authChecked, setAuthChecked] = useState(true);
  const [currentUsername, setCurrentUsername] = useState('Traveler');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en-US');
  
  const [showAllDestinations, setShowAllDestinations] = useState(false);
  
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
  
  // Saved itineraries count
  const [savedItinerariesCount, setSavedItinerariesCount] = useState(0);
  
  // Fetch saved itineraries count
  const fetchSavedItinerariesCount = async () => {
    try {
      const response = await savedItineraryAPI.getCount();
      setSavedItinerariesCount(response.count || 0);
    } catch (error) {
      console.error('Failed to fetch saved itineraries count:', error);
    }
  };
  
  // Fetch count on mount
  useEffect(() => {
    fetchSavedItinerariesCount();
  }, []);

  useEffect(() => {
    const user = authAPI.getCurrentUser();
    const resolvedUsername =
      user?.display_name ||
      user?.username ||
      (user?.email ? String(user.email).split('@')[0] : null) ||
      'Traveler';
    setCurrentUsername(resolvedUsername);
    setAuthChecked(true);
  }, []);
  
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

  // Fetch destinations from API with refresh
  const fetchDestinations = async (forceRefresh = false) => {
    setLoadingDestinations(true);
    setDestinationError(null);
    
    try {
      const count = forceRefresh ? Math.floor(Math.random() * 6) + 15 : 15; // Show 15-20 destinations
      const response = await destinationsAPI.getRandomDestinations(count);
      setDestinations(response.destinations || []);
    } catch (error) {
      console.error('Failed to fetch destinations:', error);
      setDestinationError('Failed to load destinations. Please try again.');
    } finally {
      setLoadingDestinations(false);
    }
  };

  // AI-powered search with enhanced results
  const performAISearch = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }
    
    setIsSearching(true);
    try {
      const response = await destinationsAPI.searchDestinations(query, 12);
      // Enhance search results with complete destination data
      const enhancedResults = (response.destinations || []).map((dest: any) => ({
        ...dest,
        // Ensure all required fields are present
        image: dest.image || 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80',
        rating: dest.rating || 4.5,
        reviews: dest.reviews || Math.floor(Math.random() * 1000) + 500,
        duration: dest.duration || '3-5 days',
        price: dest.price || '$399',
        priceValue: dest.priceValue || 399,
        coordinates: dest.coordinates || { lat: 40.7128, lon: -74.0060 },
        highlights: dest.highlights || [
          'Educational opportunities',
          'Student-friendly environment',
          'Cultural experiences',
          'Budget-conscious options'
        ],
        tags: dest.tags || ['Culture', 'Educational', 'Budget']
      }));
      setSearchResults(enhancedResults);
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

  const serviceCards = [
    {
      title: 'Flights',
      description: 'Search real-time flight options and compare student-friendly fares.',
      href: '/flights',
      cta: 'Explore Flights',
      icon: PaperAirplaneIcon,
    },
    {
      title: 'Trains',
      description: 'Browse train routes and plan rail journeys for your trip.',
      href: '/trains',
      cta: 'Explore Trains',
      icon: GlobeAltIcon,
    },
    {
      title: 'Bus',
      description: 'Find bus travel options for affordable intercity mobility.',
      href: '/bus',
      cta: 'Explore Bus',
      icon: TruckIcon,
    },
    {
      title: 'Hotels',
      description: 'Discover hotel stays that fit your destination and budget.',
      href: '/hotels',
      cta: 'Explore Hotels',
      icon: BuildingOffice2Icon,
    },
    {
      title: 'Rooms',
      description: 'Check private room listings for short and long stays.',
      href: '/rooms',
      cta: 'Explore Rooms',
      icon: HomeModernIcon,
    },
    {
      title: 'Airbnb',
      description: 'Compare homestay-style accommodations for flexible travel.',
      href: '/airbnb',
      cta: 'Explore Airbnb',
      icon: HomeModernIcon,
    },
    {
      title: 'Lounges',
      description: 'Find airport and transit lounges for comfortable stopovers.',
      href: '/lounges',
      cta: 'Explore Lounges',
      icon: BriefcaseIcon,
    },
    {
      title: 'Services',
      description: 'Access additional travel support tools and assistance.',
      href: '/services',
      cta: 'Explore Services',
      icon: SparklesIcon,
    },
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

  // Display destinations (limit to 9 initially unless showing all)
  const displayDestinations = useMemo(() => {
    return showAllDestinations ? filteredDestinations : filteredDestinations.slice(0, 9);
  }, [filteredDestinations, showAllDestinations]);

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

  const handleLogout = () => {
    authAPI.logout();
    setCurrentUsername('Traveler');
  };


  if (!authChecked) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] to-[#1E293B]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-gradient-to-r from-[#1E293B]/95 to-[#334155]/95 backdrop-blur-lg border-b border-[#3AA8C1]/20 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#3AA8C1]/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <SparklesIcon className="w-6 h-6 text-[#3AA8C1]" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">TravelGenie</h1>
                <p className="text-xs text-[#CBD5E1]">{t.header.tagline}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl bg-[#0F172A]/40 border border-[#3AA8C1]/20">
                <span className="text-sm text-[#CBD5E1]">Hi,</span>
                <span className="text-sm font-semibold text-white">{currentUsername}</span>
              </div>
              <LanguageSelector
                selectedLanguage={selectedLanguage}
                onLanguageChange={setSelectedLanguage}
              />
              <HamburgerMenu
                onWishlistClick={() => setIsWishlistOpen(true)}
                onItinerariesClick={() => setIsItinerariesOpen(true)}
                onLogout={handleLogout}
                wishlistCount={wishlist.length}
                savedItinerariesCount={savedItinerariesCount}
                translations={t}
              />
            </div>
      {/* Saved Itineraries Modal */}
      <SavedItineraries
        isOpen={isItinerariesOpen}
        onClose={() => setIsItinerariesOpen(false)}
        translations={t}
      />
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#334155]">
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
              <h2 className="text-4xl lg:text-5xl xl:text-6xl font-bold text-white mb-6 leading-tight">
                {t.hero.title}
              </h2>
              
              <p className="text-lg text-[#CBD5E1] mb-8 leading-relaxed">
                {t.hero.subtitle}
              </p>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-6 mt-12 pt-12 border-t border-[#475569]">
                <div>
                  <div className="text-3xl font-bold text-[#3AA8C1] mb-1">150+</div>
                  <div className="text-sm text-[#94A3B8]">{t.stats.countries}</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-[#3AA8C1] mb-1">50K+</div>
                  <div className="text-sm text-[#94A3B8]">{t.stats.travelers}</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-[#3AA8C1] mb-1">24/7</div>
                  <div className="text-sm text-[#94A3B8]">{t.stats.support}</div>
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
      <section className="py-16 bg-gradient-to-br from-[#3AA8C1] to-[#58B8CD] relative overflow-hidden">
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
            className="px-8 py-3 bg-white text-[#3AA8C1] font-semibold rounded-full hover:shadow-lg transform hover:scale-105 transition-all duration-200"
          >
            Explore Destinations
          </button>
        </div>
      </section>

      {/* Destinations Section */}
      <section id="destinations" className="py-20 bg-gradient-to-b from-[#1E293B] to-[#0F172A]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold text-white mb-2">
                {t.destinations.title}
              </h2>
              {wishlist.length > 0 && (
                <p className="text-sm text-[#CBD5E1]">
                  ❤️ {wishlist.length} saved to wishlist
                </p>
              )}
            </div>
            
            <div className="flex items-center gap-3 mt-4 md:mt-0">
              {/* Refresh Destinations Button */}
              <button
                onClick={() => fetchDestinations(true)}
                disabled={loadingDestinations}
                className="flex items-center gap-2 px-4 py-2 bg-[#334155]/80 text-[#CBD5E1] rounded-lg hover:bg-[#334155] transition-all disabled:opacity-50 shadow-sm border border-[#475569]"
                title="Get new destinations"
              >
                <ArrowPathIcon className={`w-5 h-5 ${loadingDestinations ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              
              {/* Compare Button */}
              {compareList.length > 0 && (
                <button
                  onClick={() => setIsCompareOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white rounded-lg hover:shadow-lg transition-all"
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
            <div className="flex items-center justify-center gap-2 py-4 text-[#3AA8C1]">
              <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
              <span className="text-sm font-medium">Searching destinations...</span>
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
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-[#334155] rounded-2xl overflow-hidden animate-pulse shadow-lg border border-[#475569]">
                  <div className="h-56 bg-gradient-to-r from-[#475569] to-[#64748B]" />
                  <div className="p-6 space-y-4">
                    <div className="h-6 bg-gradient-to-r from-[#475569] to-[#64748B] rounded-lg w-3/4" />
                    <div className="h-4 bg-gradient-to-r from-[#475569] to-[#64748B] rounded w-1/2" />
                    <div className="h-4 bg-gradient-to-r from-[#475569] to-[#64748B] rounded w-full" />
                    <div className="h-10 bg-gradient-to-r from-[#475569] to-[#64748B] rounded-xl" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Error State */}
          {destinationError && !loadingDestinations && (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-gradient-to-r from-[#FEF2F2] to-[#FEE2E2] rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚠️</span>
              </div>
              <p className="text-red-600 mb-6 text-lg font-medium">{destinationError}</p>
              <button
                onClick={() => fetchDestinations()}
                className="px-8 py-3 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white rounded-xl hover:shadow-lg transition-all transform hover:scale-105 font-medium"
              >
                🔄 Try Again
              </button>
            </div>
          )}

          {/* Destinations Grid */}
          {!loadingDestinations && !destinationError && (
            <>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {displayDestinations.map((destination) => (
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
              
              {/* View More Button */}
              {!showAllDestinations && filteredDestinations.length > 9 && (
                <div className="text-center mt-12">
                  <button
                    onClick={() => setShowAllDestinations(true)}
                    className="px-8 py-3 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white rounded-xl hover:shadow-lg transition-all transform hover:scale-105 font-medium"
                  >
                    {t.destinations?.viewMore || 'View More Destinations'}
                  </button>
                </div>
              )}
            </>
          )}

          {!loadingDestinations && !destinationError && displayDestinations.length === 0 && (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-gradient-to-r from-[#334155] to-[#475569] rounded-2xl flex items-center justify-center mx-auto mb-4">
                <MagnifyingGlassIcon className="w-8 h-8 text-[#94A3B8]" />
              </div>
              <p className="text-white mb-2 text-lg font-medium">No destinations found</p>
              <p className="text-[#94A3B8] mb-6">Try adjusting your search or filters</p>
              <button
                onClick={clearFilters}
                className="px-6 py-3 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white rounded-xl hover:shadow-lg transition-all transform hover:scale-105 font-medium"
              >
                🔄 Clear Filters
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Services Section */}
      <section className="py-20 bg-gradient-to-br from-[#334155] to-[#1E293B]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-white">
              Explore Travel Services
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {serviceCards.map((service) => (
              <div
                key={service.href}
                className="bg-[#1E293B] rounded-xl border border-[#334155] shadow-sm hover:shadow-lg transition-all duration-300 p-6"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-[#3AA8C1]/20 to-[#58B8CD]/20 rounded-xl flex items-center justify-center mb-4">
                  <service.icon className="w-7 h-7 text-[#3AA8C1]" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{service.title}</h3>
                <p className="text-sm text-[#CBD5E1] leading-relaxed mb-4">{service.description}</p>
                <Link
                  href={service.href}
                  className="inline-flex items-center text-sm font-semibold text-[#58B8CD] hover:text-[#7ED1E2] transition-colors"
                >
                  {service.cta}
                </Link>
              </div>
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
        hasItinerary={false}
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
          onItineraryBuilt={() => {
            fetchSavedItinerariesCount(); // Refresh count when itinerary is saved
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
      <footer className="py-12 bg-gradient-to-r from-[#0F172A] to-[#1E293B] border-t border-[#334155]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-[#3AA8C1]/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                  <SparklesIcon className="w-5 h-5 text-[#3AA8C1]" />
                </div>
                <span className="text-lg font-bold text-white">TravelGenie</span>
              </div>
              <p className="text-sm text-[#CBD5E1]">
                {t.footer.description}
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">{t.footer.destinations}</h4>
              <ul className="space-y-2 text-sm text-[#CBD5E1]">
                <li><button onClick={() => handleFooterDestinationClick('europe')} className="hover:text-[#3AA8C1] transition-colors cursor-pointer">{t.footer.europe}</button></li>
                <li><button onClick={() => handleFooterDestinationClick('asia')} className="hover:text-[#3AA8C1] transition-colors cursor-pointer">{t.footer.asia}</button></li>
                <li><button onClick={() => handleFooterDestinationClick('americas')} className="hover:text-[#3AA8C1] transition-colors cursor-pointer">{t.footer.americas}</button></li>
                <li><button onClick={() => handleFooterDestinationClick('africa')} className="hover:text-[#3AA8C1] transition-colors cursor-pointer">{t.footer.africa}</button></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">{t.footer.company}</h4>
              <ul className="space-y-2 text-sm text-[#CBD5E1]">
                <li><a href="#" className="hover:text-[#3AA8C1] transition-colors">{t.footer.about}</a></li>
                <li><a href="#" className="hover:text-[#3AA8C1] transition-colors">{t.footer.careers}</a></li>
                <li><a href="#" className="hover:text-[#3AA8C1] transition-colors">{t.footer.blog}</a></li>
                <li><a href="#" className="hover:text-[#3AA8C1] transition-colors">{t.footer.contact}</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">{t.footer.support}</h4>
              <ul className="space-y-2 text-sm text-[#CBD5E1]">
                <li><a href="#" className="hover:text-[#3AA8C1] transition-colors">{t.footer.help}</a></li>
                <li><a href="#" className="hover:text-[#3AA8C1] transition-colors">{t.footer.privacy}</a></li>
                <li><a href="#" className="hover:text-[#3AA8C1] transition-colors">{t.footer.terms}</a></li>
                <li><a href="#" className="hover:text-[#3AA8C1] transition-colors">{t.footer.cookies}</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-[#334155] text-center text-sm text-[#94A3B8]">
            <p>{t.footer.copyright}</p>
          </div>
        </div>
      </footer>
    </div>
  );
}