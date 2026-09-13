import Reveal from './Reveal';

export default function MapShowcase() {
  return (
    <section className="relative py-28 md:py-40 border-t border-line overflow-hidden">
      <div className="max-w-content mx-auto px-6">
        <Reveal className="max-w-xl">
          <h2 className="font-display font-semibold text-3xl sm:text-4xl tracking-tightest text-ink">
            See the ocean differently.
          </h2>
          <p className="mt-5 text-mute">
            Every route ORCA proposes is drawn against live maritime conditions,
            so you can see exactly where the risk sits before you commit to it.
          </p>
        </Reveal>

        <Reveal delay={0.1} className="mt-14">
          <div className="relative rounded-2xl border border-line bg-surface p-6 sm:p-10">
            <svg
              viewBox="0 0 900 420"
              className="w-full h-auto"
              role="img"
              aria-label="Map showing three compared ocean routes from Chennai to Singapore: a solid recommended route, a dashed alternate, and a dotted higher-risk route, with an advisory zone flagged along one path"
            >
              <defs>
                <pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse">
                  <path d="M 36 0 L 0 0 0 36" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                </pattern>
              </defs>
              <rect width="900" height="420" fill="url(#grid)" />

              <ellipse cx="560" cy="180" rx="70" ry="46" fill="#FFFFFF" opacity="0.04" />
              <ellipse cx="560" cy="180" rx="70" ry="46" fill="none" stroke="#FFFFFF" strokeWidth="0.75" strokeDasharray="3 4" opacity="0.4" />

              {/* Recommended — solid */}
              <path
                d="M120 320 C 220 260, 300 240, 380 210 C 460 180, 520 150, 620 140 C 700 132, 760 150, 800 110"
                fill="none"
                stroke="#FFFFFF"
                strokeWidth="1.8"
                opacity="0.95"
              />
              {/* Direct — dotted, crosses the advisory zone */}
              <path
                d="M120 320 C 260 270, 420 220, 560 180 C 660 152, 720 130, 800 110"
                fill="none"
                stroke="#FFFFFF"
                strokeWidth="1.3"
                strokeDasharray="1.5 5"
                strokeLinecap="round"
                opacity="0.5"
              />
              {/* Fastest — dashed, wide detour */}
              <path
                d="M120 320 C 240 300, 360 300, 480 260 C 560 232, 640 210, 800 110"
                fill="none"
                stroke="#FFFFFF"
                strokeWidth="1.3"
                strokeDasharray="6 4"
                opacity="0.5"
              />

              {[
                [120, 320],
                [300, 246],
                [460, 182],
                [620, 140],
                [800, 110],
              ].map(([x, y], i) => (
                <circle key={i} cx={x} cy={y} r={3.5} fill="#FFFFFF" />
              ))}

              <text x="105" y="345" fill="#9A9A9A" fontSize="13" fontFamily="Inter, sans-serif">
                Chennai
              </text>
              <text x="770" y="90" fill="#9A9A9A" fontSize="13" fontFamily="Inter, sans-serif">
                Singapore
              </text>
              <text x="520" y="130" fill="#9A9A9A" fontSize="11" fontFamily="Inter, sans-serif" opacity="0.8">
                Advisory zone
              </text>
            </svg>
          </div>

          <div className="grid sm:grid-cols-3 gap-4 mt-6">
            {[
              { label: 'Recommended', detail: 'Low risk · 6d 4h', line: 'border-t-2 border-white' },
              { label: 'Fastest', detail: 'Medium risk · 5d 20h', line: 'border-t-2 border-dashed border-white/50' },
              { label: 'Direct', detail: 'Higher risk · 5d 6h', line: 'border-t-2 border-dotted border-white/40' },
            ].map((card) => (
              <div key={card.label} className="rounded-xl border border-line bg-void/40 p-4">
                <div className={`w-8 mb-3 ${card.line}`} aria-hidden="true" />
                <p className="text-sm text-ink">{card.label}</p>
                <p className="mt-1 text-xs text-mute">{card.detail}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
