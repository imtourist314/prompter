import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  return {
    plugins: [vue()],
    server: {
      port: 5174,
      strictPort: true,
      proxy: {
        // Dev convenience: Vue dev server proxies API calls to the Express server.
        '/api': {
          target: 'http://localhost:3050',
          changeOrigin: true
        }
      }
    },
    build: {
      outDir: 'dist',
      emptyOutDir: true
    }
  }
})
