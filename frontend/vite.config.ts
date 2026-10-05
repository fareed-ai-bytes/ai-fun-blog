import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Inside Docker the API is reachable as http://api:8000; locally (no Docker) as localhost.
const apiTarget = process.env.API_PROXY_TARGET ?? 'http://localhost:8000';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': { target: apiTarget, changeOrigin: false },
    },
  },
});
