import { useRef, useState, useEffect } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Play, Pause, ChevronLeft, ChevronRight, Volume2, VolumeX, Volume1 } from 'lucide-react';
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
  const [isMuted, setIsMuted] = useState(true);
  const [volume, setVolume] = useState(0.8);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start end', 'end start'],
  });

  // A lighter tilt than a single hero video would use — the slider
  // itself needs to feel stable while stepping through slides.
  const rotateX = useTransform(scrollYProgress, [0, 0.45, 0.55, 1], [10, 0, 0, -6]);
  const scale = useTransform(scrollYProgress, [0, 0.45, 0.55, 1], [0.95, 1, 1, 0.98]);
  const glow = useTransform(scrollYProgress, [0, 0.45, 0.55, 1], [0.08, 0.22, 0.22, 0.1]);

  // Synchronize playback and audio states across video elements
  useEffect(() => {
    videoRefs.current.forEach((el, i) => {
      if (!el) return;
      el.muted = isMuted;
      el.volume = isMuted ? 0 : volume;

      if (i === active) {
        if (playing) {
          el.play().catch(() => {});
        } else {
          el.pause();
        }
      } else {
        el.pause();
      }
    });
  }, [active, playing, isMuted, volume]);

  const goTo = (i) => {
    setActive((i + SLIDES.length) % SLIDES.length);
    setPlaying(true);
  };

  const togglePlay = () => {
    const el = videoRefs.current[active];
    if (!el) return;
    if (el.paused) {
      el.play().catch(() => {});
      setPlaying(true);
    } else {
      el.pause();
      setPlaying(false);
    }
  };

  const toggleMute = () => {
    const newMuted = !isMuted;
    setIsMuted(newMuted);

    const el = videoRefs.current[active];
    if (el) {
      el.muted = newMuted;
      if (!newMuted) {
        const targetVol = volume === 0 ? 0.8 : volume;
        setVolume(targetVol);
        el.volume = targetVol;
        if (el.paused) {
          el.play().catch(() => {});
          setPlaying(true);
        }
      }
    }
  };

  const handleVolumeChange = (e) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (val === 0) {
      setIsMuted(true);
    } else {
      if (isMuted) setIsMuted(false);
    }
    const el = videoRefs.current[active];
    if (el) {
      el.volume = val;
      el.muted = val === 0;
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
          className="relative rounded-[28px] border border-line2 overflow-hidden bg-surface group"
        >
          <div className="relative aspect-video w-full">
            {SLIDES.map((slide, i) => (
              <video
                key={slide.src}
                ref={(el) => (videoRefs.current[i] = el)}
                className="absolute inset-0 h-full w-full object-cover transition-opacity duration-500"
                style={{ opacity: i === active ? 1 : 0, pointerEvents: i === active ? 'auto' : 'none' }}
                src={slide.src}
                muted={isMuted}
                loop
                playsInline
                autoPlay={i === 0}
                aria-hidden={i !== active}
                aria-label={`ORCA ${slide.label}`}
              />
            ))}
            <div className="absolute inset-0 bg-gradient-to-t from-void/60 via-transparent to-void/20 pointer-events-none" />

            {/* Unmute Prompt Badge when Muted */}
            {isMuted && playing && (
              <button
                type="button"
                onClick={toggleMute}
                className="absolute top-5 right-5 flex items-center gap-2 px-3.5 py-2 rounded-full bg-void/80 border border-line2 backdrop-blur-md text-xs font-medium text-ink hover:border-white hover:bg-void transition-all animate-pulse"
                aria-label="Click to enable video sound"
              >
                <VolumeX size={14} className="text-mute" />
                <span>Tap for sound</span>
              </button>
            )}

            {/* Active Sound Indicator (Equalizer) when Audio is Active */}
            {!isMuted && playing && (
              <div className="absolute top-5 right-5 flex items-center gap-2 px-3.5 py-2 rounded-full bg-void/80 border border-line2 backdrop-blur-md text-xs font-medium text-ink">
                <div className="flex items-end gap-0.5 h-3">
                  <span className="w-0.5 bg-emerald-400 rounded-full animate-[bounce_1s_infinite_100ms] h-full" />
                  <span className="w-0.5 bg-emerald-400 rounded-full animate-[bounce_1s_infinite_300ms] h-2/3" />
                  <span className="w-0.5 bg-emerald-400 rounded-full animate-[bounce_1s_infinite_200ms] h-4/5" />
                </div>
                <span className="text-emerald-400 text-xs">Audio Playing</span>
              </div>
            )}

            {/* Bottom Controls Bar */}
            <div className="absolute bottom-5 left-5 right-5 flex items-center justify-between pointer-events-auto">
              <div className="flex items-center gap-3">
                {/* Play / Pause Button */}
                <button
                  type="button"
                  onClick={togglePlay}
                  aria-label={playing ? 'Pause video' : 'Play video'}
                  className="flex items-center justify-center h-11 w-11 rounded-full bg-void/70 border border-line2 backdrop-blur text-ink hover:border-white transition-colors"
                >
                  {playing ? <Pause size={16} /> : <Play size={16} className="ml-0.5" />}
                </button>

                {/* Audio Mute / Unmute & Volume Control */}
                <div
                  className="relative flex items-center"
                  onMouseEnter={() => setShowVolumeSlider(true)}
                  onMouseLeave={() => setShowVolumeSlider(false)}
                >
                  <button
                    type="button"
                    onClick={toggleMute}
                    aria-label={isMuted ? 'Unmute video audio' : 'Mute video audio'}
                    className="flex items-center justify-center h-11 px-3.5 rounded-full bg-void/70 border border-line2 backdrop-blur text-ink hover:border-white transition-colors gap-2"
                  >
                    {isMuted ? (
                      <>
                        <VolumeX size={16} className="text-mute" />
                        <span className="hidden sm:inline text-xs text-mute">Unmute</span>
                      </>
                    ) : volume > 0.5 ? (
                      <>
                        <Volume2 size={16} className="text-emerald-400" />
                        <span className="hidden sm:inline text-xs text-ink font-medium">
                          {Math.round(volume * 100)}%
                        </span>
                      </>
                    ) : (
                      <>
                        <Volume1 size={16} className="text-emerald-400" />
                        <span className="hidden sm:inline text-xs text-ink font-medium">
                          {Math.round(volume * 100)}%
                        </span>
                      </>
                    )}
                  </button>

                  {/* Volume Slider Popup */}
                  {showVolumeSlider && (
                    <motion.div
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -8 }}
                      className="ml-2 flex items-center px-3 py-2 rounded-full bg-void/80 border border-line2 backdrop-blur"
                    >
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={isMuted ? 0 : volume}
                        onChange={handleVolumeChange}
                        aria-label="Volume slider"
                        className="w-20 accent-white cursor-pointer h-1.5 rounded-lg bg-line2"
                      />
                    </motion.div>
                  )}
                </div>
              </div>

              {/* Slider Dots */}
              {SLIDES.length > 1 && (
                <div className="flex items-center gap-2 bg-void/60 border border-line2 backdrop-blur px-3 py-2 rounded-full">
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
              )}
            </div>

            {/* Prev / Next Slide Arrows */}
            {SLIDES.length > 1 && (
              <>
                <button
                  type="button"
                  onClick={() => goTo(active - 1)}
                  aria-label="Previous video"
                  className="absolute top-1/2 -translate-y-1/2 left-4 flex items-center justify-center h-10 w-10 rounded-full bg-void/50 border border-line2 backdrop-blur text-ink hover:border-white transition-colors opacity-0 group-hover:opacity-100"
                >
                  <ChevronLeft size={18} />
                </button>
                <button
                  type="button"
                  onClick={() => goTo(active + 1)}
                  aria-label="Next video"
                  className="absolute top-1/2 -translate-y-1/2 right-4 flex items-center justify-center h-10 w-10 rounded-full bg-void/50 border border-line2 backdrop-blur text-ink hover:border-white transition-colors opacity-0 group-hover:opacity-100"
                >
                  <ChevronRight size={18} />
                </button>
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

