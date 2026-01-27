'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import {
  CalendarIcon,
  MapPinIcon,
  TrashIcon,
  EyeIcon,
  ShareIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ClockIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline';
import { savedItineraryAPI } from '../services/api';

export default function SavedItineraries({ isOpen, onClose, translations }) {
  const [itineraries, setItineraries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItinerary, setSelectedItinerary] = useState(null);
  const [expandedDay, setExpandedDay] = useState(1);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchItineraries();
    }
  }, [isOpen]);

  const fetchItineraries = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await savedItineraryAPI.getAll();
      setItineraries(response.data || []);
    } catch (err) {
      console.error('Failed to fetch itineraries:', err);
      setError('Failed to load saved itineraries');
    } finally {
      setLoading(false);
    }
  };

  const deleteItinerary = async (itineraryId) => {
    if (!confirm('Are you sure you want to delete this itinerary?')) return;
    
    try {
      await savedItineraryAPI.delete(itineraryId);
      setItineraries(itineraries.filter(item => item.id !== itineraryId));
      if (selectedItinerary?.id === itineraryId) {
        setSelectedItinerary(null);
      }
    } catch (err) {
      console.error('Failed to delete itinerary:', err);
      alert('Failed to delete itinerary');
    }
  };

  const shareItinerary = async (itinerary) => {
    const shareText = `Check out my ${itinerary.duration}-day trip to ${itinerary.destination}! 🌍✈️\n\n${itinerary.summary}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${itinerary.duration}-Day Trip to ${itinerary.destination}`,
          text: shareText,
          url: window.location.href,
        });
      } catch (err) {
        console.log('Share cancelled');
      }
    } else {
      await navigator.clipboard.writeText(shareText);
      alert('Itinerary summary copied to clipboard!');
    }
  };

  if (!isOpen) return null;

  const modalContent = (
    <div className="fixed inset-0 bg-black/80 z-[9999] flex items-center justify-center p-4 animate-fadeIn overflow-y-auto">
      <div className="bg-[#1E293B] rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden shadow-2xl my-auto border border-[#334155]">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#334155] bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white">
          <div className="flex items-center gap-3">
            <CalendarIcon className="w-6 h-6" />
            <div>
              <h2 className="text-xl font-bold">{translations?.savedItineraries?.title || 'My Saved Itineraries'}</h2>
              <p className="text-sm opacity-90">
                {itineraries.length} {translations?.savedItineraries?.savedTrips || 'saved trip'}{itineraries.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <div className="flex h-[calc(90vh-80px)]">
          {/* Itineraries List */}
          <div className="w-1/3 border-r border-[#334155] overflow-y-auto bg-[#0F172A]">
            {loading ? (
              <div className="p-6 text-center">
                <div className="animate-spin w-8 h-8 border-2 border-[#3AA8C1] border-t-transparent rounded-full mx-auto mb-2"></div>
                <p className="text-[#94A3B8]">{translations?.savedItineraries?.loading || 'Loading itineraries...'}</p>
              </div>
            ) : error ? (
              <div className="p-6 text-center text-red-400">
                <p>{error}</p>
                <button 
                  onClick={fetchItineraries}
                  className="mt-2 px-4 py-2 bg-[#3AA8C1] text-white rounded-lg hover:bg-[#2B8FA8]"
                >
                  {translations?.savedItineraries?.retry || 'Retry'}
                </button>
              </div>
            ) : itineraries.length === 0 ? (
              <div className="p-6 text-center text-[#94A3B8]">
                <CalendarIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>{translations?.savedItineraries?.noItineraries || 'No saved itineraries yet'}</p>
                <p className="text-sm mt-1">{translations?.savedItineraries?.createFirst || 'Create your first itinerary to see it here!'}</p>
              </div>
            ) : (
              <div className="p-4 space-y-3">
                {itineraries.map((itinerary) => (
                  <div
                    key={itinerary.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedItinerary?.id === itinerary.id
                        ? 'border-[#3AA8C1] bg-[#3AA8C1]/10'
                        : 'border-[#334155] hover:border-[#3AA8C1]/50 hover:bg-[#334155]/50'
                    }`}
                    onClick={() => setSelectedItinerary(itinerary)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-bold text-white">{itinerary.destination}</h3>
                        <p className="text-sm text-[#94A3B8] mb-2">
                          {itinerary.destination_country}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-[#CBD5E1]">
                          <span className="flex items-center gap-1">
                            <CalendarIcon className="w-3 h-3" />
                            {itinerary.duration} days
                          </span>
                          <span className="flex items-center gap-1">
                            <CurrencyDollarIcon className="w-3 h-3" />
                            {itinerary.budget}
                          </span>
                        </div>
                        <p className="text-xs text-[#64748B] mt-2">
                          {new Date(itinerary.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            shareItinerary(itinerary);
                          }}
                          className="p-1 text-[#64748B] hover:text-[#3AA8C1] transition-colors"
                        >
                          <ShareIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteItinerary(itinerary.id);
                          }}
                          className="p-1 text-[#64748B] hover:text-red-400 transition-colors"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Itinerary Details */}
          <div className="flex-1 overflow-y-auto bg-[#1E293B]">
            {selectedItinerary ? (
              <div className="p-6 space-y-6">
                {/* Summary */}
                <div className="bg-gradient-to-r from-[#3AA8C1]/10 to-[#58B8CD]/10 rounded-xl p-5 border border-[#3AA8C1]/20">
                  <h3 className="font-bold text-white mb-2">{translations?.savedItineraries?.tripSummary || 'Trip Summary'}</h3>
                  <p className="text-[#CBD5E1]">{selectedItinerary.summary}</p>
                  <div className="flex flex-wrap gap-4 mt-4">
                    <div className="flex items-center gap-2 text-sm text-[#CBD5E1]">
                      <CalendarIcon className="w-4 h-4 text-[#3AA8C1]" />
                      <span>{selectedItinerary.duration} days</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-[#CBD5E1]">
                      <CurrencyDollarIcon className="w-4 h-4 text-[#3AA8C1]" />
                      <span>{selectedItinerary.budget_estimate}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-[#CBD5E1]">
                      <MapPinIcon className="w-4 h-4 text-[#3AA8C1]" />
                      <span>{selectedItinerary.travel_style} pace</span>
                    </div>
                  </div>
                </div>

                {/* Daily Itinerary */}
                <div className="space-y-3">
                  <h3 className="font-bold text-white text-lg">{translations?.savedItineraries?.dailySchedule || 'Daily Schedule'}</h3>
                  
                  {selectedItinerary.days?.map((day) => (
                    <div key={day.day} className="border border-[#334155] rounded-xl overflow-hidden">
                      <button
                        onClick={() => setExpandedDay(expandedDay === day.day ? null : day.day)}
                        className="w-full flex items-center justify-between p-4 bg-[#334155]/50 hover:bg-[#334155] transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-[#3AA8C1] text-white rounded-full flex items-center justify-center font-bold">
                            {day.day}
                          </div>
                          <div className="text-left">
                            <div className="font-bold text-white">{day.title}</div>
                            <div className="text-sm text-[#94A3B8]">
                              {day.activities?.length || 0} {translations?.savedItineraries?.activities || 'activities'}
                            </div>
                          </div>
                        </div>
                        {expandedDay === day.day ? (
                          <ChevronUpIcon className="w-5 h-5 text-[#94A3B8]" />
                        ) : (
                          <ChevronDownIcon className="w-5 h-5 text-[#94A3B8]" />
                        )}
                      </button>
                      
                      {expandedDay === day.day && (
                        <div className="p-4 space-y-4 animate-slideDown bg-[#1E293B]">
                          {day.activities?.map((activity, idx) => (
                            <div key={idx} className="flex gap-4">
                              <div className="flex flex-col items-center">
                                <div className="w-3 h-3 bg-[#3AA8C1] rounded-full" />
                                {idx < day.activities.length - 1 && (
                                  <div className="flex-1 w-0.5 bg-[#3AA8C1]/30 my-1 min-h-[60px]" />
                                )}
                              </div>
                              <div className="flex-1 pb-4">
                                <div className="flex items-start justify-between">
                                  <div>
                                    <div className="flex items-center gap-2 text-sm text-[#3AA8C1] font-medium">
                                      <ClockIcon className="w-4 h-4" />
                                      {activity.time}
                                    </div>
                                    <h4 className="font-bold text-white mt-1">{activity.title}</h4>
                                    <p className="text-sm text-[#CBD5E1] mt-1">{activity.description}</p>
                                    <div className="flex flex-wrap gap-3 mt-2 text-xs text-[#94A3B8]">
                                      <span className="flex items-center gap-1">
                                        <MapPinIcon className="w-3 h-3" />
                                        {activity.location}
                                      </span>
                                      <span>⏱️ {activity.duration}</span>
                                      {activity.cost && <span>💰 {activity.cost}</span>}
                                    </div>
                                    {activity.tips && (
                                      <div className="mt-2 text-xs bg-yellow-500/20 text-yellow-300 px-2 py-1 rounded inline-block border border-yellow-500/30">
                                        💡 {activity.tips}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Packing Tips & Local Phrases */}
                <div className="grid md:grid-cols-2 gap-4">
                  {selectedItinerary.packing_tips?.length > 0 && (
                    <div className="bg-blue-500/10 rounded-xl p-4 border border-blue-500/20">
                      <h4 className="font-bold text-blue-300 mb-3">🎒 {translations?.savedItineraries?.packingTips || 'Packing Tips'}</h4>
                      <ul className="space-y-2">
                        {selectedItinerary.packing_tips.map((tip, idx) => (
                          <li key={idx} className="text-sm text-[#CBD5E1] flex items-start gap-2">
                            <span className="text-blue-400">✓</span>
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {selectedItinerary.local_phrases?.length > 0 && (
                    <div className="bg-green-500/10 rounded-xl p-4 border border-green-500/20">
                      <h4 className="font-bold text-green-300 mb-3">🗣️ {translations?.savedItineraries?.usefulPhrases || 'Useful Phrases'}</h4>
                      <div className="space-y-2">
                        {selectedItinerary.local_phrases.map((phrase, idx) => (
                          <div key={idx} className="text-sm">
                            <span className="font-medium text-white">{phrase.phrase}:</span>
                            <span className="text-[#CBD5E1] ml-1">{phrase.translation}</span>
                            {phrase.pronunciation && (
                              <span className="text-[#94A3B8] ml-1 italic">({phrase.pronunciation})</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8]">
                <div className="text-center">
                  <EyeIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>{translations?.savedItineraries?.selectItinerary || 'Select an itinerary to view details'}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return typeof window !== 'undefined' ? createPortal(modalContent, document.body) : null;
}