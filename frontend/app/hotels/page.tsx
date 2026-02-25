import ServicePageTemplate from '../components/ServicePageTemplate';

export default function HotelsPage() {
  return (
    <ServicePageTemplate
      title="Hotels"
      description="Find hotel stays with upcoming availability and pricing support."
    >
      <div className="bg-[#1E293B]/80 border border-[#334155] rounded-2xl p-6 text-[#CBD5E1]">
        Hotel booking UI will be available in this route.
      </div>
    </ServicePageTemplate>
  );
}
