'use client';

import { useState } from 'react';
import { flightsAPI } from '../services/api';

const formatFlightPrice = (amount, currency) => {
  const normalizedCurrency = (currency || 'INR').toUpperCase();
  try {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: normalizedCurrency,
      maximumFractionDigits: 0,
    }).format(Number(amount));
  } catch {
    return `${normalizedCurrency} ${amount}`;
  }
};

export default function FlightSearch() {
  const [flightForm, setFlightForm] = useState({
    origin: '',
    destination: '',
    departure_date: '',
    return_date: '',
    adults: 1,
    budget: '',
    cabin_class: 'ECONOMY',
    max_stops: 2,
    baggage_required: false,
    ranking_preference: 'balanced',
  });
  const [flightLoading, setFlightLoading] = useState(false);
  const [flightError, setFlightError] = useState(null);
  const [flightNotice, setFlightNotice] = useState(null);
  const [flightResults, setFlightResults] = useState([]);
  const [flightMeta, setFlightMeta] = useState(null);

  const handleFlightSearch = async () => {
    if (!flightForm.origin || !flightForm.destination || !flightForm.departure_date || !flightForm.return_date || !flightForm.budget) {
      setFlightError('Please fill origin, destination, start date, end date, and budget.');
      return;
    }

    if (new Date(flightForm.return_date) < new Date(flightForm.departure_date)) {
      setFlightError('Ending date must be on or after starting date.');
      return;
    }

    setFlightLoading(true);
    setFlightError(null);
    setFlightNotice(null);

    try {
      const response = await flightsAPI.searchFlights({
        origin: flightForm.origin,
        destination: flightForm.destination,
        departure_date: flightForm.departure_date,
        return_date: flightForm.return_date,
        adults: Number(flightForm.adults) || 1,
        budget: Number(flightForm.budget),
        cabin_class: flightForm.cabin_class,
        max_stops: Number(flightForm.max_stops),
        baggage_required: !!flightForm.baggage_required,
        ranking_preference: flightForm.ranking_preference,
        non_stop_only: Number(flightForm.max_stops) === 0,
      });

      setFlightResults(response.flights || []);
      setFlightMeta({
        originIata: response.resolved_origin_iata,
        destinationIata: response.resolved_destination_iata,
        preference: flightForm.ranking_preference,
        source: response.data_source,
        searchedAt: new Date().toLocaleTimeString(),
        diagnostics: response.filters_applied,
      });
      if (!response.flights || response.flights.length === 0) {
        const diagnostics = response.filters_applied || {};
        if ((diagnostics.provider_offers_count || 0) === 0) {
          setFlightNotice('No real-time flights are currently available for these exact dates/route. Try nearby dates.');
        } else {
          setFlightNotice('Live flights exist, but current filters are too strict. You can relax filters below.');
        }
      }
    } catch (error) {
      setFlightResults([]);
      setFlightMeta(null);
      setFlightNotice(null);
      setFlightError(error?.message || 'Flight search failed. Please try again.');
    } finally {
      setFlightLoading(false);
    }
  };

  const handleRelaxFilters = async () => {
    setFlightLoading(true);
    setFlightError(null);
    setFlightNotice(null);

    try {
      const relaxedStops = Math.min(Number(flightForm.max_stops) + 1, 3);
      const response = await flightsAPI.searchFlights({
        origin: flightForm.origin,
        destination: flightForm.destination,
        departure_date: flightForm.departure_date,
        return_date: flightForm.return_date,
        adults: Number(flightForm.adults) || 1,
        budget: Number(flightForm.budget),
        cabin_class: flightForm.cabin_class,
        max_stops: relaxedStops,
        baggage_required: false,
        ranking_preference: flightForm.ranking_preference,
        non_stop_only: relaxedStops === 0,
      });

      setFlightForm((prev) => ({ ...prev, max_stops: relaxedStops, baggage_required: false }));
      setFlightResults(response.flights || []);
      setFlightMeta({
        originIata: response.resolved_origin_iata,
        destinationIata: response.resolved_destination_iata,
        preference: flightForm.ranking_preference,
        source: response.data_source,
        searchedAt: new Date().toLocaleTimeString(),
        diagnostics: response.filters_applied,
      });

      if (!response.flights || response.flights.length === 0) {
        setFlightNotice('Still no flights after relaxing filters. Try changing dates or route.');
      } else {
        setFlightNotice('Showing best available live flights after relaxing filters (more layovers allowed, baggage-only removed).');
      }
    } catch (error) {
      setFlightError(error?.message || 'Could not relax filters right now.');
    } finally {
      setFlightLoading(false);
    }
  };

  return (
    <section className="py-16 bg-gradient-to-b from-[#0F172A] to-[#1E293B] border-t border-[#334155]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-[#1E293B]/80 border border-[#334155] rounded-2xl p-6 lg:p-8 shadow-xl">
          <h3 className="text-2xl font-bold text-white mb-2">🎫 Student Flight Search</h3>
          <p className="text-[#CBD5E1] mb-6">Enter your trip details in simple terms. We auto-detect airport codes and return live flight options.</p>

          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">From (city or airport)</label>
              <input
                type="text"
                placeholder="e.g., Delhi"
                value={flightForm.origin}
                onChange={(e) => setFlightForm((prev) => ({ ...prev, origin: e.target.value }))}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">To (city or airport)</label>
              <input
                type="text"
                placeholder="e.g., Chennai"
                value={flightForm.destination}
                onChange={(e) => setFlightForm((prev) => ({ ...prev, destination: e.target.value }))}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">Start date</label>
              <input
                type="date"
                value={flightForm.departure_date}
                onChange={(e) => setFlightForm((prev) => ({ ...prev, departure_date: e.target.value }))}
                className="input-field"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">End date</label>
              <input
                type="date"
                value={flightForm.return_date}
                onChange={(e) => setFlightForm((prev) => ({ ...prev, return_date: e.target.value }))}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">Number of travelers</label>
              <input
                type="number"
                min={1}
                max={9}
                value={flightForm.adults}
                onChange={(e) => {
                  const value = Number(e.target.value);
                  setFlightForm((prev) => ({ ...prev, adults: Number.isNaN(value) ? 1 : Math.min(Math.max(value, 1), 9) }));
                }}
                className="input-field"
                placeholder="1"
              />
            </div>
            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">Total budget (INR)</label>
              <input
                type="number"
                min={1}
                value={flightForm.budget}
                onChange={(e) => setFlightForm((prev) => ({ ...prev, budget: e.target.value }))}
                className="input-field"
                placeholder="e.g., 15000"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">Seat type</label>
              <select
                value={flightForm.cabin_class}
                onChange={(e) => setFlightForm((prev) => ({ ...prev, cabin_class: e.target.value }))}
                className="input-field"
              >
                <option value="ECONOMY">Economy</option>
                <option value="PREMIUM_ECONOMY">Premium Economy</option>
                <option value="BUSINESS">Business</option>
                <option value="FIRST">First</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">Layovers you can accept</label>
              <select
                value={flightForm.max_stops}
                onChange={(e) => setFlightForm((prev) => ({ ...prev, max_stops: Number(e.target.value) }))}
                className="input-field"
              >
                <option value={0}>Direct flights only (0 layovers)</option>
                <option value={1}>Up to 1 layover</option>
                <option value={2}>Up to 2 layovers</option>
                <option value={3}>Up to 3 layovers</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-[#94A3B8] mb-1">What matters most to you?</label>
              <select
                value={flightForm.ranking_preference}
                onChange={(e) => setFlightForm((prev) => ({ ...prev, ranking_preference: e.target.value }))}
                className="input-field"
              >
                <option value="balanced">Best overall balance</option>
                <option value="cheapest">Lowest price</option>
                <option value="fastest">Shortest travel time</option>
                <option value="baggage">Checked baggage included</option>
              </select>
            </div>

            <div className="flex items-center gap-4 px-4 py-3 rounded-xl border border-[#334155] bg-[#0F172A]/50">
              <label className="flex items-center gap-2 text-sm text-[#CBD5E1]">
                <input
                  type="checkbox"
                  checked={flightForm.baggage_required}
                  onChange={(e) => setFlightForm((prev) => ({ ...prev, baggage_required: e.target.checked }))}
                />
                Only show flights with checked baggage included
              </label>
            </div>
          </div>

          <button
            onClick={handleFlightSearch}
            disabled={flightLoading}
            className="btn-primary w-full md:w-auto px-8 disabled:opacity-60"
          >
            {flightLoading ? 'Searching flights...' : 'Search Flights'}
          </button>

          {flightError && <p className="mt-4 text-sm text-red-400">{flightError}</p>}
          {flightNotice && <p className="mt-4 text-sm text-amber-300">{flightNotice}</p>}

          {flightNotice && flightResults.length === 0 && !flightLoading && (
            <button
              onClick={handleRelaxFilters}
              className="mt-3 px-4 py-2 rounded-lg text-sm font-semibold bg-amber-500/20 text-amber-200 border border-amber-400/30 hover:bg-amber-500/30 transition-colors"
            >
              Show best available live flights
            </button>
          )}

          {flightMeta && !flightError && (
            <p className="mt-4 text-sm text-[#94A3B8]">
              Live results from {flightMeta.source || 'Amadeus'} • Route matched to {flightMeta.originIata || 'N/A'} → {flightMeta.destinationIata || 'N/A'} • Updated at {flightMeta.searchedAt}
            </p>
          )}

          {flightResults.length > 0 && (
            <div className="mt-6 space-y-3">
              {flightResults.map((flight, index) => (
                <div key={flight.offer_id || index} className="bg-[#0F172A]/70 border border-[#334155] rounded-xl p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                    <p className="text-white font-semibold">#{index + 1} • {flight.airline || 'Airline'}</p>
                    <p className="text-[#3AA8C1] font-bold">{formatFlightPrice(flight.price, flight.currency)}</p>
                  </div>
                  <div className="grid sm:grid-cols-3 gap-2 text-sm text-[#CBD5E1]">
                    <p>Duration: {flight.total_duration_minutes} min</p>
                    <p>Stops: {flight.number_of_stops}</p>
                    <p>Baggage: {flight.baggage_included ? 'Included' : 'Not included'}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
