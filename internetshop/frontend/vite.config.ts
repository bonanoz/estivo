import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

// Build output lives inside the Django static dir so collectstatic picks it up.
// django-vite reads the manifest at <outDir>/.vite/manifest.json (Vite >= 5).
// Paths are relative to this folder (the Vite root).
export default defineConfig({
  plugins: [tailwindcss()],
  base: '/static/dist/',
  build: {
    outDir: '../shop/static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: 'src/main.ts',
    },
  },
  server: {
    host: 'localhost',
    port: 5173,
    strictPort: true,
    origin: 'http://localhost:5173',
  },
});
