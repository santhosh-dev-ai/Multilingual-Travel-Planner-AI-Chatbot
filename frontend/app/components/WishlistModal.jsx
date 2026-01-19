'use client';

import {
  XMarkIcon,
  MapPinIcon,
  HeartIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon, StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';

export default function WishlistModal({
  isOpen,
  onClose,
  wishlist,
  onRemoveFromWishlist,
  onExplore,
}) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      {/* Backdrop */}
      <div 
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
        }}
        onClick={onClose}
      />
      
      {/* Modal */}
      <div 
        style={{
          position: 'relative',
          backgroundColor: 'white',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '640px',
          maxHeight: '80vh',
          margin: '16px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '24px',
          borderBottom: '1px solid #e5e7eb',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '40px',
              height: '40px',
              background: 'linear-gradient(to bottom right, #ef4444, #ec4899)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <HeartSolidIcon style={{ width: '24px', height: '24px', color: 'white' }} />
            </div>
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>My Wishlist</h2>
              <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
                {wishlist.length} {wishlist.length === 1 ? 'destination' : 'destinations'} saved
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              padding: '8px',
              borderRadius: '8px',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
            }}
          >
            <XMarkIcon style={{ width: '24px', height: '24px', color: '#6b7280' }} />
          </button>
        </div>

        {/* Content */}
        <div style={{
          padding: '24px',
          overflowY: 'auto',
          flex: 1,
        }}>
          {wishlist.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '48px 0' }}>
              <HeartIcon style={{ width: '64px', height: '64px', color: '#d1d5db', margin: '0 auto 16px' }} />
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '8px' }}>
                Your wishlist is empty
              </h3>
              <p style={{ color: '#6b7280' }}>
                Start exploring destinations and save your favorites!
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {wishlist.map((destination) => (
                <div
                  key={destination.id}
                  style={{
                    display: 'flex',
                    gap: '16px',
                    padding: '16px',
                    backgroundColor: '#ffffffff',
                    borderRadius: '12px',
                  }}
                >
                  {/* Image */}
                  <div style={{
                    width: '96px',
                    height: '96px',
                    flexShrink: 0,
                    borderRadius: '8px',
                    overflow: 'hidden',
                  }}>
                    <img
                      src={destination.image}
                      alt={destination.name}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  </div>

                  {/* Info */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                      <div>
                        <h3 style={{ fontWeight: '600', color: '#111827', margin: 0 }}>
                          {destination.name}
                        </h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '14px', color: '#6b7280' }}>
                          <MapPinIcon style={{ width: '16px', height: '16px' }} />
                          <span>{destination.country}</span>
                        </div>
                      </div>
                      {destination.badge && (
                        <span style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          fontWeight: '500',
                          backgroundColor: '#ccfbf1',
                          color: '#0f766e',
                          borderRadius: '9999px',
                        }}>
                          {destination.badge}
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginTop: '8px', fontSize: '14px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <StarSolidIcon style={{ width: '16px', height: '16px', color: '#eab308' }} />
                        <span style={{ fontWeight: '500', color: '#111827' }}>
                          {destination.rating}
                        </span>
                      </div>
                      <span style={{ color: '#0d9488', fontWeight: '600' }}>
                        {destination.price}
                      </span>
                      <span style={{ color: '#9ca3af' }}>
                        {destination.duration}
                      </span>
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px' }}>
                      <button
                        onClick={() => {
                          onExplore(destination);
                          onClose();
                        }}
                        style={{
                          padding: '6px 12px',
                          fontSize: '14px',
                          background: 'linear-gradient(to right, #14b8a6, #06b6d4)',
                          color: 'white',
                          borderRadius: '8px',
                          border: 'none',
                          cursor: 'pointer',
                        }}
                      >
                        Explore
                      </button>
                      <button
                        onClick={() => onRemoveFromWishlist(destination)}
                        style={{
                          padding: '6px 12px',
                          fontSize: '14px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          color: '#ef4444',
                          backgroundColor: 'transparent',
                          borderRadius: '8px',
                          border: 'none',
                          cursor: 'pointer',
                        }}
                      >
                        <TrashIcon style={{ width: '16px', height: '16px' }} />
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
