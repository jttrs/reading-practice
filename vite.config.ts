import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: '/reading-practice/',
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
