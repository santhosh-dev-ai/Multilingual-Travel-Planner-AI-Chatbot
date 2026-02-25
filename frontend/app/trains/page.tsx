import ServicePageTemplate from '../components/ServicePageTemplate';
import TrainSearch from '../components/TrainSearch';

export default function TrainsPage() {
  return (
    <ServicePageTemplate
      title="Trains"
      description="Find real-time train options with student-friendly filters and optimization."
    >
      <TrainSearch />
    </ServicePageTemplate>
  );
}
