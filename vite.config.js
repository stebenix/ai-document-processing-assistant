import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  build: {
    // Keep classic max-width media queries intact for older real-device Safari.
    cssMinify: false,
  },
});
