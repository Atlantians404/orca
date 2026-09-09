import { LifeBuoy, Fish, Waves, Languages, Route, Zap } from 'lucide-react';
import Reveal from './Reveal';

const BENEFITS = [
  {
    icon: LifeBuoy,
    title: 'Enhanced fishermen safety',
    description: 'Combines weather, waves, marine warnings and geospatial restrictions to support safer fishing decisions.',
  },
  {
    icon: Fish,
    title: 'Smarter fishing decisions',
    description: 'Uses PFZ, SST and chlorophyll data to identify potentially productive fishing zones and improve planning.',
  },
  {
    icon: Waves,
    title: '360° marine awareness',
    description: 'Correlates marine, weather and geospatial data in one platform, reducing the need to consult multiple sources.',
  },
  {
    icon: Languages,
    title: 'Inclusive & visual access',
    description: 'Indian-language support, charts, graphs, risk indicators and interactive maps make complex marine information easier to understand.',
  },
  {
    icon: Route,
    title: 'Safer route planning',
    description: 'Generates recommended routes considering risk, weather conditions and geographic restrictions.',
  },
  {
    icon: Zap,
    title: 'Faster decision support',
    description: '0–50% less information-gathering effort by bringing marine, weather and geospatial information into one AI-powered interface.',
  },
];

export default function FisherFocus() {
  return (
    <section className="py-28 md:py-40 border-t border-line">
      <div className="max-w-content mx-auto px-6">
        <Reveal className="max-w-xl">
          <span className="text-xs text-mute tracking-wide">Built for the water</span>
          <h2 className="font-display font-semibold text-3xl sm:text-4xl tracking-tightest text-ink mt-4">
            Made for the people who sail.
          </h2>
        </Reveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-px mt-14 bg-line rounded-2xl overflow-hidden">
          {BENEFITS.map((item, i) => {
            const Icon = item.icon;
            return (
              <Reveal key={item.title} delay={(i % 3) * 0.05}>
                <div className="bg-void h-full p-8 hover:bg-surface transition-colors duration-300">
                  <Icon size={20} className="text-ink" aria-hidden="true" />
                  <h3 className="mt-5 text-ink font-medium">{item.title}</h3>
                  <p className="mt-2 text-sm text-mute leading-relaxed">{item.description}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
