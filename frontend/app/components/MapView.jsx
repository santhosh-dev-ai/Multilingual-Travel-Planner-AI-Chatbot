'use client';

import { useState, useEffect, useRef } from 'react';
import { MapPinIcon, XMarkIcon, GlobeAltIcon } from '@heroicons/react/24/outline';

export default function MapView({ destinations, selectedDestination, onSelectDestination, onClose }) {
  const mapContainerRef = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState(false);

  // Simple SVG-based world map visualization (no external dependencies)
  const worldMapBounds = {
    minLat: -60,
    maxLat: 85,
    minLng: -180,
    maxLng: 180,
  };

  const latLngToXY = (lat, lng, width, height) => {
    const x = ((lng - worldMapBounds.minLng) / (worldMapBounds.maxLng - worldMapBounds.minLng)) * width;
    const y = ((worldMapBounds.maxLat - lat) / (worldMapBounds.maxLat - worldMapBounds.minLat)) * height;
    return { x, y };
  };

  const [dimensions, setDimensions] = useState({ width: 800, height: 450 });
  const [hoveredDestination, setHoveredDestination] = useState(null);

  useEffect(() => {
    if (mapContainerRef.current) {
      const rect = mapContainerRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width, height: Math.min(rect.width * 0.5625, 500) });
    }
    
    const handleResize = () => {
      if (mapContainerRef.current) {
        const rect = mapContainerRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: Math.min(rect.width * 0.5625, 500) });
      }
    };
    
    window.addEventListener('resize', handleResize);
    setMapLoaded(true);
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Filter destinations with valid coordinates
  const mappableDestinations = destinations.filter(d => d.coordinates?.lat && d.coordinates?.lng);

  const regionColors = {
    europe: '#3B82F6',
    asia: '#10B981',
    africa: '#F59E0B',
    americas: '#EF4444',
    oceania: '#8B5CF6',
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-white rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-teal-600 to-blue-600 text-white">
          <div className="flex items-center gap-3">
            <GlobeAltIcon className="w-6 h-6" />
            <div>
              <h2 className="text-xl font-bold">Explore Destinations</h2>
              <p className="text-sm opacity-90">{mappableDestinations.length} destinations on map</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Map Container */}
        <div className="relative" ref={mapContainerRef}>
          <svg
            width="100%"
            height={dimensions.height}
            viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
            className="bg-gradient-to-b from-blue-100 to-blue-200"
          >
            {/* Simple world outline - stylized */}
            <defs>
              <linearGradient id="oceanGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#E0F2FE" />
                <stop offset="100%" stopColor="#BAE6FD" />
              </linearGradient>
              <linearGradient id="landGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#86EFAC" />
                <stop offset="100%" stopColor="#4ADE80" />
              </linearGradient>
              <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.3"/>
              </filter>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#oceanGradient)" />
            
            {/* Simplified continent shapes */}
            {/* These are approximate artistic representations */}
            
            {/* Grid lines for reference */}
            {[-60, -30, 0, 30, 60].map(lat => {
              const pos = latLngToXY(lat, 0, dimensions.width, dimensions.height);
              return (
                <line
                  key={`lat-${lat}`}
                  x1={0}
                  y1={pos.y}
                  x2={dimensions.width}
                  y2={pos.y}
                  stroke="#fff"
                  strokeWidth="0.5"
                  strokeOpacity="0.3"
                />
              );
            })}
            
            {[-120, -60, 0, 60, 120].map(lng => {
              const pos = latLngToXY(0, lng, dimensions.width, dimensions.height);
              return (
                <line
                  key={`lng-${lng}`}
                  x1={pos.x}
                  y1={0}
                  x2={pos.x}
                  y2={dimensions.height}
                  stroke="#fff"
                  strokeWidth="0.5"
                  strokeOpacity="0.3"
                />
              );
            })}

            {/* Destination markers */}
            {mappableDestinations.map((dest, index) => {
              const pos = latLngToXY(dest.coordinates.lat, dest.coordinates.lng, dimensions.width, dimensions.height);
              const isSelected = selectedDestination?.id === dest.id;
              const isHovered = hoveredDestination?.id === dest.id;
              const color = regionColors[dest.region] || '#6B7280';
              
              return (
                <g key={dest.id || index}>
                  {/* Pulse animation for selected */}
                  {isSelected && (
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r="20"
                      fill={color}
                      opacity="0.3"
                      className="animate-ping"
                    />
                  )}
                  
                  {/* Outer ring */}
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={isSelected ? 16 : isHovered ? 14 : 10}
                    fill="white"
                    filter="url(#shadow)"
                    className="transition-all duration-300 cursor-pointer"
                    onMouseEnter={() => setHoveredDestination(dest)}
                    onMouseLeave={() => setHoveredDestination(null)}
                    onClick={() => onSelectDestination(dest)}
                  />
                  
                  {/* Inner colored circle */}
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={isSelected ? 12 : isHovered ? 10 : 7}
                    fill={color}
                    className="transition-all duration-300 cursor-pointer"
                    onMouseEnter={() => setHoveredDestination(dest)}
                    onMouseLeave={() => setHoveredDestination(null)}
                    onClick={() => onSelectDestination(dest)}
                  />
                  
                  {/* Pin icon */}
                  <text
                    x={pos.x}
                    y={pos.y + 1}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill="white"
                    fontSize={isSelected || isHovered ? "10" : "8"}
                    className="pointer-events-none"
                  >
                    📍
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Hover tooltip */}
          {hoveredDestination && (
            <div
              className="absolute bg-white rounded-lg shadow-xl p-3 pointer-events-none z-10 min-w-48"
              style={{
                left: Math.min(
                  latLngToXY(hoveredDestination.coordinates.lat, hoveredDestination.coordinates.lng, dimensions.width, dimensions.height).x + 20,
                  dimensions.width - 200
                ),
                top: Math.max(
                  latLngToXY(hoveredDestination.coordinates.lat, hoveredDestination.coordinates.lng, dimensions.width, dimensions.height).y - 50,
                  10
                ),
              }}
            >
              <div className="flex items-start gap-3">
                <img
                  src={hoveredDestination.image}
                  alt={hoveredDestination.name}
                  className="w-16 h-16 rounded-lg object-cover"
                />
                <div>
                  <h4 className="font-bold text-gray-800">{hoveredDestination.name}</h4>
                  <p className="text-sm text-gray-500">{hoveredDestination.country}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-yellow-500">⭐</span>
                    <span className="text-sm font-medium">{hoveredDestination.rating}</span>
                    <span className="text-teal-600 font-bold text-sm">{hoveredDestination.price}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="p-4 bg-gray-50 border-t">
          <div className="flex flex-wrap items-center justify-center gap-4">
            <span className="text-sm text-gray-600 font-medium">Regions:</span>
            {Object.entries(regionColors).map(([region, color]) => (
              <div key={region} className="flex items-center gap-1">
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: color }}
                />
                <span className="text-sm text-gray-600 capitalize">{region}</span>
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-gray-400 mt-2">
            Click on any destination marker to view details
          </p>
        </div>

        {/* Selected destination info */}
        {selectedDestination && (
          <div className="p-4 bg-gradient-to-r from-teal-50 to-blue-50 border-t">
            <div className="flex items-center gap-4">
              <img
                src={selectedDestination.image}
                alt={selectedDestination.name}
                className="w-20 h-20 rounded-xl object-cover"
              />
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-800">
                  {selectedDestination.name}, {selectedDestination.country}
                </h3>
                <p className="text-sm text-gray-600 line-clamp-2">{selectedDestination.description}</p>
                <div className="flex items-center gap-4 mt-2">
                  <span className="text-yellow-500">⭐ {selectedDestination.rating}</span>
                  <span className="text-teal-600 font-bold">{selectedDestination.price}</span>
                  <span className="text-gray-500">{selectedDestination.duration}</span>
                </div>
              </div>
              <button
                onClick={() => {
                  onSelectDestination(selectedDestination);
                  onClose();
                }}
                className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
              >
                View Details
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
