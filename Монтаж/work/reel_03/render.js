// Render anim.html frame by frame to a silent MP4.
// Usage (from repo root): node Монтаж/work/reel_03/render.js <out.mp4> [seconds] [fps] [stepFrames]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const [out, secs = '33', fps = '30', step = '1'] = process.argv.slice(2);
const root = process.cwd();
const types = { '.html': 'text/html', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  const f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(root) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
const listening = new Promise(r => server.listen(0, '127.0.0.1', r));

(async () => {
  await listening;
  const port = server.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto(`http://127.0.0.1:${port}/${encodeURI('Монтаж/work/reel_03/anim.html')}`);
  await page.waitForFunction('window.ready === true', null, { timeout: 30000 });
  await page.evaluate(() => document.fonts.ready);
  const total = Math.round(+secs * +fps);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(+fps / +step), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', fps, out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < total; f += +step) {
    await page.evaluate(t => window.renderAt(t), f / +fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log('frame', f, '/', total);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  server.close();
})();
