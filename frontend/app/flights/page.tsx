import FlightSearch from '../components/FlightSearch';
import ServicePageTemplate from '../components/ServicePageTemplate';

export default function FlightsPage() {
  return (
    <ServicePageTemplate
      title="Flights"
      description="Search and compare real-time flight offers for your journey."
    >
      <FlightSearch />
    </ServicePageTemplate>
  );
}
