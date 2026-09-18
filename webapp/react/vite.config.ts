import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// GitHub Pages はサブパス配信（https://<user>.github.io/<repo>/）なので、
// アセットは相対パスで参照させる。これを外すと本番で 404 になる。
export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
});
