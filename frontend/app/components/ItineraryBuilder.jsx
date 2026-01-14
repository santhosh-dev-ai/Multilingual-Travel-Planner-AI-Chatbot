'use client';

import { useState } from 'react';
import {
  CalendarIcon,
  MapPinIcon,
  ClockIcon,
  CurrencyDollarIcon,
  SparklesIcon,
  XMarkIcon,
  PencilIcon,
  ShareIcon,
  PrinterIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  BookmarkIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';
import { itineraryAPI, savedItineraryAPI } from '../services/api';

const INTERESTS = [
  'Adventure', 'Culture', 'Food', 'Nature', 'Photography',
  'Relaxation', 'History', 'Nightlife', 'Shopping', 'Art',
  'Architecture', 'Wildlife', 'Beach', 'Mountains', 'Spiritual'
];

const BUDGETS = [
  { value: 'budget', label: '💰 Budget', desc: 'Hostels, street food' },
  { value: 'moderate', label: '💵 Moderate', desc: 'Mid-range hotels, restaurants' },
  { value: 'luxury', label: '💎 Luxury', desc: 'Premium everything' },
];

const TRAVEL_STYLES = [
  { value: 'relaxed', label: '🌴 Relaxed', desc: '2-3 activities per day' },
  { value: 'balanced', label: '⚖️ Balanced', desc: '4-5 activities per day' },
  { value: 'packed', label: '🏃 Packed', desc: 'Maximum exploration' },
];

export default function ItineraryBuilder({ destination, onClose, onItineraryBuilt }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState(null);
  const [error, setError] = useState(null);
  const [expandedDay, setExpandedDay] = useState(1);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // Form state
  const [duration, setDuration] = useState(5);
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [budget, setBudget] = useState('moderate');
  const [travelStyle, setTravelStyle] = useState('balanced');
  const [customizing, setCustomizing] = useState(false);
  const [customizePrompt, setCustomizePrompt] = useState('');

  const toggleInterest = (interest) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter(i => i !== interest));
    } else if (selectedInterests.length < 5) {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const generateItinerary = async () => {
    if (selectedInterests.length === 0) {
      setError('Please select at least one interest');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await itineraryAPI.generate(
        destination?.name || destination,
        duration,
        selectedInterests,
        budget,
        travelStyle
      );
      setItinerary(result);
      setStep(3);
      // Notify parent that itinerary was built
      if (onItineraryBuilt) {
        onItineraryBuilt(destination?.id || destination);
      }
    } catch (err) {
      console.error('Itinerary generation error:', err);
      setError('Failed to generate itinerary. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const customizeItinerary = async () => {
    if (!customizePrompt.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await itineraryAPI.customize(itinerary, customizePrompt);
      setItinerary(result);
      setCustomizing(false);
      setCustomizePrompt('');
    } catch (err) {
      console.error('Customization error:', err);
      setError('Failed to customize itinerary. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    const shareText = `Check out my ${duration}-day trip to ${destination?.name || destination}! 🌍✈️\n\n${itinerary?.summary}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${duration}-Day Trip to ${destination?.name || destination}`,
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

  const handlePrint = () => {
    window.print();
  };

  const handleSaveItinerary = async () => {
    if (!itinerary || isSaving) return;
    
    setIsSaving(true);
    try {
      await savedItineraryAPI.save({
        destination: destination?.name || destination,
        destination_country: destination?.country || null,
        duration: itinerary.duration,
        travel_style: travelStyle,
        budget: budget,
        summary: itinerary.summary,
        days: itinerary.days,
        budget_estimate: itinerary.budget_estimate,
        packing_tips: itinerary.packing_tips,
        local_phrases: itinerary.local_phrases,
      });
      setIsSaved(true);
    } catch (err) {
      console.error('Failed to save itinerary:', err);
      setError('Failed to save itinerary. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 animate-fadeIn overflow-y-auto">
      <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl my-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
          <div className="flex items-center gap-3">
            <CalendarIcon className="w-6 h-6" />
            <div>
              <h2 className="text-xl font-bold">Trip Itinerary Builder</h2>
              <p className="text-sm opacity-90">
                {destination?.name || destination}
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

        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          {/* Step Indicator */}
          {!itinerary && (
            <div className="flex items-center justify-center gap-4 py-4 border-b bg-gray-50">
              {[1, 2].map(s => (
                <div key={s} className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    step >= s ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-500'
                  }`}>
                    {s}
                  </div>
                  <span className={step >= s ? 'text-gray-800' : 'text-gray-400'}>
                    {s === 1 ? 'Preferences' : 'Generate'}
                  </span>
                  {s < 2 && <div className="w-12 h-0.5 bg-gray-200" />}
                </div>
              ))}
            </div>
          )}

          {/* Step 1: Preferences */}
          {step === 1 && !loading && (
            <div className="p-6 space-y-6">
              {/* Duration */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Trip Duration
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="2"
                    max="14"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                  />
                  <div className="bg-purple-100 px-4 py-2 rounded-lg min-w-20 text-center">
                    <span className="text-2xl font-bold text-purple-600">{duration}</span>
                    <span className="text-sm text-gray-600"> days</span>
                  </div>
                </div>
              </div>

              {/* Interests */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Your Interests (select up to 5)
                </label>
                <div className="flex flex-wrap gap-2">
                  {INTERESTS.map(interest => (
                    <button
                      key={interest}
                      onClick={() => toggleInterest(interest)}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                        selectedInterests.includes(interest)
                          ? 'bg-purple-600 text-white shadow-lg scale-105'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      } ${
                        selectedInterests.length >= 5 && !selectedInterests.includes(interest)
                          ? 'opacity-50 cursor-not-allowed'
                          : ''
                      }`}
                    >
                      {interest}
                    </button>
                  ))}
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  {selectedInterests.length}/5 selected
                </p>
              </div>

              <button
                onClick={() => setStep(2)}
                disabled={selectedInterests.length === 0}
                className="w-full py-3 bg-purple-600 text-white rounded-xl font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue
              </button>
            </div>
          )}

          {/* Step 2: Budget & Style */}
          {step === 2 && !loading && !itinerary && (
            <div className="p-6 space-y-6">
              {/* Budget */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Budget Level
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {BUDGETS.map(b => (
                    <button
                      key={b.value}
                      onClick={() => setBudget(b.value)}
                      className={`p-4 rounded-xl text-left transition-all ${
                        budget === b.value
                          ? 'bg-purple-100 border-2 border-purple-600 shadow-lg'
                          : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                      }`}
                    >
                      <div className="text-lg font-bold text-gray-800">{b.label}</div>
                      <div className="text-xs text-gray-600">{b.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Travel Style */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Travel Pace
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {TRAVEL_STYLES.map(s => (
                    <button
                      key={s.value}
                      onClick={() => setTravelStyle(s.value)}
                      className={`p-4 rounded-xl text-left transition-all ${
                        travelStyle === s.value
                          ? 'bg-purple-100 border-2 border-purple-600 shadow-lg'
                          : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                      }`}
                    >
                      <div className="text-lg font-bold text-gray-800">{s.label}</div>
                      <div className="text-xs text-gray-600">{s.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {error && (
                <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 py-3 border-2 border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={generateItinerary}
                  className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-medium hover:from-purple-700 hover:to-indigo-700 transition-all flex items-center justify-center gap-2"
                >
                  <SparklesIcon className="w-5 h-5" />
                  Generate Itinerary
                </button>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
                <SparklesIcon className="w-8 h-8 text-purple-600 animate-pulse" />
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                {customizing ? 'Customizing your itinerary...' : 'Creating your perfect itinerary...'}
              </h3>
              <p className="text-gray-500">
                Our AI is crafting a personalized trip plan just for you
              </p>
              <div className="mt-6 flex justify-center gap-1">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="w-3 h-3 bg-purple-600 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Itinerary Display */}
          {itinerary && !loading && (
            <div className="p-6 space-y-6">
              {/* Summary */}
              <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-5">
                <h3 className="font-bold text-gray-800 mb-2">Trip Summary</h3>
                <p className="text-gray-600">{itinerary.summary}</p>
                <div className="flex flex-wrap gap-4 mt-4">
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CalendarIcon className="w-4 h-4 text-purple-600" />
                    <span>{itinerary.duration} days</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CurrencyDollarIcon className="w-4 h-4 text-purple-600" />
                    <span>{itinerary.budget_estimate}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button
                  onClick={handleSaveItinerary}
                  disabled={isSaving || isSaved}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg transition-colors ${
                    isSaved 
                      ? 'bg-green-100 text-green-600 border-2 border-green-200'
                      : 'border-2 border-purple-200 text-purple-600 hover:bg-purple-50'
                  }`}
                >
                  {isSaving ? (
                    <>
                      <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
                      Saving...
                    </>
                  ) : isSaved ? (
                    <>
                      <CheckIcon className="w-4 h-4" />
                      Saved!
                    </>
                  ) : (
                    <>
                      <BookmarkIcon className="w-4 h-4" />
                      Save
                    </>
                  )}
                </button>
                <button
                  onClick={() => setCustomizing(!customizing)}
                  className="flex-1 flex items-center justify-center gap-2 py-2 border-2 border-purple-200 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
                >
                  <PencilIcon className="w-4 h-4" />
                  Customize
                </button>
                <button
                  onClick={handleShare}
                  className="flex-1 flex items-center justify-center gap-2 py-2 border-2 border-purple-200 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
                >
                  <ShareIcon className="w-4 h-4" />
                  Share
                </button>
                <button
                  onClick={handlePrint}
                  className="flex-1 flex items-center justify-center gap-2 py-2 border-2 border-purple-200 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
                >
                  <PrinterIcon className="w-4 h-4" />
                  Print
                </button>
              </div>

              {/* Customize Input */}
              {customizing && (
                <div className="bg-gray-50 rounded-xl p-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What would you like to change?
                  </label>
                  <textarea
                    value={customizePrompt}
                    onChange={(e) => setCustomizePrompt(e.target.value)}
                    placeholder="E.g., 'Add more beach activities', 'Remove Day 3 and add a spa day', 'Make it more budget-friendly'"
                    className="w-full p-3 border rounded-lg resize-none h-24 focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  />
                  <button
                    onClick={customizeItinerary}
                    disabled={!customizePrompt.trim()}
                    className="mt-2 w-full py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
                  >
                    Apply Changes
                  </button>
                </div>
              )}

              {/* Daily Itinerary */}
              <div className="space-y-3">
                <h3 className="font-bold text-gray-800 text-lg">Daily Schedule</h3>
                
                {itinerary.days?.map((day) => (
                  <div key={day.day} className="border rounded-xl overflow-hidden">
                    <button
                      onClick={() => setExpandedDay(expandedDay === day.day ? null : day.day)}
                      className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                          {day.day}
                        </div>
                        <div className="text-left">
                          <div className="font-bold text-gray-800">{day.title}</div>
                          <div className="text-sm text-gray-500">
                            {day.activities?.length || 0} activities
                          </div>
                        </div>
                      </div>
                      {expandedDay === day.day ? (
                        <ChevronUpIcon className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDownIcon className="w-5 h-5 text-gray-400" />
                      )}
                    </button>
                    
                    {expandedDay === day.day && (
                      <div className="p-4 space-y-4 animate-slideDown">
                        {day.activities?.map((activity, idx) => (
                          <div key={idx} className="flex gap-4">
                            <div className="flex flex-col items-center">
                              <div className="w-3 h-3 bg-purple-600 rounded-full" />
                              {idx < day.activities.length - 1 && (
                                <div className="flex-1 w-0.5 bg-purple-200 my-1" />
                              )}
                            </div>
                            <div className="flex-1 pb-4">
                              <div className="flex items-start justify-between">
                                <div>
                                  <div className="flex items-center gap-2 text-sm text-purple-600 font-medium">
                                    <ClockIcon className="w-4 h-4" />
                                    {activity.time}
                                  </div>
                                  <h4 className="font-bold text-gray-800 mt-1">{activity.title}</h4>
                                  <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
                                  <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-500">
                                    <span className="flex items-center gap-1">
                                      <MapPinIcon className="w-3 h-3" />
                                      {activity.location}
                                    </span>
                                    <span>⏱️ {activity.duration}</span>
                                    {activity.cost && <span>💰 {activity.cost}</span>}
                                  </div>
                                  {activity.tips && (
                                    <div className="mt-2 text-xs bg-yellow-50 text-yellow-700 px-2 py-1 rounded inline-block">
                                      💡 {activity.tips}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        {/* Meals */}
                        {day.meals && (
                          <div className="bg-orange-50 rounded-lg p-3 mt-2">
                            <h5 className="font-medium text-orange-800 mb-2">🍽️ Meal Recommendations</h5>
                            <div className="grid grid-cols-3 gap-2 text-sm">
                              {day.meals.breakfast && (
                                <div>
                                  <span className="text-orange-600 font-medium">Breakfast:</span>
                                  <span className="text-gray-600 ml-1">{day.meals.breakfast}</span>
                                </div>
                              )}
                              {day.meals.lunch && (
                                <div>
                                  <span className="text-orange-600 font-medium">Lunch:</span>
                                  <span className="text-gray-600 ml-1">{day.meals.lunch}</span>
                                </div>
                              )}
                              {day.meals.dinner && (
                                <div>
                                  <span className="text-orange-600 font-medium">Dinner:</span>
                                  <span className="text-gray-600 ml-1">{day.meals.dinner}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {day.notes && (
                          <div className="text-sm text-gray-500 italic mt-2">
                            📝 {day.notes}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Packing Tips & Local Phrases */}
              <div className="grid md:grid-cols-2 gap-4">
                {itinerary.packing_tips?.length > 0 && (
                  <div className="bg-blue-50 rounded-xl p-4">
                    <h4 className="font-bold text-blue-800 mb-3">🎒 Packing Tips</h4>
                    <ul className="space-y-2">
                      {itinerary.packing_tips.map((tip, idx) => (
                        <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-blue-500">✓</span>
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {itinerary.local_phrases?.length > 0 && (
                  <div className="bg-green-50 rounded-xl p-4">
                    <h4 className="font-bold text-green-800 mb-3">🗣️ Useful Phrases</h4>
                    <div className="space-y-2">
                      {itinerary.local_phrases.map((phrase, idx) => (
                        <div key={idx} className="text-sm">
                          <span className="font-medium text-gray-800">{phrase.phrase}:</span>
                          <span className="text-gray-600 ml-1">{phrase.translation}</span>
                          {phrase.pronunciation && (
                            <span className="text-gray-400 ml-1 italic">({phrase.pronunciation})</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Generate New */}
              <button
                onClick={() => {
                  setItinerary(null);
                  setStep(1);
                  setSelectedInterests([]);
                }}
                className="w-full py-3 border-2 border-purple-200 text-purple-600 rounded-xl font-medium hover:bg-purple-50 transition-colors"
              >
                Start Over
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
