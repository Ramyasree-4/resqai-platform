import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          // Core React runtime
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // Data fetching
          'vendor-query': ['@tanstack/react-query', 'axios'],
          // Charts (large — isolated)
          'vendor-recharts': ['recharts'],
          // UI utilities
          'vendor-ui': [
            'lucide-react',
            'sonner',
            'clsx',
            'tailwind-merge',
            'class-variance-authority',
          ],
          // Form / validation
          'vendor-forms': ['react-hook-form', '@hookform/resolvers', 'zod'],
          // Date utils
          'vendor-dates': ['date-fns'],
        },
      },
    },
  },
})
