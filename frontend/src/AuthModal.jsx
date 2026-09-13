import { useEffect } from 'react';
import { CloseIcon } from './AuthIcons';
import './auth.css';

/**
 * Shared shell for the login/signup popups: dark backdrop + glass card + teal glow,
 * matching the ORCA landing page. Renders nothing when isOpen is false.
 */
export default function AuthModal({ isOpen, onClose, children, wide = false, glow = true }) {
  // Close on Escape, lock background scroll while open
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('keydown', handleKeyDown);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="auth-overlay"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className={`auth-card${wide ? ' auth-card-wide' : ''}`} role="dialog" aria-modal="true">
        {glow && <div className="auth-glow" aria-hidden="true" />}
        <button type="button" className="auth-close" onClick={onClose} aria-label="Close">
          <CloseIcon />
        </button>
        <div className="auth-card-content">{children}</div>
      </div>
    </div>
  );
}