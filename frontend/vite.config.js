import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// /api requests are forwarded to the FastAPI dev server (fastapi dev backend/main.py).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
