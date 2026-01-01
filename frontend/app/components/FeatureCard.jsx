export default function FeatureCard({ icon: Icon, title, description }) {
  return (
    <div className="card p-6 hover:shadow-lg transition-all duration-300 group">
      <div className="w-14 h-14 bg-gradient-to-br from-(--color-primary-50) to-(--color-accent-50) rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
        <Icon className="w-7 h-7 text-(--color-primary)" />
      </div>
      <h3 className="text-lg font-bold text-(--color-text-primary) mb-2">{title}</h3>
      <p className="text-sm text-(--color-text-secondary) leading-relaxed">{description}</p>
    </div>
  );
}