import { useState } from 'react';
import AuthModal from '../AuthModal';
import { EyeIcon, EyeOffIcon, ChevronDownIcon } from '../AuthIcons';

// Replace with real data (ideally fetched from your backend / a ports API)
const USER_TYPES = [
  'Researcher',
  'Fishing Vessel Operator',
  'Commercial Shipping',
  'Port Authority',
  'Recreational Sailor',
  'Other',
];

// Placeholder list — swap for a real port/location dataset
const HOME_PORTS = [
  'Chennai, India',
  'Mumbai, India',
  'Visakhapatnam, India',
  'Kochi, India',
  'Other',
];

const initialFormData = {
  fullName: '',
  username: '',
  email: '',
  phone: '',
  userType: '',
  homeLocation: '',
  password: '',
  confirmPassword: '',
};

/**
 * Signup popup.
 * Props:
 *  - isOpen: boolean
 *  - onClose: () => void
 *  - onSwitchToLogin: () => void
 *  - onRegister: (payload) => Promise   (wire this to your API — see handleSubmit below)
 */
export default function Register({ isOpen, onClose, onSwitchToLogin, onRegister }) {
  const [formData, setFormData] = useState(initialFormData);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const validate = () => {
    const next = {};

    if (!formData.fullName.trim()) next.fullName = 'Full name is required';
    if (!formData.username.trim()) next.username = 'Username is required';

    if (!formData.email.trim()) {
      next.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      next.email = 'Enter a valid email address';
    }

    if (!formData.phone.trim()) {
      next.phone = 'Phone number is required';
    } else if (!/^[0-9+\-\s()]{7,15}$/.test(formData.phone)) {
      next.phone = 'Enter a valid phone number';
    }

    if (!formData.userType) next.userType = 'Select a user type';
    if (!formData.homeLocation) next.homeLocation = 'Select a location';

    if (!formData.password) {
      next.password = 'Password is required';
    } else if (formData.password.length < 8) {
      next.password = 'Use at least 8 characters';
    }

    if (!formData.confirmPassword) {
      next.confirmPassword = 'Confirm your password';
    } else if (formData.confirmPassword !== formData.password) {
      next.confirmPassword = 'Passwords do not match';
    }

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    setErrors((prev) => ({ ...prev, form: '' }));

    // Don't send confirmPassword to the backend
    const { confirmPassword, ...payload } = formData;

    try {
      if (onRegister) {
        await onRegister(payload);
      } else {
        // TODO: replace with your actual endpoint once it's ready
        // const res = await fetch('/api/auth/register', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(payload),
        // });
        // if (!res.ok) throw new Error('Could not create account');
        // const data = await res.json();
        console.log('Register payload (no onRegister handler wired yet):', payload);
      }
    } catch (err) {
      setErrors((prev) => ({ ...prev, form: err?.message || 'Something went wrong. Please try again.' }));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthModal isOpen={isOpen} onClose={onClose} wide>
      <div className="auth-header">
        <div className="auth-logo font-display">ORCA</div>
        <h2 className="auth-title font-display">Create your account</h2>
        <p className="auth-subtitle font-body">Marine Intelligence Platform</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        {errors.form && <div className="auth-error-banner font-body">{errors.form}</div>}

        <div className="auth-field">
          <label htmlFor="reg-fullName" className="auth-label font-body">Full Name</label>
          <input
            id="reg-fullName"
            name="fullName"
            type="text"
            className={`auth-input font-body ${errors.fullName ? 'auth-input-error' : ''}`}
            placeholder="Enter your full name"
            value={formData.fullName}
            onChange={handleChange}
            autoComplete="name"
          />
          {errors.fullName && <span className="auth-field-error font-body">{errors.fullName}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="reg-username" className="auth-label font-body">Username</label>
          <input
            id="reg-username"
            name="username"
            type="text"
            className={`auth-input font-body ${errors.username ? 'auth-input-error' : ''}`}
            placeholder="Choose a username"
            value={formData.username}
            onChange={handleChange}
            autoComplete="username"
          />
          {errors.username && <span className="auth-field-error font-body">{errors.username}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="reg-email" className="auth-label font-body">Email</label>
          <input
            id="reg-email"
            name="email"
            type="email"
            className={`auth-input font-body ${errors.email ? 'auth-input-error' : ''}`}
            placeholder="Enter your email"
            value={formData.email}
            onChange={handleChange}
            autoComplete="email"
          />
          {errors.email && <span className="auth-field-error font-body">{errors.email}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="reg-phone" className="auth-label font-body">Phone Number</label>
          <input
            id="reg-phone"
            name="phone"
            type="tel"
            className={`auth-input font-body ${errors.phone ? 'auth-input-error' : ''}`}
            placeholder="Enter your phone number"
            value={formData.phone}
            onChange={handleChange}
            autoComplete="tel"
          />
          {errors.phone && <span className="auth-field-error font-body">{errors.phone}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="reg-userType" className="auth-label font-body">User Type</label>
          <div className="auth-select-wrap">
            <select
              id="reg-userType"
              name="userType"
              className={`auth-select font-body ${errors.userType ? 'auth-input-error' : ''}`}
              value={formData.userType}
              onChange={handleChange}
            >
              <option value="" disabled>Select your user type</option>
              {USER_TYPES.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            <ChevronDownIcon className="auth-select-chevron" />
          </div>
          {errors.userType && <span className="auth-field-error font-body">{errors.userType}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="reg-homeLocation" className="auth-label font-body">Home Port / Location</label>
          <div className="auth-select-wrap">
            <select
              id="reg-homeLocation"
              name="homeLocation"
              className={`auth-select font-body ${errors.homeLocation ? 'auth-input-error' : ''}`}
              value={formData.homeLocation}
              onChange={handleChange}
            >
              <option value="" disabled>Select your location</option>
              {HOME_PORTS.map((port) => (
                <option key={port} value={port}>{port}</option>
              ))}
            </select>
            <ChevronDownIcon className="auth-select-chevron" />
          </div>
          {errors.homeLocation && <span className="auth-field-error font-body">{errors.homeLocation}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="reg-password" className="auth-label font-body">Password</label>
          <div className="auth-input-wrap">
            <input
              id="reg-password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              className={`auth-input font-body ${errors.password ? 'auth-input-error' : ''}`}
              placeholder="Create a password"
              value={formData.password}
              onChange={handleChange}
              autoComplete="new-password"
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

        <div className="auth-field">
          <label htmlFor="reg-confirmPassword" className="auth-label font-body">Confirm Password</label>
          <div className="auth-input-wrap">
            <input
              id="reg-confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              className={`auth-input font-body ${errors.confirmPassword ? 'auth-input-error' : ''}`}
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChange={handleChange}
              autoComplete="new-password"
            />
            <button
              type="button"
              className="auth-eye-btn"
              onClick={() => setShowConfirmPassword((s) => !s)}
              aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
            >
              {showConfirmPassword ? <EyeOffIcon /> : <EyeIcon />}
            </button>
          </div>
          {errors.confirmPassword && <span className="auth-field-error font-body">{errors.confirmPassword}</span>}
        </div>

        <button type="submit" className="auth-submit font-body" disabled={isSubmitting}>
          {isSubmitting ? 'Creating account…' : 'Register'}
        </button>
      </form>

      <p className="auth-switch font-body">
        Already have an account?{' '}
        <button type="button" className="auth-link" onClick={onSwitchToLogin}>
          Login
        </button>
      </p>
    </AuthModal>
  );
}