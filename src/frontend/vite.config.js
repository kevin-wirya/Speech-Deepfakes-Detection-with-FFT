import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendTarget = process.env.BACKEND_URL || 'http://localhost:5000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/predict': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/status': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/stats': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/test-datasets': {
        target: backendTarget,
        changeOrigin: true,
      }
    }
  }
})
