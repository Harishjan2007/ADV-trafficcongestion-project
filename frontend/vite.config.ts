import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Synchronize root index.html to frontend/public/index.html
const rootIndexPath = path.resolve(__dirname, '../index.html');
const publicIndexPath = path.resolve(__dirname, 'public/index.html');
try {
  if (fs.existsSync(rootIndexPath)) {
    fs.copyFileSync(rootIndexPath, publicIndexPath);
  }
} catch (e) {
  console.warn('Sync root index.html warning:', e);
}

// Ensure FastAPI backend on port 8000 is running
import http from 'http';
import { spawn } from 'child_process';

function ensureBackend() {
  const req = http.get('http://127.0.0.1:8000/health', (res) => {
    // backend is already running
  });
  req.on('error', () => {
    console.log('[Vite] Starting FastAPI backend on port 8000...');
    const projectRoot = path.resolve(__dirname, '..');
    const uvicorn = spawn('python', ['-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000'], {
      cwd: projectRoot,
      detached: true,
      stdio: 'ignore'
    });
    uvicorn.unref();
  });
}
try {
  ensureBackend();
} catch (e) {
  console.warn('[Vite] ensureBackend error:', e);
}



// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'serve-root-index-html',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          const pathname = req.url ? req.url.split('?')[0] : '';
          if (pathname === '/index.html') {
            if (fs.existsSync(rootIndexPath)) {
              res.setHeader('Content-Type', 'text/html');
              res.end(fs.readFileSync(rootIndexPath, 'utf-8'));
              return;
            }
          }
          next();
        });
      }
    }
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
});













