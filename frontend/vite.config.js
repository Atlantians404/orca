import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    cors: true,
    proxy: {
      '/auth': {
        target: 'https://orca-qlqz.onrender.com',
        changeOrigin: true,
        secure: false,
      },
      '/sessions': {
        target: 'https://orca-qlqz.onrender.com',
        changeOrigin: true,
        secure: false,
      },
      '/chat': {
        target: 'https://orca-qlqz.onrender.com',
        changeOrigin: true,
        secure: false,
        bypass: (req) => {
          // If browser is requesting the HTML page for the /chat route, don't proxy to backend
          if (req.headers.accept?.includes('text/html')) {
            return '/index.html';
          }
        },
      },
      '/profile': {
        target: 'https://orca-qlqz.onrender.com',
        changeOrigin: true,
        secure: false,
        bypass: (req) => {
          if (req.headers.accept?.includes('text/html')) {
            return '/index.html';
          }
        },
      },
      '/api': {
        target: 'https://orca-qlqz.onrender.com',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
