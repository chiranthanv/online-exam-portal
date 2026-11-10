import { fileURLToPath } from "node:url";
import { defineConfig } from "../frontend/node_modules/vite/dist/node/index.js";

export default defineConfig({
  root: fileURLToPath(new URL("../frontend", import.meta.url)),
  server: {
    host: "127.0.0.1",
    port: 5285,
    strictPort: true,
    proxy: {
      "/api": "http://127.0.0.1:8105",
      "/health": "http://127.0.0.1:8105",
    },
  },
});
