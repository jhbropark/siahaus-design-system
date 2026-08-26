import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// SIA.HAUS proposal deck — Vite + React.
export default defineConfig({
  plugins: [react()],
  base: "./",
});
