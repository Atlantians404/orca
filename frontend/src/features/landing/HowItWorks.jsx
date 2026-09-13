import { useRef } from 'react';
import { motion, useScroll } from 'framer-motion';
import Reveal from './Reveal';

const STEPS = [
  { n: '01', title: 'Ask', description: 'Tell ORCA about your voyage.' },
  { n: '02', title: 'Analyze', description: 'ORCA processes route and risk information.' },
  { n: '03', title: 'Compare', description: 'Multiple route options are evaluated.' },
  { n: '04', title: 'Navigate', description: 'Choose the route and visualize it on the map.' },
];

export default function HowItWorks() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start 0.8', 'end 0.4'],
  });

  return (
    <section id="how-it-works" className="py-28 md:py-40 border-t border-line">
      <div className="max-w-content mx-auto px-6">
        <Reveal className="max-w-xl">
          <h2 className="font-display font-semibold text-3xl sm:text-4xl tracking-tightest text-ink">
            Four steps to a safer voyage.
          </h2>
        </Reveal>

        <div ref={ref} className="relative mt-16 max-w-xl">
          <div className="absolute left-[19px] top-2 bottom-2 w-px bg-line" aria-hidden="true" />
          <motion.div
            className="absolute left-[19px] top-2 w-px bg-white origin-top"
            style={{ scaleY: scrollYProgress, height: 'calc(100% - 16px)' }}
            aria-hidden="true"
          />

          <ol className="space-y-12">
            {STEPS.map((step) => (
              <li key={step.n} className="relative pl-14">
                <span className="absolute left-0 top-0 flex items-center justify-center h-10 w-10 rounded-full border border-line2 bg-void text-xs text-mute">
                  {step.n}
                </span>
                <h3 className="text-ink font-medium">{step.title}</h3>
                <p className="mt-1.5 text-sm text-mute">{step.description}</p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
