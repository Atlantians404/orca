const LINKS = ['Product', 'How it Works', 'Features', 'About', 'Contact'];

export default function Footer() {
  return (
    <footer className="border-t border-line py-14">
      <div className="max-w-content mx-auto px-6 flex flex-col md:flex-row md:items-start md:justify-between gap-10">
        <div>
          <p className="font-display text-lg tracking-tightest text-ink">ORCA</p>
          <p className="mt-2 text-sm text-mute max-w-xs">
            AI-powered maritime intelligence.
          </p>
        </div>

        <nav aria-label="Footer" className="flex flex-wrap gap-x-6 gap-y-2">
          {LINKS.map((link) => (
            <a
              key={link}
              href={`#${link.toLowerCase().replace(/\s+/g, '-')}`}
              className="text-sm text-mute hover:text-ink transition-colors"
            >
              {link}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-5">
          <a href="/login" className="text-sm text-mute hover:text-ink transition-colors">
            Sign in
          </a>
          <a href="/signup" className="text-sm text-mute hover:text-ink transition-colors">
            Sign up
          </a>
        </div>
      </div>

      <p className="max-w-content mx-auto px-6 mt-10 text-xs text-mute2">
        © {new Date().getFullYear()} ORCA. All rights reserved.
      </p>
    </footer>
  );
}
