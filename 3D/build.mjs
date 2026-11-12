// Бір файлдық нұсқа жинау: dist/erxan3d.html (барлық код пен three.js ішінде).
// Іске қосу:  node build.mjs   (esbuild керек: npx esbuild@0.24.0 автоматты түрде жүктеледі)
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const esbuild = process.env.ESBUILD || 'npx';
const args = [
  join(here, 'src/main.js'), '--bundle', '--format=iife', '--minify', '--target=es2020',
  `--alias:three=${join(here, 'vendor/three.module.min.js')}`,
  '--log-level=warning',
];
// three/addons/... жолдарын vendor/addons-қа бағыттау
const plugin = `--alias:three/addons=${join(here, 'vendor/addons')}`;
const cmd = esbuild === 'npx' ? ['npx', ['--yes', 'esbuild@0.24.0', ...args, plugin]] : [esbuild, [...args, plugin]];
const js = execFileSync(cmd[0], cmd[1], { encoding: 'utf8', maxBuffer: 64 << 20 });

let html = readFileSync(join(here, 'index.html'), 'utf8');
html = html.replace(/<script type="importmap">[\s\S]*?<\/script>\s*<script type="module"[^>]*><\/script>/,
  () => `<script>\n${js.replace(/<\/script/gi, '<\\/script')}\n</script>`);
mkdirSync(join(here, 'dist'), { recursive: true });
writeFileSync(join(here, 'dist/erxan3d.html'), html);
console.log('dist/erxan3d.html', (html.length / 1024).toFixed(0) + ' KB');
