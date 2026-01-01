'use client';

import { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import LanguageSelector from './components/LanguageSelector';
import DestinationCard from './components/DestinationCard';
import FeatureCard from './components/FeatureCard';
import { destinations, translations } from './data/destinations';
import {
  SparklesIcon,
  GlobeAltIcon,
  ChatBubbleBottomCenterTextIcon,
  MapIcon,
  ClockIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';

export default function Home() {
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en-US');

  const t = (translations as Record<string, typeof translations['en-US']>)[selectedLanguage] || translations['en-US'];

  const featureIcons = [
    SparklesIcon,
    GlobeAltIcon,
    ChatBubbleBottomCenterTextIcon,
    MapIcon,
    ClockIcon,
    ShieldCheckIcon,
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-(--color-dark-surface)/80 backdrop-blur-md border-b border-(--color-border)">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-(--color-primary) to-(--color-secondary) rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-(--color-text-primary)">TravelGenie</h1>
                <p className="text-xs text-(--color-text-tertiary)">{t.header.tagline}</p>
              </div>
            </div>
            <LanguageSelector
              selectedLanguage={selectedLanguage}
              onLanguageChange={setSelectedLanguage}
            />
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-(--color-primary-50) via-(--color-background) to-(--color-accent-50) dark:from-(--color-dark-background) dark:via-(--color-dark-background-secondary) dark:to-(--color-dark-background-tertiary)">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, currentColor 1px, transparent 0)',
            backgroundSize: '32px 32px',
          }} />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="text-center lg:text-left">
              <h2 className="text-4xl lg:text-5xl xl:text-6xl font-bold text-(--color-text-primary) mb-6 leading-tight">
                {t.hero.title}
              </h2>
              
              <p className="text-lg text-(--color-text-secondary) mb-8 leading-relaxed">
                {t.hero.subtitle}
              </p>


              {/* Stats */}
              <div className="grid grid-cols-3 gap-6 mt-12 pt-12 border-t border-(--color-border)">
                <div>
                  <div className="text-3xl font-bold text-(--color-primary) mb-1">150+</div>
                  <div className="text-sm text-(--color-text-tertiary)">{t.stats.countries}</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-(--color-primary) mb-1">50K+</div>
                  <div className="text-sm text-(--color-text-tertiary)">{t.stats.travelers}</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-(--color-primary) mb-1">24/7</div>
                  <div className="text-sm text-(--color-text-tertiary)">{t.stats.support}</div>
                </div>
              </div>
            </div>

            {/* Right - Chat Interface */}
            <div className="lg:pl-8">
              <ChatInterface selectedLanguage={selectedLanguage} />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary)">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-(--color-text-primary) mb-4">
              {t.features.title}
            </h2>
            <p className="text-lg text-(--color-text-secondary) max-w-2xl mx-auto">
              {t.features.subtitle}
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {t.features.items.map((feature, index) => (
              <FeatureCard
                key={index}
                icon={featureIcons[index]}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Destinations Section */}
      <section id="destinations" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-(--color-text-primary) mb-4">
              {t.destinations.title}
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {destinations.map((destination) => (
              <DestinationCard key={destination.id} destination={destination} translations={t.destinations} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="cta-section" className="py-20 bg-gradient-to-br from-(--color-primary) to-(--color-secondary) relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '32px 32px',
          }} />
        </div>
        
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
            {t.cta.title}
          </h2>
          <p className="text-lg text-white/90 mb-8">
            {t.cta.subtitle}
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-(--color-background-secondary) dark:bg-(--color-dark-background-secondary) border-t border-(--color-border)">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-(--color-primary) to-(--color-secondary) rounded-lg flex items-center justify-center">
                  <SparklesIcon className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold text-(--color-text-primary)">TravelGenie</span>
              </div>
              <p className="text-sm text-(--color-text-secondary)">
                {t.footer.description}
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-(--color-text-primary) mb-4">{t.footer.destinations}</h4>
              <ul className="space-y-2 text-sm text-(--color-text-secondary)">
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.europe}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.asia}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.americas}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.africa}</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-(--color-text-primary) mb-4">{t.footer.company}</h4>
              <ul className="space-y-2 text-sm text-(--color-text-secondary)">
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.about}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.careers}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.blog}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.contact}</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-(--color-text-primary) mb-4">{t.footer.support}</h4>
              <ul className="space-y-2 text-sm text-(--color-text-secondary)">
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.help}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.privacy}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.terms}</a></li>
                <li><a href="#" className="hover:text-(--color-primary) transition-colors">{t.footer.cookies}</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-(--color-border) text-center text-sm text-(--color-text-tertiary)">
            <p>{t.footer.copyright}</p>
          </div>
        </div>
      </footer>
    </div>
  );
}