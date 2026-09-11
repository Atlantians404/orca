import { Compass, Map, User, LogOut, Plus } from 'lucide-react';
import Reveal from './Reveal';

const RECENT_CHATS = [
  'Chennai → Singapore',
  'Mumbai → Dubai',
  'Safe voyage planning',
  'Weather route analysis',
];

const ROUTES = [
  { name: 'Route 1', risk: 'Low risk', tone: 'low', detail: '6d 4h · shortest, calm seas' },
  { name: 'Route 2', risk: 'Medium risk', tone: 'medium', detail: '5d 20h · faster, one storm band' },
  { name: 'Route 3', risk: 'Higher risk', tone: 'high', detail: '5d 6h · fastest, piracy advisory' },
];

function RiskBadge({ tone, label }) {
  const dot =
    tone === 'high' ? (
      <span className="relative flex h-2 w-2">
        <span className="absolute inline-flex h-full w-full rounded-full bg-white" />
        <span className="absolute -inset-1 rounded-full border border-white/40" />
      </span>
    ) : tone === 'medium' ? (
      <span className="h-2 w-2 rounded-full bg-white/60" />
    ) : (
      <span className="h-2 w-2 rounded-full border border-white/70" />
    );
  return (
    <span className="inline-flex items-center gap-1.5 mt-2 text-[11px] rounded-full border border-line2 px-2 py-0.5 text-mute">
      {dot}
      {label}
    </span>
  );
}

export default function ProductShowcase() {
  return (
    <section className="py-28 md:py-40 border-t border-line">
      <div className="max-w-content mx-auto px-6">
        <Reveal className="max-w-xl">
          <h2 className="font-display font-semibold text-3xl sm:text-4xl tracking-tightest text-ink">
            Ask, and ORCA does the charting.
          </h2>
          <p className="mt-5 text-mute">
            A conversation in, a compared set of routes out — each one scored
            against real maritime risk before you ever open a map.
          </p>
        </Reveal>

        <Reveal delay={0.1} className="mt-14">
          <div className="rounded-2xl border border-line overflow-hidden bg-surface flex flex-col md:flex-row md:h-[520px]">
            <aside className="w-full md:w-60 shrink-0 border-b md:border-b-0 md:border-r border-line p-5 flex md:flex-col justify-between">
              <div className="w-full">
                <div className="flex items-center gap-2 font-display text-sm tracking-tightest text-ink">
                  <Compass size={16} className="text-ink" aria-hidden="true" />
                  ORCA
                </div>
                <button
                  type="button"
                  className="mt-6 hidden md:flex items-center gap-2 text-sm text-mute border border-line2 rounded-lg px-3 py-2 w-full hover:text-ink hover:border-white transition-colors"
                >
                  <Plus size={14} /> New chat
                </button>
                <p className="hidden md:block mt-6 text-xs text-mute2 uppercase tracking-wide">
                  Recent
                </p>
                <ul className="hidden md:block mt-3 space-y-1">
                  {RECENT_CHATS.map((chat) => (
                    <li key={chat}>
                      <button
                        type="button"
                        className="w-full text-left text-sm text-mute hover:text-ink py-1.5 truncate transition-colors"
                      >
                        {chat}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="hidden md:flex flex-col gap-1 pt-4 border-t border-line">
                <button type="button" className="flex items-center gap-2 text-sm text-mute hover:text-ink py-1.5">
                  <Map size={14} /> Maps
                </button>
                <button type="button" className="flex items-center gap-2 text-sm text-mute hover:text-ink py-1.5">
                  <User size={14} /> Profile
                </button>
                <button type="button" className="flex items-center gap-2 text-sm text-mute hover:text-ink py-1.5">
                  <LogOut size={14} /> Log out
                </button>
              </div>
            </aside>

            <div className="flex-1 p-6 md:p-8 flex flex-col overflow-y-auto">
              <p className="text-xs text-mute2 mb-6">How can I help with your voyage?</p>

              <div className="self-end max-w-[85%] bg-surface2 border border-line rounded-2xl rounded-br-sm px-4 py-3 text-sm text-ink">
                Find me the safest route from Chennai to Singapore.
              </div>

              <div className="self-start max-w-[90%] mt-4 text-sm text-mute">
                I've analyzed the available routes and identified 3 possible
                options.
              </div>

              <div className="grid sm:grid-cols-3 gap-3 mt-5">
                {ROUTES.map((route) => (
                  <div
                    key={route.name}
                    className="rounded-xl border border-line bg-void/40 p-4 hover:border-line2 transition-colors"
                  >
                    <p className="text-sm text-ink">{route.name}</p>
                    <RiskBadge tone={route.tone} label={route.risk} />
                    <p className="mt-3 text-xs text-mute2">{route.detail}</p>
                  </div>
                ))}
              </div>

              <div className="mt-6 flex-1 rounded-xl border border-line bg-void/30 min-h-[120px] flex items-center justify-center">
                <svg viewBox="0 0 240 90" className="w-4/5 h-auto" role="img" aria-label="Small preview map of the three compared routes">
                  <path d="M10 70 L60 30 L110 50 L160 20 L230 45" fill="none" stroke="#FFFFFF" strokeWidth="1.2" opacity="0.8" />
                  <path d="M10 70 L70 55 L140 65 L230 45" fill="none" stroke="#FFFFFF" strokeWidth="1.2" strokeDasharray="3 3" opacity="0.4" />
                  <circle cx="10" cy="70" r="3" fill="#FFFFFF" />
                  <circle cx="230" cy="45" r="3" fill="#FFFFFF" />
                </svg>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
