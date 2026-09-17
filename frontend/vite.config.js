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
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/sessions': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/chat': {
        target: 'http://localhost:8000',
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
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        bypass: (req) => {
          if (req.headers.accept?.includes('text/html')) {
            return '/index.html';
          }
        },
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})

