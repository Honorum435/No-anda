import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Redirige las llamadas /api al servidor backend (Express) durante el desarrollo.
    proxy: {
      '/api': 'http://localhost:3001',
    },
  },
})
