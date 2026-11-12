// Render one still per visual style: node Монтаж/work/reel_03/stills.js <outDir> <time>
const { chromium } = require('playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const [outDir, t = '26.2'] = process.argv.slice(2);
const root = process.cwd();
const server = http.createServer((req, res) => {
  const f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(root) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': f.endsWith('.js') ? 'text/javascript' : 'text/html' });
  fs.createReadStream(f).pipe(res);
});
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  for (const st of ['minimal', 'premium', 'wood', 'toon', 'blueprint']) {
    const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
    pg.on('pageerror', e => console.error(st, e.message));
    await pg.goto(`http://127.0.0.1:${server.address().port}/${encodeURI('Монтаж/work/reel_03/anim.html')}?style=${st}&still=1`);
    await pg.waitForFunction('window.ready === true');
    await pg.evaluate(x => window.renderAt(x), +t);
    await pg.screenshot({ path: path.join(outDir, `style_${st}.jpg`), type: 'jpeg', quality: 90 });
    await pg.close();
  }
  await b.close(); server.close();
})();
