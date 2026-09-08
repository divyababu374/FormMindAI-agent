import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'charts-vendor': ['chart.js', 'react-chartjs-2'],
          'icons-vendor': ['lucide-react'],
          'utils-vendor': ['clsx', 'tailwind-merge', 'html2canvas', 'canvas-confetti', '@supabase/supabase-js']
        }
      }
    }
  }
})
