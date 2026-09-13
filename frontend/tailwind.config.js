/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        void: '#050505',
        deep: '#0A0A0A',
        surface: '#0F0F0F',
        surface2: '#161616',
        line: 'rgba(255,255,255,0.08)',
        line2: 'rgba(255,255,255,0.16)',
        ink: '#FFFFFF',
        mute: '#9A9A9A',
        mute2: '#5C5C5C',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      letterSpacing: {
        tightest: '-0.04em',
      },
      maxWidth: {
        content: '1180px',
      },
    },
  },
  plugins: [],
};
