'use client';

import { useState, useEffect } from 'react';
import { SunIcon, CloudIcon, MapPinIcon } from '@heroicons/react/24/outline';
import { chatAPI } from '../services/api';

// Weather icon mapping
const getWeatherIcon = (iconCode) => {
  const iconMap = {
    '01d': '☀️', '01n': '🌙',
    '02d': '⛅', '02n': '☁️',
    '03d': '☁️', '03n': '☁️',
    '04d': '☁️', '04n': '☁️',
    '09d': '🌧️', '09n': '🌧️',
    '10d': '🌦️', '10n': '🌧️',
    '11d': '⛈️', '11n': '⛈️',
    '13d': '❄️', '13n': '❄️',
    '50d': '🌫️', '50n': '🌫️',
  };
  return iconMap[iconCode] || '🌡️';
};

export default function WeatherWidget({ destination, coordinates, compact = false }) {
  const [seasonalInfo, setSeasonalInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSeasonalInfo();
  }, [destination]);

  const fetchSeasonalInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      if (!destination) throw new Error('No destination provided');
      const prompt = `Describe the typical seasons, average temperatures, and weather conditions throughout the year for ${destination}. Format as JSON: {"seasons": [{"name": "Summer", "months": "June-August", "avg_temp": "25-30°C", "weather": "Sunny, dry"}, ...]}`;
      const response = await chatAPI.sendMessage(prompt);
      // Expecting response to contain a JSON string or object
      let info = response?.content;
      if (typeof info === 'string') {
        info = JSON.parse(info);
      }
      setSeasonalInfo(info);
    } catch (err) {
      console.error('Seasonal info fetch error:', err);
      setError('Unable to load seasonal weather info');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl p-4 text-white ${compact ? 'h-20' : 'h-32'} flex items-center justify-center`}>
        <div className="animate-pulse flex items-center gap-2">
          <SunIcon className="w-6 h-6 animate-spin" />
          <span>Loading seasonal info...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-gradient-to-br from-gray-400 to-gray-600 rounded-xl p-4 text-white ${compact ? 'h-20' : 'h-32'} flex items-center justify-center`}>
        <CloudIcon className="w-6 h-6 mr-2" />
        <span className="text-sm">{error}</span>
      </div>
    );
  }

  if (!seasonalInfo || !seasonalInfo.seasons) return null;

  return (
    <div className="bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 rounded-2xl p-5 text-white shadow-lg">
      <div className="mb-4">
        <div className="flex items-center gap-2 text-sm opacity-90 mb-1">
          <MapPinIcon className="w-4 h-4" />
          {destination}
        </div>
        <div className="font-bold text-lg mb-2">Typical Seasons & Weather</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {seasonalInfo.seasons.map((season, idx) => (
            <div key={idx} className="bg-white/10 rounded-lg p-3">
              <div className="font-semibold text-base mb-1">{season.name}</div>
              <div className="text-xs opacity-80 mb-1">Months: {season.months}</div>
              <div className="text-sm">Avg Temp: {season.avg_temp}</div>
              <div className="text-sm">Weather: {season.weather}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
