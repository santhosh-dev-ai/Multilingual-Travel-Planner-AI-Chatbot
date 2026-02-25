import Link from 'next/link';
import { ReactNode } from 'react';

type ServicePageTemplateProps = {
  title: string;
  description: string;
  children?: ReactNode;
};

const serviceLinks = [
  { href: '/flights', label: 'Flights' },
  { href: '/trains', label: 'Trains' },
  { href: '/bus', label: 'Bus' },
  { href: '/hotels', label: 'Hotels' },
  { href: '/rooms', label: 'Rooms' },
  { href: '/airbnb', label: 'Airbnb' },
  { href: '/lounges', label: 'Lounges' },
  { href: '/services', label: 'Services' },
];

export default function ServicePageTemplate({ title, description, children }: ServicePageTemplateProps) {
  return (
    <main className="min-h-screen bg-gradient-to-br from-[#0F172A] to-[#1E293B] text-white">
      <header className="sticky top-0 z-40 bg-gradient-to-r from-[#1E293B]/95 to-[#334155]/95 backdrop-blur-lg border-b border-[#3AA8C1]/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-lg font-bold text-white hover:text-[#58B8CD] transition-colors">
              TravelGenie
            </Link>
            <Link href="/" className="text-sm font-semibold text-[#58B8CD] hover:text-[#7ED1E2] transition-colors">
              Back Home
            </Link>
          </div>
          <nav className="flex flex-wrap gap-2">
            {serviceLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="px-3 py-1.5 text-xs sm:text-sm rounded-full bg-[#0F172A]/50 border border-[#334155] hover:border-[#58B8CD] hover:text-[#7ED1E2] transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-3xl lg:text-4xl font-bold mb-2">{title}</h1>
          <p className="text-[#CBD5E1]">{description}</p>
        </div>
        {children}
      </section>
    </main>
  );
}
