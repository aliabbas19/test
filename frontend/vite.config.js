import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    // VitePWA({ ... }) // Disabled temporarily to fix cache issues
  ],
  server: {
    host: true,
    port: 5173
  },
  build: {
    outDir: 'dist'
  }
})

