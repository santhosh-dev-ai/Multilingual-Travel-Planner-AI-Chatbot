import { useState } from 'react';
import { Bars3Icon, XMarkIcon, HeartIcon, CalendarDaysIcon } from '@heroicons/react/24/outline';

export default function HamburgerMenu({
  onWishlistClick,
  onItinerariesClick,
  wishlistCount = 0,
  savedItinerariesCount = 0,
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        className="p-2 rounded-lg hover:bg-(--color-background-secondary)"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Open menu"
      >
        {open ? (
          <XMarkIcon className="w-7 h-7 text-(--color-text-primary)" />
        ) : (
          <Bars3Icon className="w-7 h-7 text-(--color-text-primary)" />
        )}
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-(--color-dark-surface) border border-(--color-border) rounded-xl shadow-lg z-50">
          <ul className="py-2">
            <li>
              <button
                className="flex items-center w-full px-4 py-3 gap-3 hover:bg-(--color-background-secondary) text-(--color-text-primary)"
                onClick={() => { setOpen(false); onWishlistClick(); }}
              >
                <HeartIcon className="w-5 h-5 text-red-500" />
                My Wishlist
                {wishlistCount > 0 && (
                  <span className="ml-auto min-w-5 h-5 px-1.5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {wishlistCount}
                  </span>
                )}
              </button>
            </li>
            <li>
              <button
                className="flex items-center w-full px-4 py-3 gap-3 hover:bg-(--color-background-secondary) text-(--color-text-primary)"
                onClick={() => { setOpen(false); onItinerariesClick(); }}
              >
                <CalendarDaysIcon className="w-5 h-5 text-blue-500" />
                Saved Itineraries
                {savedItinerariesCount > 0 && (
                  <span className="ml-auto min-w-5 h-5 px-1.5 bg-blue-500 text-white text-xs rounded-full flex items-center justify-center">
                    {savedItinerariesCount}
                  </span>
                )}
              </button>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
