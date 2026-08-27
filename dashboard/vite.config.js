import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Growth Ops dashboard — dev server proxies /api to the local Express layer
// (server/index.js), which wraps the real Smartlead/HeyReach/Pipedrive clients
// from ../src plus a mock layer for services without credentials configured.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      "/api": {
        target: `http://localhost:${process.env.DASHBOARD_PORT || 5175}`,
        changeOrigin: true,
      },
    },
  },
});
