import { useState } from 'react';
import AuthModal from '../AuthModal';
import { EyeIcon, EyeOffIcon } from '../AuthIcons';

/**
 * Login popup.
 * Props:
 *  - isOpen: boolean, controls visibility
 *  - onClose: () => void
 *  - onSwitchToRegister: () => void   (called when the user taps "Sign up")
 *  - onForgotPassword: () => void     (called when the user taps "Forgot password?")
 *  - onLogin: (payload) => Promise    (wire this to your API — see handleSubmit below)
 */
export default function Login({ isOpen, onClose, onSwitchToRegister, onForgotPassword, onLogin }) {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const validate = () => {
    const nextErrors = {};
    if (!formData.username.trim()) nextErrors.username = 'Username is required';
    if (!formData.password) nextErrors.password = 'Password is required';
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    setErrors((prev) => ({ ...prev, form: '' }));

    try {
      if (onLogin) {
        // Delegate to whatever the parent wires up (e.g. a fetch/axios call to
        // POST /api/auth/login). Expected to throw on failure.
        await onLogin(formData);
      } else {
        // TODO: replace with your actual endpoint once it's ready
        // const res = await fetch('/api/auth/login', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(formData),
        // });
        // if (!res.ok) throw new Error('Invalid username or password');
        // const data = await res.json();
        console.log('Login payload (no onLogin handler wired yet):', formData);
      }
    } catch (err) {
      setErrors((prev) => ({ ...prev, form: err?.message || 'Something went wrong. Please try again.' }));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthModal isOpen={isOpen} onClose={onClose} glow={false}>
      <div className="auth-header">
        <div className="auth-logo font-display">ORCA</div>
        <h2 className="auth-title font-display">Welcome back</h2>
        <p className="auth-subtitle font-body">Sign in to your account</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        {errors.form && <div className="auth-error-banner font-body">{errors.form}</div>}

        <div className="auth-field">
          <label htmlFor="login-username" className="auth-label font-body">Username</label>
          <input
            id="login-username"
            name="username"
            type="text"
            className={`auth-input font-body ${errors.username ? 'auth-input-error' : ''}`}
            placeholder="Enter your username"
            value={formData.username}
            onChange={handleChange}
            autoComplete="username"
          />
          {errors.username && <span className="auth-field-error font-body">{errors.username}</span>}
        </div>

        <div className="auth-field">
          <div className="auth-label-row">
            <label htmlFor="login-password" className="auth-label font-body">Password</label>
            <button type="button" className="auth-link-inline auth-link-neutral font-body" onClick={onForgotPassword}>
              Forgot password?
            </button>
          </div>
          <div className="auth-input-wrap">
            <input
              id="login-password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              className={`auth-input font-body ${errors.password ? 'auth-input-error' : ''}`}
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              autoComplete="current-password"
            />
            <button
              type="button"
              className="auth-eye-btn"
              onClick={() => setShowPassword((s) => !s)}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOffIcon /> : <EyeIcon />}
            </button>
          </div>
          {errors.password && <span className="auth-field-error font-body">{errors.password}</span>}
        </div>

        <button type="submit" className="auth-submit font-body" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in…' : 'Log in'}
        </button>
      </form>

      <p className="auth-switch font-body">
        Don&apos;t have an account?{' '}
        <button type="button" className="auth-link auth-link-neutral" onClick={onSwitchToRegister}>
          Sign up
        </button>
      </p>
    </AuthModal>
  );
}