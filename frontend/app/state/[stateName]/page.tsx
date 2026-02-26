'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import StateDetails from '../../components/StateDetails';
import { destinationAPI } from '../../services/api';

export default function StateDetailsPage({ params }: { params: { stateName: string } }) {
  const stateName = useMemo(() => decodeURIComponent(params.stateName || ''), [params.stateName]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await destinationAPI.exploreState(stateName);
        if (!active) return;
        setData(response);
      } catch (err: any) {
        if (!active) return;
        setError(err?.message || 'Failed to load state details');
      } finally {
        if (active) setLoading(false);
      }
    };

    if (stateName) {
      load();
    } else {
      setLoading(false);
      setError('Invalid state');
    }

    return () => {
      active = false;
    };
  }, [stateName]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#1E293B] to-[#0F172A]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-6">
          <Link
            href="/#destinations"
            className="inline-flex items-center text-sm font-semibold text-[#58B8CD] hover:text-[#7ED1E2] transition-colors"
          >
            ← Back to States
          </Link>
        </div>

        <StateDetails
          stateName={stateName}
          data={data}
          loading={loading}
          error={error}
        />
      </div>
    </div>
  );
}
