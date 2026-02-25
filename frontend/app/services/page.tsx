import ServicePageTemplate from '../components/ServicePageTemplate';

export default function ServicesPage() {
  return (
    <ServicePageTemplate
      title="Services"
      description="Access additional support tools for complete trip planning."
    >
      <div className="bg-[#1E293B]/80 border border-[#334155] rounded-2xl p-6 text-[#CBD5E1]">
        Additional travel services UI will be available in this route.
      </div>
    </ServicePageTemplate>
  );
}
