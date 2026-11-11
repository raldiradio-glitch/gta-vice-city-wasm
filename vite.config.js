import { defineConfig } from "vite";

export default defineConfig({
  // Keep the GitHub Pages path by default; the Python localhost launcher sets
  // VITE_BASE_PATH=/ so built asset URLs work from localhost.
  base: process.env.VITE_BASE_PATH || "/gta-vice-city-wasm/",
  server: {
    headers: {
      "Cross-Origin-Opener-Policy": "same-origin",
      "Cross-Origin-Embedder-Policy": "require-corp",
    },
  },
});
