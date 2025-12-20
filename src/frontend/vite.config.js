import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/predict': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/status': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/stats': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
