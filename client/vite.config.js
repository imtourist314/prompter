import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_');
  const agentApiTarget = env.VITE_AGENT_API_TARGET || env.VITE_AGENT_API_BASE || 'http://localhost:5333';

  return {
    plugins: [vue()],
    server: {
      port: Number(env.VITE_DEV_SERVER_PORT || 5173),
      host: '0.0.0.0',
      allowedHosts: true,
      proxy: {
        '/agent-api': {
          target: agentApiTarget,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/agent-api/, ''),
        },
      },
    },
    preview: {
      port: Number(env.VITE_PREVIEW_PORT || 4173),
      host: '0.0.0.0',
    },
  };
});
