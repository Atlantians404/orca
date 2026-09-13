import { motion } from 'framer-motion';

const PARTICLES = Array.from({ length: 22 }, (_, i) => ({
  id: i,
  left: Math.round((i * 137.5) % 100),
  delay: (i % 11) * 0.9,
  duration: 9 + (i % 6),
  dx: ((i % 5) - 2) * 14,
  size: i % 4 === 0 ? 2 : 1,
}));

// Waypoints on the tilted grid. "weight" drives how much visual emphasis
// a point gets now that color no longer encodes risk level.
const WAYPOINTS = [
  { x: 140, y: 350, weight: 'plain' },
  { x: 230, y: 270, weight: 'low' },
  { x: 300, y: 190, weight: 'high' },
  { x: 400, y: 90, weight: 'plain' },
];

const ROUTE_D = 'M140,350 C260,280 300,180 400,90';

export default function Hero() {
  return (
    <section
      id="top"
      className="relative min-h-screen flex flex-col justify-center overflow-hidden pt-24"
      style={{
        background:
          'radial-gradient(60% 50% at 50% 18%, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0) 70%), #050505',
      }}
    >
      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
        {PARTICLES.map((p) => (
          <span
            key={p.id}
            className="absolute bottom-0 rounded-full bg-white/50"
            style={{
              left: `${p.left}%`,
              width: p.size,
              height: p.size,
              '--dx': `${p.dx}px`,
              animation: `drift ${p.duration}s linear ${p.delay}s infinite`,
            }}
          />
        ))}
      </div>

      {/* Headline */}
      <div className="relative z-10 max-w-content mx-auto px-6 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="font-display font-semibold text-[3.1rem] leading-[1.02] tracking-tightest text-ink sm:text-7xl md:text-8xl"
        >
          Navigate smarter.
          <br />
          <span
            style={{
              backgroundImage: 'linear-gradient(90deg, #FFFFFF 0%, #8A8A8A 100%)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
              color: 'transparent',
            }}
          >
            Sail safer.
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
          className="mt-6 text-base sm:text-lg text-mute max-w-xl mx-auto"
        >
          AI-powered maritime route planning and risk intelligence for safer voyages.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="mt-9 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <a
            href="/signup"
            className="w-full sm:w-auto text-center bg-ink text-void font-medium text-sm rounded-full px-7 py-3.5 hover:bg-white/85 transition-colors duration-300"
          >
            Start planning
          </a>
          <a
            href="#product"
            className="w-full sm:w-auto text-center border border-line2 text-ink text-sm rounded-full px-7 py-3.5 hover:border-white hover:bg-white/5 transition-colors duration-300"
          >
            Explore ORCA
          </a>
        </motion.div>
      </div>

      {/* Tilted ocean grid with sonar sweep */}
      <div className="relative z-0 mt-16 md:mt-20 h-[260px] sm:h-[320px] md:h-[380px] w-full" style={{ perspective: '900px' }}>
        <div
          className="absolute inset-0"
          style={{
            maskImage: 'linear-gradient(to bottom, transparent, black 25%, black 80%, transparent)',
            WebkitMaskImage: 'linear-gradient(to bottom, transparent, black 25%, black 80%, transparent)',
          }}
        >
          <svg
            viewBox="0 0 680 420"
            preserveAspectRatio="xMidYMax meet"
            className="w-full h-full"
            role="img"
            aria-label="A tilted grid representing the ocean, with an AI-calculated route, waypoints, and a rotating sonar sweep scanning for risk"
          >
            <defs>
              <linearGradient id="heroSweep" x1="340" y1="380" x2="300" y2="150" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.28" />
                <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
              </linearGradient>
            </defs>

            <path d="M230,60 L430,60 L620,380 L60,380 Z" fill="#0A0A0A" stroke="rgba(255,255,255,0.14)" strokeWidth="1" />
            <line x1="187.5" y1="140" x2="477.5" y2="140" stroke="rgba(255,255,255,0.07)" strokeWidth="0.5" />
            <line x1="145" y1="220" x2="525" y2="220" stroke="rgba(255,255,255,0.07)" strokeWidth="0.5" />
            <line x1="102.5" y1="300" x2="572.5" y2="300" stroke="rgba(255,255,255,0.07)" strokeWidth="0.5" />
            <line x1="280" y1="60" x2="200" y2="380" stroke="rgba(255,255,255,0.07)" strokeWidth="0.5" />
            <line x1="330" y1="60" x2="340" y2="380" stroke="rgba(255,255,255,0.07)" strokeWidth="0.5" />
            <line x1="380" y1="60" x2="480" y2="380" stroke="rgba(255,255,255,0.07)" strokeWidth="0.5" />

            <g style={{ transformOrigin: '340px 380px', animation: 'sweepRotate 7s linear infinite' }} opacity="0.9">
              <path d="M340,380 L230,190 A250,250 0 0,1 370,150 Z" fill="url(#heroSweep)" />
            </g>

            <path
              d={ROUTE_D}
              fill="none"
              stroke="#FFFFFF"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeDasharray="700"
              strokeDashoffset="700"
              style={{ animation: 'dash 2.2s 0.6s ease-out forwards' }}
              opacity="0.9"
            />

            {WAYPOINTS.map((w, i) => {
              if (w.weight === 'high') {
                return (
                  <g key={i} style={{ animation: `pulseDot 2.4s ${1.2 + i * 0.15}s ease-in-out infinite` }}>
                    <circle cx={w.x} cy={w.y} r="5" fill="#FFFFFF" />
                    <circle cx={w.x} cy={w.y} r="12" fill="none" stroke="#FFFFFF" strokeWidth="0.75" opacity="0.35" />
                  </g>
                );
              }
              if (w.weight === 'low') {
                return (
                  <circle
                    key={i}
                    cx={w.x}
                    cy={w.y}
                    r="4"
                    fill="none"
                    stroke="#FFFFFF"
                    strokeWidth="1.4"
                    opacity="0.75"
                  />
                );
              }
              return <circle key={i} cx={w.x} cy={w.y} r="3.5" fill="#FFFFFF" opacity="0.9" />;
            })}
          </svg>
        </div>
      </div>
    </section>
  );
}
