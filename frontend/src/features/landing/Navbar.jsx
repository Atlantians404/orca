import { useEffect, useState } from 'react';
import { Menu, X } from 'lucide-react';
import logo from '../../assets/logo.png';

const NAV_LINKS = [
  { label: 'Product', href: '#product' },
  { label: 'How it Works', href: '#how-it-works' },
  { label: 'Features', href: '#features' },
  { label: 'About', href: '#about' },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-colors duration-500 ${
        scrolled ? 'backdrop-blur-md border-b border-line' : 'border-b border-transparent'
      }`}
      style={{ backgroundColor: scrolled ? 'rgba(5,5,5,0.75)' : 'transparent' }}
    >
      <nav
        className="max-w-content mx-auto flex items-center justify-between px-6 md:px-10 h-16 md:h-20"
        aria-label="Primary"
      >
        <a href="#top" className="flex items-center gap-3">
          <img src={logo} alt="ORCA logo" className="h-12 w-15 md:h-26 md:w-25 object-contain" />
          <span className="font-display text-xl md:text-2xl tracking-tightest text-ink">ORCA</span>
        </a>

        <ul className="hidden md:flex items-center gap-9">
          {NAV_LINKS.map((link) => (
            <li key={link.label}>
              <a
                href={link.href}
                className="text-sm text-mute hover:text-ink transition-colors duration-300"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden md:flex items-center gap-5">
          <a href="/login" className="text-sm text-mute hover:text-ink transition-colors duration-300">
            Sign in
          </a>
          <a
            href="/signup"
            className="text-sm text-ink border border-line2 rounded-full px-4 py-2 hover:border-white hover:bg-white/5 transition-colors duration-300"
          >
            Sign up
          </a>
        </div>

        <button
          type="button"
          className="md:hidden text-ink"
          aria-label={open ? 'Close menu' : 'Open menu'}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {open && (
        <div className="md:hidden border-t border-line bg-void/95 backdrop-blur-md px-6 pb-6 pt-2">
          <ul className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <li key={link.label}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block py-3 text-base text-mute hover:text-ink transition-colors"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
          <div className="flex items-center gap-4 mt-3 pt-4 border-t border-line">
            <a href="/login" className="text-sm text-mute hover:text-ink">
              Sign in
            </a>
            <a
              href="/signup"
              className="text-sm text-ink border border-line2 rounded-full px-4 py-2 hover:border-white transition-colors"
            >
              Sign up
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
