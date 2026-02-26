'use client';

import Link from 'next/link';

export default function StatesGrid({ states = [] }) {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 animate-fadeIn">
      {states.map((state) => {
        const href = `/state/${encodeURIComponent(state.name)}`;

        return (
          <div
            key={state.name}
            className="bg-[#1E293B] rounded-xl border border-[#334155] shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden group hover:scale-[1.02]"
          >
            <div className="relative h-52 overflow-hidden">
              <img
                src={state.image}
                alt={state.name}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
              <h3 className="absolute bottom-4 left-4 text-white text-xl font-bold pr-4">{state.name}</h3>
            </div>

            <div className="p-4 flex items-center justify-end">
              <Link
                href={href}
                className="px-4 py-2 bg-gradient-to-r from-[#3AA8C1] to-[#58B8CD] text-white text-sm font-semibold rounded-lg hover:shadow-lg transition-all duration-200 active:scale-95"
              >
                Explore
              </Link>
            </div>
          </div>
        );
      })}
    </div>
  );
}
