import { Route, ShieldAlert, MapPinned, History } from 'lucide-react';
import Reveal from './Reveal';

const FEATURES = [
  {
    icon: Route,
    title: 'AI route planning',
    description: 'Describe your voyage naturally and let ORCA generate intelligent route options.',
  },
  {
    icon: ShieldAlert,
    title: 'Risk intelligence',
    description: 'Evaluate routes against maritime risk factors before choosing your path.',
  },
  {
    icon: MapPinned,
    title: 'Smart map visualization',
    description: 'Visualize routes, waypoints, and risk zones on an interactive map.',
  },
  {
    icon: History,
    title: 'Voyage history',
    description: 'Access previously generated routes and conversations from one place.',
  },
];

export default function Features() {
  return (
    <section id="features" className="py-28 md:py-40 border-t border-line">
      <div className="max-w-content mx-auto px-6">
        <Reveal className="max-w-xl">
          <h2 className="font-display font-semibold text-3xl sm:text-4xl tracking-tightest text-ink">
            Intelligence for every voyage.
          </h2>
        </Reveal>

        <div className="grid sm:grid-cols-2 gap-px mt-14 bg-line rounded-2xl overflow-hidden">
          {FEATURES.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <Reveal key={feature.title} delay={i * 0.05}>
                <div className="bg-void h-full p-8 hover:bg-surface transition-colors duration-300 group">
                  <Icon size={20} className="text-ink" aria-hidden="true" />
                  <h3 className="mt-5 text-ink font-medium">{feature.title}</h3>
                  <p className="mt-2 text-sm text-mute leading-relaxed">{feature.description}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
