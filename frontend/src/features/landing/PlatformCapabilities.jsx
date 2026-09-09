import { Cpu, Database, Layers, Bot, Globe, TrendingUp } from 'lucide-react';
import Reveal from './Reveal';

const CAPABILITIES = [
  {
    icon: Cpu,
    title: 'Technology readiness',
    description: 'Uses proven technologies such as FastAPI, AI agents, geospatial analysis and database technologies.',
  },
  {
    icon: Database,
    title: 'Data availability',
    description: 'Provides access to marine datasets from ISRO/MOSDAC and INCOIS, including satellite-derived ocean information.',
  },
  {
    icon: Layers,
    title: 'Modular architecture',
    description: 'Supports independent and scalable modules for marine, weather, route and risk functions, integrated through common interfaces.',
  },
  {
    icon: Bot,
    title: 'Reliable decisions',
    description: 'Uses AI for understanding and coordination, while backend logic handles risk and route decisions.',
  },
  {
    icon: Globe,
    title: 'Practical deployment',
    description: 'Is designed for real users through multilingual interaction, maps and contextual recommendations.',
  },
  {
    icon: TrendingUp,
    title: 'Future scalability',
    description: 'Is ready for expansion with support for additional ocean parameters, languages, data sources and real-time.',
  },
];

export default function PlatformCapabilities() {
  return (
    <section className="py-28 md:py-40 border-t border-line">
      <div className="max-w-content mx-auto px-6">
        <Reveal className="max-w-xl">
          <span className="text-xs text-mute tracking-wide">Under the hood</span>
          <h2 className="font-display font-semibold text-3xl sm:text-4xl tracking-tightest text-ink mt-4">
            Built on solid ground.
          </h2>
        </Reveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-px mt-14 bg-line rounded-2xl overflow-hidden">
          {CAPABILITIES.map((item, i) => {
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
