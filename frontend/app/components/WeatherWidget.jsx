'use client';

import { useState, useEffect } from 'react';
import { SunIcon, CloudIcon, MapPinIcon, CalendarDaysIcon } from '@heroicons/react/24/outline';
import { weatherAPI } from '../services/api';

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

export default function WeatherWidget({ destination, coordinates, compact = false, initialTab }) {
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(initialTab && initialTab === 'forecast' ? 'forecast' : 'current'); // 'current' or 'forecast'

  useEffect(() => {
    if (coordinates && coordinates.lat && coordinates.lon) {
      fetchWeatherData();
    } else {
      // Fallback to city name if coordinates not available
      fetchWeatherByCity();
    }
  }, [destination, coordinates]);

  useEffect(() => {
    if (forecast && forecast.forecast && forecast.forecast.length > 0) {
      setActiveTab('forecast');
    }
  }, [forecast]);

  const fetchWeatherData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch current weather
      const currentResponse = await weatherAPI.getCurrentByCoords(coordinates.lat, coordinates.lon);
      setCurrentWeather(currentResponse);

      // Fetch forecast
      const forecastResponse = await weatherAPI.getForecast(coordinates.lat, coordinates.lon, 7);
      setForecast(forecastResponse);
    } catch (err) {
      console.error('Weather fetch error:', err);
      setError('Unable to load weather data');
    } finally {
      setLoading(false);
    }
  };

  const fetchWeatherByCity = async () => {
    setLoading(true);
    setError(null);
    try {
      // Extract city name from destination string
      const cityName = destination.split(',')[0].trim();

      // Fetch current weather by city
      const currentResponse = await weatherAPI.getCurrentByCity(cityName);
      setCurrentWeather(currentResponse);

      // For forecast, we'd need coordinates, so we'll skip forecast for now
      setForecast(null);
    } catch (err) {
      console.error('Weather fetch error:', err);
      setError('Unable to load weather data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl p-4 text-white ${compact ? 'h-20' : 'h-32'} flex items-center justify-center`}>
        <div className="animate-pulse flex items-center gap-2">
          <SunIcon className="w-6 h-6 animate-spin" />
          <span>Loading weather...</span>
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

  if (!currentWeather) return null;

  return (
    <div className="bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 rounded-2xl p-5 text-white shadow-lg">
      {/* Header */}
      <div className="flex items-center gap-2 text-sm opacity-90 mb-4">
        <MapPinIcon className="w-4 h-4" />
        <span>{currentWeather.location}{currentWeather.country ? `, ${currentWeather.country}` : ''}</span>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveTab('current')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'current'
              ? 'bg-white/20 text-white'
              : 'text-white/70 hover:text-white hover:bg-white/10'
          }`}
        >
          Current
        </button>
        {forecast && (
          <button
            onClick={() => setActiveTab('forecast')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'forecast'
                ? 'bg-white/20 text-white'
                : 'text-white/70 hover:text-white hover:bg-white/10'
            }`}
          >
            7-Day Forecast
          </button>
        )}
      </div>

      {/* Current Weather */}
      {activeTab === 'current' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold mb-1">{Math.round(currentWeather.temperature)}°C</div>
              <div className="text-sm opacity-80">Feels like {Math.round(currentWeather.feels_like)}°C</div>
            </div>
            <div className="text-6xl">{getWeatherIcon(currentWeather.icon)}</div>
          </div>

          <div className="text-lg font-medium mb-3">{currentWeather.description}</div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="opacity-70">Humidity:</span>
              <span className="font-medium">{currentWeather.humidity}%</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="opacity-70">Wind:</span>
              <span className="font-medium">{currentWeather.wind_speed} m/s</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="opacity-70">Pressure:</span>
              <span className="font-medium">{currentWeather.pressure} hPa</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="opacity-70">Visibility:</span>
              <span className="font-medium">{(currentWeather.visibility / 1000).toFixed(1)} km</span>
            </div>
          </div>
        </div>
      )}

      {/* Forecast */}
      {activeTab === 'forecast' && forecast && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm opacity-90">
            <CalendarDaysIcon className="w-4 h-4" />
            <span>7-Day Forecast</span>
          </div>

          <div className="space-y-2">
            {forecast.forecast.map((day, idx) => (
              <div key={idx} className="flex items-center justify-between bg-white/10 rounded-lg p-3">
                <div className="flex items-center gap-3">
                  <span className="text-lg">{getWeatherIcon(day.icon)}</span>
                  <div>
                    <div className="font-medium text-sm">
                      {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                    </div>
                    <div className="text-xs opacity-80">{day.description}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-sm">{Math.round(day.temp_max)}°</div>
                  <div className="text-xs opacity-70">{Math.round(day.temp_min)}°</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
