import ServicePageTemplate from '../components/ServicePageTemplate';
import BusSearch from '../components/BusSearch';

export default function BusPage() {
  return (
    <ServicePageTemplate
      title="Bus"
      description="Find real-time bus options with student-friendly filters and optimization."
    >
      <BusSearch />
    </ServicePageTemplate>
  );
}
