'use client';

import { useState, useEffect } from 'react';
import { SunIcon, CloudIcon, MapPinIcon } from '@heroicons/react/24/outline';
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

export default function WeatherWidget({ destination, coordinates, compact = false }) {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForecast, setShowForecast] = useState(false);

  useEffect(() => {
    fetchWeather();
  }, [destination, coordinates]);

  const fetchWeather = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let weatherData;
      
      if (coordinates?.lat && coordinates?.lng) {
        weatherData = await weatherAPI.getCurrentByCoords(coordinates.lat, coordinates.lng);
      } else if (destination) {
        weatherData = await weatherAPI.getCurrentByCity(destination);
      } else {
        throw new Error('No location provided');
      }
      
      setWeather(weatherData);
      
      // Fetch forecast if coordinates available
      if (coordinates?.lat && coordinates?.lng) {
        const forecastData = await weatherAPI.getForecast(coordinates.lat, coordinates.lng, 5);
        setForecast(forecastData.forecast);
      }
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

  if (!weather) return null;

  if (compact) {
    return (
      <div className="bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl p-3 text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{getWeatherIcon(weather.icon)}</span>
          <div>
            <div className="text-lg font-bold">{Math.round(weather.temperature)}°C</div>
            <div className="text-xs opacity-90">{weather.description}</div>
          </div>
        </div>
        <div className="text-xs opacity-75">
          <div>Humidity: {weather.humidity}%</div>
          <div>Wind: {weather.wind_speed} m/s</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 rounded-2xl p-5 text-white shadow-lg">
      {/* Current Weather */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 text-sm opacity-90 mb-1">
            <MapPinIcon className="w-4 h-4" />
            {weather.location}{weather.country ? `, ${weather.country}` : ''}
          </div>
          <div className="flex items-center gap-3">
            <span className="text-5xl">{getWeatherIcon(weather.icon)}</span>
            <div>
              <div className="text-4xl font-bold">{Math.round(weather.temperature)}°C</div>
              <div className="text-sm opacity-90">Feels like {Math.round(weather.feels_like)}°C</div>
            </div>
          </div>
        </div>
        <div className="text-right text-sm">
          <div className="bg-white/20 rounded-lg px-3 py-2">
            <div className="font-semibold">{weather.description}</div>
          </div>
        </div>
      </div>

      {/* Weather Details */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="bg-white/10 rounded-lg p-2 text-center">
          <div className="text-xs opacity-75">Humidity</div>
          <div className="font-semibold">{weather.humidity}%</div>
        </div>
        <div className="bg-white/10 rounded-lg p-2 text-center">
          <div className="text-xs opacity-75">Wind</div>
          <div className="font-semibold">{weather.wind_speed} m/s</div>
        </div>
        <div className="bg-white/10 rounded-lg p-2 text-center">
          <div className="text-xs opacity-75">Pressure</div>
          <div className="font-semibold">{weather.pressure} hPa</div>
        </div>
        <div className="bg-white/10 rounded-lg p-2 text-center">
          <div className="text-xs opacity-75">Clouds</div>
          <div className="font-semibold">{weather.clouds}%</div>
        </div>
      </div>

      {/* Forecast Toggle */}
      {forecast && forecast.length > 0 && (
        <>
          <button
            onClick={() => setShowForecast(!showForecast)}
            className="w-full text-center text-sm bg-white/10 hover:bg-white/20 rounded-lg py-2 transition-colors mb-3"
          >
            {showForecast ? 'Hide Forecast' : 'Show 5-Day Forecast'}
          </button>
          
          {showForecast && (
            <div className="grid grid-cols-5 gap-2">
              {forecast.map((day, index) => (
                <div key={index} className="bg-white/10 rounded-lg p-2 text-center">
                  <div className="text-xs opacity-75">
                    {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                  </div>
                  <div className="text-xl my-1">{getWeatherIcon(day.icon)}</div>
                  <div className="text-xs">
                    <span className="font-semibold">{Math.round(day.temp_max)}°</span>
                    <span className="opacity-75"> / {Math.round(day.temp_min)}°</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
      
      {weather.note && (
        <div className="text-xs text-center opacity-75 mt-3">
          ⚠️ {weather.note}
        </div>
      )}
    </div>
  );
}
