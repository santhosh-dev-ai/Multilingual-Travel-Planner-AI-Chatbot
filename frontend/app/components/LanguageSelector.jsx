'use client';

import { useState } from 'react';
import { GlobeAltIcon, ChevronDownIcon, CheckIcon } from '@heroicons/react/24/outline';

const languages = [
  { code: 'en-US', name: 'English', flag: '🇺🇸' },
  { code: 'es-ES', name: 'Español', flag: '🇪🇸' },
  { code: 'fr-FR', name: 'Français', flag: '🇫🇷' },
  { code: 'de-DE', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'hi-IN', name: 'हिन्दी', flag: '🇮🇳' },
  { code: 'ja-JP', name: '日本語', flag: '🇯🇵' },
  { code: 'zh-CN', name: '中文', flag: '🇨🇳' },
  { code: 'pt-BR', name: 'Português', flag: '🇧🇷' },
  { code: 'ar-SA', name: 'العربية', flag: '🇸🇦' },
];

export default function LanguageSelector({ selectedLanguage, onLanguageChange }) {
  const [isOpen, setIsOpen] = useState(false);

  const currentLanguage = languages.find(lang => lang.code === selectedLanguage) || languages[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-(--color-surface) border border-(--color-border) rounded-lg hover:border-(--color-primary) transition-all duration-200 shadow-sm"
      >
        <GlobeAltIcon className="w-5 h-5 text-(--color-primary)" />
        <span className="text-2xl">{currentLanguage.flag}</span>
        <span className="text-sm font-medium text-(--color-text-primary)">{currentLanguage.name}</span>
        <ChevronDownIcon className={`w-4 h-4 text-(--color-text-secondary) transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-56 bg-(--color-surface) border border-(--color-border) rounded-xl shadow-xl z-20 overflow-hidden">
            <div className="py-2">
              {languages.map((language) => (
                <button
                  key={language.code}
                  onClick={() => {
                    onLanguageChange(language.code);
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-(--color-background-secondary) transition-colors duration-150"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{language.flag}</span>
                    <span className="text-sm font-medium text-(--color-text-primary)">{language.name}</span>
                  </div>
                  {language.code === selectedLanguage && (
                    <CheckIcon className="w-5 h-5 text-(--color-primary)" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}