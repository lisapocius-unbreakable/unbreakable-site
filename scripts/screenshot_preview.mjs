// Render the built new post + updated listing + updated homepage
// at 1440px and 390px per publishing checklist. Save to /tmp/screens/.
import { chromium } from '/root/.openclaw/plugin-runtime-deps/openclaw-2026.4.23-4eca5026e977/node_modules/playwright-core/index.mjs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { mkdirSync, existsSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(__dirname, '..');
const OUT = '/tmp/screens';
mkdirSync(OUT, { recursive: true });

const pages = [
  { name: 'post', path: 'blog/protein-and-fracture-recovery.html' },
  { name: 'blog-list', path: 'blog/index.html' },
  { name: 'home', path: 'index.html' },
];

const viewports = [
  { name: 'desktop', w: 1440, h: 900 },
  { name: 'mobile',  w: 390,  h: 844 },
];

const browser = await chromium.launch();

for (const p of pages) {
  const url = 'file://' + resolve(REPO, p.path);
  for (const v of viewports) {
    const ctx = await browser.newContext({
      viewport: { width: v.w, height: v.h },
      deviceScaleFactor: 1,
    });
    const page = await ctx.newPage();
    // Silence console errors (missing fonts from CDN when offline is fine to note)
    page.on('pageerror', (e) => console.error(`  ! ${p.name} ${v.name} pageerror:`, e.message));
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
    } catch (e) {
      console.error(`  ! ${p.name} ${v.name} nav err: ${e.message} (continuing anyway)`);
    }
    // Wait a bit for fonts/layout to settle
    await page.waitForTimeout(1500);
    const out = `${OUT}/${p.name}-${v.name}.png`;
    await page.screenshot({ path: out, fullPage: true });
    const sz = (await import('fs')).statSync(out).size;
    console.log(`  wrote ${out} (${Math.round(sz/1024)}KB)`);
    await ctx.close();
  }
}

await browser.close();
console.log('done.');
