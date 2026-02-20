import { useState } from 'react';
import { Bars3Icon, XMarkIcon, HeartIcon, CalendarDaysIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';

export default function HamburgerMenu({
  onWishlistClick,
  onItinerariesClick,
  onLogout,
  wishlistCount = 0,
  savedItinerariesCount = 0,
  translations,
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        className="p-2 rounded-lg hover:bg-white/10"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Open menu"
      >
        {open ? (
          <XMarkIcon className="w-7 h-7 text-white" />
        ) : (
          <Bars3Icon className="w-7 h-7 text-white" />
        )}
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-56 bg-[#1E293B] border border-[#334155] rounded-xl shadow-lg z-50">
          <ul className="py-2">
            <li>
              <button
                className="flex items-center w-full px-4 py-3 gap-3 hover:bg-[#334155] text-white"
                onClick={() => { setOpen(false); onWishlistClick(); }}
              >
                <HeartIcon className="w-5 h-5 text-red-500" />
                {translations?.menu?.wishlist || 'My Wishlist'}
                {wishlistCount > 0 && (
                  <span className="ml-auto min-w-5 h-5 px-1.5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {wishlistCount}
                  </span>
                )}
              </button>
            </li>
            <li>
              <button
                className="flex items-center w-full px-4 py-3 gap-3 hover:bg-[#334155] text-white"
                onClick={() => { setOpen(false); onItinerariesClick(); }}
              >
                <CalendarDaysIcon className="w-5 h-5 text-[#3AA8C1]" />
                {translations?.menu?.savedItineraries || 'Saved Itineraries'}
                {savedItinerariesCount > 0 && (
                  <span className="ml-auto min-w-5 h-5 px-1.5 bg-[#3AA8C1] text-white text-xs rounded-full flex items-center justify-center">
                    {savedItinerariesCount}
                  </span>
                )}
              </button>
            </li>
            {onLogout && (
              <li>
                <button
                  className="flex items-center w-full px-4 py-3 gap-3 hover:bg-[#334155] text-white border-t border-[#334155]"
                  onClick={() => { setOpen(false); onLogout(); }}
                >
                  <ArrowRightOnRectangleIcon className="w-5 h-5 text-[#F87171]" />
                  {translations?.menu?.logout || 'Logout'}
                </button>
              </li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
