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
import { itineraryAPI, chatAPI, savedItineraryAPI } from '../services/api';

const INTERESTS = [
  'Adventure', 'Culture', 'Food', 'Nature', 'Photography',
  'Relaxation', 'History', 'Nightlife', 'Shopping', 'Art',
  'Architecture', 'Wildlife', 'Beach', 'Mountains', 'Spiritual'
];

const getBudgetLabel = (amount) => {
  if (amount <= 300) return { emoji: '💰', label: 'Ultra Budget', desc: 'Hostels, street food, free activities' };
  if (amount <= 600) return { emoji: '💵', label: 'Budget', desc: 'Budget hotels, local restaurants' };
  if (amount <= 1200) return { emoji: '💳', label: 'Moderate', desc: 'Mid-range hotels, nice restaurants' };
  return { emoji: '💎', label: 'Luxury', desc: 'Premium hotels, fine dining' };
};

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
  const [budgetAmount, setBudgetAmount] = useState(500);
  const [travelStyle, setTravelStyle] = useState('balanced');
  // ...existing code...

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
        `$${budgetAmount}`,
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

  // Removed customizeItinerary logic

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
      // Save to database
      const itineraryData = {
        destination: destination?.name || destination,
        destination_country: destination?.country || 'Unknown',
        duration: itinerary.duration,
        travel_style: travelStyle,
        budget: `$${budgetAmount}`,
        summary: itinerary.summary,
        days: itinerary.days,
        budget_estimate: itinerary.budget_estimate,
        packing_tips: itinerary.packing_tips || [],
        local_phrases: itinerary.local_phrases || []
      };

      const response = await savedItineraryAPI.save(itineraryData);
      if (!response.success) {
        throw new Error(response.message || 'Failed to save itinerary');
      }

      setIsSaved(true);
      
      // Notify parent that itinerary was saved
      if (onItineraryBuilt) {
        onItineraryBuilt();
      }
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
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-[#3AA8C1] via-[#58B8CD] to-[#3E8EDE] text-white">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
              <CalendarIcon className="w-7 h-7" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight">Trip Itinerary Builder</h2>
              <p className="text-sm opacity-90 font-medium">
                ✈️ {destination?.name || destination}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-3 hover:bg-white/20 rounded-xl transition-all duration-200 backdrop-blur-sm hover:scale-105"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          {/* Step Indicator */}
          {!itinerary && (
            <div className="flex items-center justify-center gap-6 py-6 border-b bg-gradient-to-r from-[#DEF1F5] to-[#F8FAFB]">
              {[1, 2].map(s => (
                <div key={s} className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg transition-all duration-300 ${
                    step >= s 
                      ? 'bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white shadow-lg scale-105' 
                      : 'bg-white text-[#A3A3A3] border-2 border-[#E2E8F0]'
                  }`}>
                    {s}
                  </div>
                  <span className={`font-semibold transition-colors ${
                    step >= s ? 'text-[#0F172A]' : 'text-[#94A3B8]'
                  }`}>
                    {s === 1 ? 'Preferences' : 'Generate'}
                  </span>
                  {s < 2 && <div className="w-16 h-1 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] rounded-full opacity-30" />}
                </div>
              ))}
            </div>
          )}

          {/* Step 1: Preferences */}
          {step === 1 && !loading && (
            <div className="p-8 space-y-8">
              {/* Duration */}
              <div className="space-y-4">
                <label className="block text-lg font-semibold text-[#0F172A] mb-4">
                  🗓️ Trip Duration
                </label>
                <div className="flex items-center gap-6">
                  <input
                    type="range"
                    min="2"
                    max="14"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    className="flex-1 h-3 bg-gradient-to-r from-[#DEF1F5] to-[#BCE2EB] rounded-full appearance-none cursor-pointer slider-thumb"
                    style={{
                      background: `linear-gradient(to right, #3AA8C1 0%, #3AA8C1 ${((duration-2)/(14-2))*100}%, #E2E8F0 ${((duration-2)/(14-2))*100}%, #E2E8F0 100%)`
                    }}
                  />
                  <div className="bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] px-6 py-3 rounded-xl min-w-28 text-center shadow-lg">
                    <span className="text-3xl font-bold text-white">{duration}</span>
                    <span className="text-sm text-white/90 block font-medium">days</span>
                  </div>
                </div>
              </div>

              {/* Interests */}
              <div className="space-y-4">
                <label className="block text-lg font-semibold text-[#0F172A] mb-4">
                  🎯 Your Interests (select up to 5)
                </label>
                <div className="flex flex-wrap gap-3">
                  {INTERESTS.map(interest => (
                    <button
                      key={interest}
                      onClick={() => toggleInterest(interest)}
                      className={`px-5 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
                        selectedInterests.includes(interest)
                          ? 'bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white shadow-lg scale-105 border-2 border-[#3AA8C1]'
                          : 'bg-white text-[#475569] hover:bg-[#F8FAFB] border-2 border-[#E2E8F0] hover:border-[#3AA8C1] hover:scale-102'
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
                <div className="flex items-center gap-2 mt-3">
                  <div className={`w-3 h-3 rounded-full ${
                    selectedInterests.length > 0 ? 'bg-[#10B981]' : 'bg-[#E2E8F0]'
                  }`} />
                  <p className="text-sm text-[#475569] font-medium">
                    {selectedInterests.length}/5 interests selected
                  </p>
                </div>
              </div>

              <button
                onClick={() => setStep(2)}
                disabled={selectedInterests.length === 0}
                className="w-full py-4 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white rounded-xl font-semibold text-lg hover:from-[#308CA0] hover:to-[#4AA5BA] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]"
              >
                Continue to Budget & Style →
              </button>
            </div>
          )}

          {/* Step 2: Budget & Style */}
          {step === 2 && !loading && !itinerary && (
            <div className="p-6 space-y-6">
              {/* Budget Slider */}
              <div className="space-y-5">
                <label className="block text-lg font-semibold text-[#0F172A] mb-4">
                  💰 Your Budget (Total Trip Cost)
                </label>
                <div className="space-y-6">
                  <div className="flex items-center gap-6">
                    <input
                      type="range"
                      min="150"
                      max="2000"
                      step="50"
                      value={budgetAmount}
                      onChange={(e) => setBudgetAmount(parseInt(e.target.value))}
                      className="flex-1 h-3 bg-gradient-to-r from-[#DEF1F5] to-[#BCE2EB] rounded-full appearance-none cursor-pointer slider-thumb"
                      style={{
                        background: `linear-gradient(to right, #3AA8C1 0%, #3AA8C1 ${((budgetAmount-150)/(2000-150))*100}%, #E2E8F0 ${((budgetAmount-150)/(2000-150))*100}%, #E2E8F0 100%)`
                      }}
                    />
                    <div className="bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] px-6 py-3 rounded-xl min-w-32 text-center shadow-lg">
                      <span className="text-2xl font-bold text-white">${budgetAmount}</span>
                    </div>
                  </div>
                  <div className="bg-gradient-to-r from-[#F8FAFB] to-[#DEF1F5] rounded-xl p-5 border border-[#BCE2EB]">
                    <div className="flex items-center gap-4">
                      <span className="text-3xl">{getBudgetLabel(budgetAmount).emoji}</span>
                      <div>
                        <div className="font-bold text-[#0F172A] text-lg">{getBudgetLabel(budgetAmount).label}</div>
                        <div className="text-sm text-[#475569] font-medium">{getBudgetLabel(budgetAmount).desc}</div>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-3">
                    {[200, 400, 800, 1500].map(amount => (
                      <button 
                        key={amount}
                        onClick={() => setBudgetAmount(amount)} 
                        className="p-3 bg-white border-2 border-[#E2E8F0] rounded-xl hover:border-[#3AA8C1] hover:bg-[#F8FAFB] transition-all duration-200 text-sm font-semibold text-[#475569] hover:text-[#3AA8C1] hover:scale-105"
                      >
                        ${amount}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Travel Style */}
              <div className="space-y-4">
                <label className="block text-lg font-semibold text-[#0F172A] mb-4">
                  ⚡ Travel Pace
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {TRAVEL_STYLES.map(s => (
                    <button
                      key={s.value}
                      onClick={() => setTravelStyle(s.value)}
                      className={`p-5 rounded-xl text-left transition-all duration-200 border-2 ${
                        travelStyle === s.value
                          ? 'bg-gradient-to-br from-[#DEF1F5] to-[#BCE2EB] border-[#3AA8C1] shadow-lg scale-105'
                          : 'bg-white border-[#E2E8F0] hover:border-[#3AA8C1] hover:bg-[#F8FAFB] hover:scale-102'
                      }`}
                    >
                      <div className="text-xl font-bold text-[#0F172A] mb-1">{s.label}</div>
                      <div className="text-sm text-[#475569] font-medium">{s.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {error && (
                <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <div className="flex gap-4">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 py-4 border-2 border-[#E2E8F0] text-[#475569] rounded-xl font-semibold hover:bg-[#F8FAFB] hover:border-[#3AA8C1] transition-all duration-200 hover:scale-[1.02]"
                >
                  ← Back
                </button>
                <button
                  onClick={generateItinerary}
                  className="flex-1 py-4 bg-gradient-to-r from-[#3AA8C1] via-[#58B8CD] to-[#3E8EDE] text-white rounded-xl font-semibold hover:from-[#308CA0] hover:via-[#4AA5BA] hover:to-[#2377CB] transition-all duration-200 flex items-center justify-center gap-3 shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]"
                >
                  <SparklesIcon className="w-6 h-6" />
                  Generate Itinerary ✨
                </button>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="p-16 text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-[#DEF1F5] to-[#BCE2EB] rounded-2xl mb-6 shadow-lg">
                <SparklesIcon className="w-10 h-10 text-[#3AA8C1] animate-pulse" />
              </div>
              <h3 className="text-2xl font-bold text-[#0F172A] mb-3">
                Creating your perfect itinerary... ✨
              </h3>
              <p className="text-[#475569] text-lg font-medium mb-8">
                Our AI is crafting a personalized ${budgetAmount} trip plan just for you
              </p>
              <div className="flex justify-center gap-2">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="w-4 h-4 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] rounded-full animate-bounce shadow-lg"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Itinerary Display */}
          {itinerary && !loading && (
            <div className="p-8 space-y-8">
              {/* Summary */}
              <div className="bg-gradient-to-br from-[#DEF1F5] via-[#F8FAFB] to-[#BCE2EB] rounded-2xl p-6 border border-[#3AA8C1]/20 shadow-lg">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] rounded-xl shadow-lg">
                    <SparklesIcon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-[#0F172A] text-xl mb-3">🎯 Trip Summary</h3>
                    <p className="text-[#475569] text-lg leading-relaxed">{itinerary.summary}</p>
                    <div className="flex flex-wrap gap-6 mt-5">
                      <div className="flex items-center gap-3 text-[#0F172A]">
                        <div className="p-2 bg-white/60 rounded-lg">
                          <CalendarIcon className="w-5 h-5 text-[#3AA8C1]" />
                        </div>
                        <span className="font-semibold">{itinerary.duration} days</span>
                      </div>
                      <div className="flex items-center gap-3 text-[#0F172A]">
                        <div className="p-2 bg-white/60 rounded-lg">
                          <CurrencyDollarIcon className="w-5 h-5 text-[#00A86B]" />
                        </div>
                        <span className="font-semibold">{itinerary.budget_estimate}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={handleSaveItinerary}
                  disabled={isSaving || isSaved}
                  className={`flex-1 flex items-center justify-center gap-3 py-3 rounded-xl transition-all duration-200 font-semibold ${
                    isSaved 
                      ? 'bg-gradient-to-r from-[#10B981] to-[#059669] text-white shadow-lg'
                      : 'border-2 border-[#3AA8C1] text-[#3AA8C1] hover:bg-[#3AA8C1] hover:text-white shadow-lg hover:shadow-xl'
                  }`}
                >
                  {isSaving ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Saving...
                    </>
                  ) : isSaved ? (
                    <>
                      <CheckIcon className="w-5 h-5" />
                      Saved! ✅
                    </>
                  ) : (
                    <>
                      <BookmarkIcon className="w-5 h-5" />
                      Save Itinerary
                    </>
                  )}
                </button>
                <button
                  onClick={handleShare}
                  className="flex-1 flex items-center justify-center gap-3 py-3 border-2 border-[#3AA8C1] text-[#3AA8C1] rounded-xl hover:bg-[#3AA8C1] hover:text-white transition-all duration-200 font-semibold shadow-lg hover:shadow-xl"
                >
                  <ShareIcon className="w-5 h-5" />
                  Share
                </button>
                <button
                  onClick={handlePrint}
                  className="flex-1 flex items-center justify-center gap-3 py-3 border-2 border-[#3AA8C1] text-[#3AA8C1] rounded-xl hover:bg-[#3AA8C1] hover:text-white transition-all duration-200 font-semibold shadow-lg hover:shadow-xl"
                >
                  <PrinterIcon className="w-5 h-5" />
                  Print
                </button>
              </div>

              {/* Customize input removed */}

              {/* Daily Itinerary */}
              <div className="space-y-4">
                <h3 className="font-bold text-[#0F172A] text-2xl flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] rounded-lg">
                    <ClockIcon className="w-6 h-6 text-white" />
                  </div>
                  Daily Schedule
                </h3>
                
                {itinerary.days?.map((day) => (
                  <div key={day.day} className="border-2 border-[#E2E8F0] rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-all duration-200">
                    <button
                      onClick={() => setExpandedDay(expandedDay === day.day ? null : day.day)}
                      className="w-full flex items-center justify-between p-6 bg-gradient-to-r from-[#F8FAFB] to-[#DEF1F5] hover:from-[#DEF1F5] hover:to-[#BCE2EB] transition-all duration-200"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white rounded-xl flex items-center justify-center font-bold text-lg shadow-lg">
                          {day.day}
                        </div>
                        <div className="text-left">
                          <div className="font-bold text-[#0F172A] text-lg">{day.title}</div>
                          <div className="text-sm text-[#475569] font-medium">
                            {day.activities?.length || 0} activities planned
                          </div>
                        </div>
                      </div>
                      <div className="p-2 bg-white/60 rounded-lg">
                        {expandedDay === day.day ? (
                          <ChevronUpIcon className="w-6 h-6 text-[#3AA8C1]" />
                        ) : (
                          <ChevronDownIcon className="w-6 h-6 text-[#3AA8C1]" />
                        )}
                      </div>
                    </button>
                    
                    {expandedDay === day.day && (
                      <div className="p-6 space-y-6 bg-white animate-slideDown">
                        {day.activities?.map((activity, idx) => (
                          <div key={idx} className="flex gap-5">
                            <div className="flex flex-col items-center">
                              <div className="w-4 h-4 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] rounded-full shadow-lg" />
                              {idx < day.activities.length - 1 && (
                                <div className="flex-1 w-0.5 bg-gradient-to-b from-[#3AA8C1] to-[#BCE2EB] my-2 min-h-[60px]" />
                              )}
                            </div>
                            <div className="flex-1 pb-4">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-3 text-sm text-[#3AA8C1] font-semibold mb-2">
                                    <div className="p-1 bg-[#DEF1F5] rounded">
                                      <ClockIcon className="w-4 h-4" />
                                    </div>
                                    {activity.time}
                                  </div>
                                  <h4 className="font-bold text-[#0F172A] text-lg mb-2">{activity.title}</h4>
                                  <p className="text-[#475569] mb-3 leading-relaxed">{activity.description}</p>
                                  <div className="flex flex-wrap gap-4 text-sm">
                                    <span className="flex items-center gap-2 text-[#475569] bg-[#F8FAFB] px-3 py-1 rounded-lg">
                                      <MapPinIcon className="w-4 h-4 text-[#3AA8C1]" />
                                      {activity.location}
                                    </span>
                                    <span className="bg-[#DEF1F5] text-[#3AA8C1] px-3 py-1 rounded-lg font-medium">
                                      ⏱️ {activity.duration}
                                    </span>
                                    {activity.cost && (
                                      <span className="bg-[#C6FFEA] text-[#00A86B] px-3 py-1 rounded-lg font-medium">
                                        💰 {activity.cost}
                                      </span>
                                    )}
                                  </div>
                                  {activity.tips && (
                                    <div className="mt-3 text-sm bg-gradient-to-r from-[#FEF3C7] to-[#FDE68A] text-[#92400E] px-4 py-2 rounded-lg border border-[#F59E0B]/20">
                                      💡 <span className="font-medium">{activity.tips}</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        {/* Meals */}
                        {day.meals && (
                          <div className="bg-gradient-to-r from-[#FEF3C7] to-[#FDE68A] rounded-xl p-5 border border-[#F59E0B]/20">
                            <h5 className="font-bold text-[#92400E] mb-4 text-lg flex items-center gap-2">
                              🍽️ Meal Recommendations
                            </h5>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              {day.meals.breakfast && (
                                <div className="bg-white/60 p-3 rounded-lg">
                                  <span className="text-[#92400E] font-semibold block mb-1">🌅 Breakfast:</span>
                                  <span className="text-[#475569] font-medium">{day.meals.breakfast}</span>
                                </div>
                              )}
                              {day.meals.lunch && (
                                <div className="bg-white/60 p-3 rounded-lg">
                                  <span className="text-[#92400E] font-semibold block mb-1">☀️ Lunch:</span>
                                  <span className="text-[#475569] font-medium">{day.meals.lunch}</span>
                                </div>
                              )}
                              {day.meals.dinner && (
                                <div className="bg-white/60 p-3 rounded-lg">
                                  <span className="text-[#92400E] font-semibold block mb-1">🌙 Dinner:</span>
                                  <span className="text-[#475569] font-medium">{day.meals.dinner}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {day.notes && (
                          <div className="text-[#475569] italic bg-[#F8FAFB] p-4 rounded-lg border-l-4 border-[#3AA8C1]">
                            📝 <span className="font-medium">{day.notes}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Packing Tips & Local Phrases */}
              <div className="grid md:grid-cols-2 gap-6">
                {itinerary.packing_tips?.length > 0 && (
                  <div className="bg-gradient-to-br from-[#DBEAFE] to-[#BFDBFE] rounded-2xl p-6 border border-[#3B82F6]/20 shadow-lg">
                    <h4 className="font-bold text-[#1E40AF] mb-4 text-xl flex items-center gap-3">
                      <div className="p-2 bg-white/60 rounded-lg">
                        🎒
                      </div>
                      Packing Tips
                    </h4>
                    <ul className="space-y-3">
                      {itinerary.packing_tips.map((tip, idx) => (
                        <li key={idx} className="text-[#475569] flex items-start gap-3 bg-white/60 p-3 rounded-lg">
                          <span className="text-[#10B981] font-bold text-lg">✓</span>
                          <span className="font-medium">{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {itinerary.local_phrases?.length > 0 && (
                  <div className="bg-gradient-to-br from-[#D1FAE5] to-[#A7F3D0] rounded-2xl p-6 border border-[#10B981]/20 shadow-lg">
                    <h4 className="font-bold text-[#065F46] mb-4 text-xl flex items-center gap-3">
                      <div className="p-2 bg-white/60 rounded-lg">
                        🗣️
                      </div>
                      Useful Phrases
                    </h4>
                    <div className="space-y-3">
                      {itinerary.local_phrases.map((phrase, idx) => (
                        <div key={idx} className="bg-white/60 p-4 rounded-lg">
                          <span className="font-bold text-[#0F172A] text-lg">{phrase.phrase}:</span>
                          <span className="text-[#475569] ml-2 font-medium">{phrase.translation}</span>
                          {phrase.pronunciation && (
                            <span className="text-[#6B7280] ml-2 italic text-sm">({phrase.pronunciation})</span>
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
                className="w-full py-4 border-2 border-[#3AA8C1] text-[#3AA8C1] rounded-xl font-semibold hover:bg-[#3AA8C1] hover:text-white transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
              >
                🔄 Start Over - Create New Itinerary
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
