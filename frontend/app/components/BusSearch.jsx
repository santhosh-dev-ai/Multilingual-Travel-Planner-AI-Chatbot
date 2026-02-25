'use client';

import { useState } from 'react';
import { busesAPI } from '../services/api';

const formatPrice = (amount, currency) => {
  const code = (currency || 'INR').toUpperCase();
  try {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: code,
      maximumFractionDigits: 0,
    }).format(Number(amount));
  } catch {
    return `${code} ${amount}`;
  }
};

const formatDuration = (minutes) => {
  const total = Number(minutes) || 0;
  const hours = Math.floor(total / 60);
  const mins = total % 60;
  return `${hours}h ${mins}m`;
};

export default function BusSearch() {
  const [form, setForm] = useState({
    origin: '',
    destination: '',
    travel_date: '',
    passengers: 1,
    budget: '',
    max_stops: 2,
    ranking_preference: 'balanced',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [results, setResults] = useState([]);
  const [meta, setMeta] = useState(null);

  const searchBuses = async () => {
    if (!form.origin || !form.destination || !form.travel_date || !form.budget) {
      setError('Please fill origin, destination, date, and budget.');
      return;
    }

    setLoading(true);
    setError(null);
    setNotice(null);

    try {
      const response = await busesAPI.searchBuses({
        origin: form.origin,
        destination: form.destination,
        travel_date: form.travel_date,
        passengers: Number(form.passengers) || 1,
        budget: Number(form.budget),
        max_stops: Number(form.max_stops),
        ranking_preference: form.ranking_preference,
      });

      const options = response.buses || [];
      const diagnostics = response.filters_applied || {};

      setResults(options);
      setMeta({
        source: response.data_source,
        diagnostics,
        searchedAt: new Date().toLocaleTimeString(),
      });

      if (options.length === 0) {
        if ((diagnostics.provider_results_count || 0) === 0) {
          setNotice('No live bus options are currently available for this route/date.');
        } else {
          setNotice('Live buses exist, but your current filters removed all options.');
        }
      }
    } catch (err) {
      setResults([]);
      setMeta(null);
      setNotice(null);
      setError(err?.message || 'Bus search failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="py-8">
      <div className="bg-[#1E293B]/80 border border-[#334155] rounded-2xl p-6 lg:p-8 shadow-xl">
        <h3 className="text-2xl font-bold text-white mb-2">🚌 Student Bus Search</h3>
        <p className="text-[#CBD5E1] mb-6">Search live bus options with budget and stop controls.</p>

        <div className="grid md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-xs text-[#94A3B8] mb-1">From</label>
            <input
              type="text"
              placeholder="e.g., Bangalore"
              value={form.origin}
              onChange={(e) => setForm((prev) => ({ ...prev, origin: e.target.value }))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-xs text-[#94A3B8] mb-1">To</label>
            <input
              type="text"
              placeholder="e.g., Mysore"
              value={form.destination}
              onChange={(e) => setForm((prev) => ({ ...prev, destination: e.target.value }))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-xs text-[#94A3B8] mb-1">Travel date</label>
            <input
              type="date"
              value={form.travel_date}
              onChange={(e) => setForm((prev) => ({ ...prev, travel_date: e.target.value }))}
              className="input-field"
            />
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-xs text-[#94A3B8] mb-1">Passengers</label>
            <input
              type="number"
              min={1}
              max={9}
              value={form.passengers}
              onChange={(e) => {
                const value = Number(e.target.value);
                setForm((prev) => ({ ...prev, passengers: Number.isNaN(value) ? 1 : Math.min(Math.max(value, 1), 9) }));
              }}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-xs text-[#94A3B8] mb-1">Budget (INR)</label>
            <input
              type="number"
              min={1}
              value={form.budget}
              onChange={(e) => setForm((prev) => ({ ...prev, budget: e.target.value }))}
              className="input-field"
              placeholder="e.g., 1200"
            />
          </div>
          <div>
            <label className="block text-xs text-[#94A3B8] mb-1">Max stops</label>
            <select
              value={form.max_stops}
              onChange={(e) => setForm((prev) => ({ ...prev, max_stops: Number(e.target.value) }))}
              className="input-field"
            >
              <option value={0}>Non-stop only</option>
              <option value={1}>Up to 1 stop</option>
              <option value={2}>Up to 2 stops</option>
              <option value={3}>Up to 3 stops</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-[#94A3B8] mb-1">Preference</label>
            <select
              value={form.ranking_preference}
              onChange={(e) => setForm((prev) => ({ ...prev, ranking_preference: e.target.value }))}
              className="input-field"
            >
              <option value="balanced">Best balance</option>
              <option value="cheapest">Lowest price</option>
              <option value="fastest">Shortest duration</option>
              <option value="least_stops">Fewest stops</option>
            </select>
          </div>
        </div>

        <button
          onClick={searchBuses}
          disabled={loading}
          className="btn-primary w-full md:w-auto px-8 disabled:opacity-60"
        >
          {loading ? 'Searching buses...' : 'Search Buses'}
        </button>

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
        {notice && <p className="mt-4 text-sm text-amber-300">{notice}</p>}

        {meta && !error && (
          <p className="mt-4 text-sm text-[#94A3B8]">
            Live source: {meta.source} • Updated at {meta.searchedAt}
          </p>
        )}

        {results.length > 0 && (
          <div className="mt-6 space-y-3">
            {results.map((bus, index) => (
              <div key={bus.option_id || index} className="bg-[#0F172A]/70 border border-[#334155] rounded-xl p-4">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <p className="text-white font-semibold">#{index + 1} • {bus.operator}</p>
                  <p className="text-[#3AA8C1] font-bold">{formatPrice(bus.price, bus.currency)}</p>
                </div>
                <div className="grid sm:grid-cols-3 gap-2 text-sm text-[#CBD5E1]">
                  <p>Service: {bus.service_name}</p>
                  <p>Duration: {formatDuration(bus.total_duration_minutes)}</p>
                  <p>Stops: {bus.stops}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
