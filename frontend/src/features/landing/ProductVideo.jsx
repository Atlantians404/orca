import { useRef, useState, useEffect } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Play, Pause, ChevronLeft, ChevronRight } from 'lucide-react';
import Reveal from './Reveal';

// Swap or add files here — the slider adapts to however many entries exist.
const SLIDES = [
  { src: '/videos/orca-demo.mp4', label: 'Product demo' },
  { src: '/videos/orca-promo.mp4', label: 'Cinematic preview' },
];

export default function ProductVideo() {
  const sectionRef = useRef(null);
  const videoRefs = useRef([]);
  const [active, setActive] = useState(0);
  const [playing, setPlaying] = useState(true);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start end', 'end start'],
  });

  // A lighter tilt than a single hero video would use — the slider
  // itself needs to feel stable while stepping through slides.
  const rotateX = useTransform(scrollYProgress, [0, 0.45, 0.55, 1], [10, 0, 0, -6]);
  const scale = useTransform(scrollYProgress, [0, 0.45, 0.55, 1], [0.95, 1, 1, 0.98]);
  const glow = useTransform(scrollYProgress, [0, 0.45, 0.55, 1], [0.08, 0.22, 0.22, 0.1]);

  useEffect(() => {
    videoRefs.current.forEach((el, i) => {
      if (!el) return;
      if (i === active) {
        if (playing) el.play().catch(() => {});
      } else {
        el.pause();
      }
    });
  }, [active, playing]);

  const goTo = (i) => {
    setActive((i + SLIDES.length) % SLIDES.length);
    setPlaying(true);
  };

  const togglePlay = () => {
    const el = videoRefs.current[active];
    if (!el) return;
    if (el.paused) {
      el.play();
      setPlaying(true);
    } else {
      el.pause();
      setPlaying(false);
    }
  };

  return (
    <section id="product" ref={sectionRef} className="relative py-28 md:py-40">
      <div className="max-w-content mx-auto px-6 text-center">
        <Reveal>
          <span className="text-xs text-mute tracking-wide">See ORCA in action</span>
          <h2 className="font-display font-semibold text-3xl sm:text-4xl md:text-5xl tracking-tightest text-ink mt-4">
            From conversation to route.
          </h2>
          <p className="mt-5 text-mute max-w-lg mx-auto">
            Tell ORCA where you're going. ORCA analyzes the voyage and turns your
            request into intelligent route options.
          </p>
        </Reveal>
      </div>

      <div className="max-w-5xl mx-auto mt-14 px-6" style={{ perspective: '1400px' }}>
        <motion.div
          style={{
            rotateX,
            scale,
            transformStyle: 'preserve-3d',
            boxShadow: useTransform(glow, (g) => `0 40px 120px -20px rgba(255,255,255,${g})`),
          }}
          className="relative rounded-[28px] border border-line2 overflow-hidden bg-surface"
        >
          <div className="relative aspect-video w-full">
            {SLIDES.map((slide, i) => (
              <video
                key={slide.src}
                ref={(el) => (videoRefs.current[i] = el)}
                className="absolute inset-0 h-full w-full object-cover transition-opacity duration-500"
                style={{ opacity: i === active ? 1 : 0, pointerEvents: i === active ? 'auto' : 'none' }}
                src={slide.src}
                muted
                loop
                playsInline
                autoPlay={i === 0}
                aria-hidden={i !== active}
                aria-label={`ORCA ${slide.label}`}
              />
            ))}
            <div className="absolute inset-0 bg-gradient-to-t from-void/40 via-transparent to-transparent pointer-events-none" />

            <button
              type="button"
              onClick={togglePlay}
              aria-label={playing ? 'Pause video' : 'Play video'}
              className="absolute bottom-5 left-5 flex items-center justify-center h-11 w-11 rounded-full bg-void/60 border border-line2 backdrop-blur text-ink hover:border-white transition-colors"
            >
              {playing ? <Pause size={16} /> : <Play size={16} className="ml-0.5" />}
            </button>

            {SLIDES.length > 1 && (
              <>
                <button
                  type="button"
                  onClick={() => goTo(active - 1)}
                  aria-label="Previous video"
                  className="absolute top-1/2 -translate-y-1/2 left-4 flex items-center justify-center h-10 w-10 rounded-full bg-void/50 border border-line2 backdrop-blur text-ink hover:border-white transition-colors"
                >
                  <ChevronLeft size={18} />
                </button>
                <button
                  type="button"
                  onClick={() => goTo(active + 1)}
                  aria-label="Next video"
                  className="absolute top-1/2 -translate-y-1/2 right-4 flex items-center justify-center h-10 w-10 rounded-full bg-void/50 border border-line2 backdrop-blur text-ink hover:border-white transition-colors"
                >
                  <ChevronRight size={18} />
                </button>

                <div className="absolute bottom-5 right-5 flex items-center gap-2">
                  {SLIDES.map((slide, i) => (
                    <button
                      key={slide.src}
                      type="button"
                      onClick={() => goTo(i)}
                      aria-label={`Show ${slide.label}`}
                      aria-current={i === active}
                      className={`h-1.5 rounded-full transition-all duration-300 ${
                        i === active ? 'w-6 bg-white' : 'w-1.5 bg-white/35 hover:bg-white/60'
                      }`}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        </motion.div>

        {SLIDES.length > 1 && (
          <p className="mt-4 text-center text-xs text-mute2">{SLIDES[active].label}</p>
        )}
      </div>
    </section>
  );
}
