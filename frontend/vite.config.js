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
      },
      '/profile': {
        target: 'https://orca-qlqz.onrender.com',
        changeOrigin: true,
        secure: false,
      },
      '/api': {
        target: 'https://orca-qlqz.onrender.com',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
