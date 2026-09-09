import Reveal from './Reveal';

export default function FinalCTA() {
  return (
    <section
      className="relative py-32 md:py-44 border-t border-line overflow-hidden"
      style={{
        background:
          'radial-gradient(60% 60% at 50% 100%, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0) 70%), #050505',
      }}
    >
      <div className="max-w-content mx-auto px-6 text-center relative z-10">
        <Reveal>
          <h2 className="font-display font-semibold text-3xl sm:text-4xl md:text-5xl tracking-tightest text-ink max-w-2xl mx-auto">
            Your next voyage starts with a smarter route.
          </h2>
          <p className="mt-5 text-mute max-w-md mx-auto">
            Let ORCA help you understand the ocean before you navigate it.
          </p>
          <a
            href="/signup"
            className="inline-block mt-9 bg-ink text-void font-medium text-sm rounded-full px-8 py-4 hover:bg-white/85 transition-colors duration-300"
          >
            Start planning with ORCA
          </a>
        </Reveal>
      </div>
    </section>
  );
}
