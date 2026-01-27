export default function FeatureCard({ icon: Icon, title, description }) {
  return (
    <div className="bg-[#1E293B] rounded-xl border border-[#334155] shadow-sm hover:shadow-md transition-shadow duration-200 p-6 hover:shadow-lg transition-all duration-300 group">
      <div className="w-14 h-14 bg-gradient-to-br from-[#3AA8C1]/20 to-[#58B8CD]/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
        <Icon className="w-7 h-7 text-[#3AA8C1]" />
      </div>
      <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
      <p className="text-sm text-[#CBD5E1] leading-relaxed">{description}</p>
    </div>
  );
}