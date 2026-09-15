// r5 fetch: node fetch.js <mode> <url> <outfile> [jsfile]
// modes: html (page HTML after load+challenge), text (innerText), pdf (download bytes via page.request after visiting origin), js (run JS file in page, JSON result)
const { chromium } = require('playwright');
const fs = require('fs');
const [,, mode, url, out, jsfile] = process.argv;
const PROFILE = process.env.R5_PROFILE || '/Users/rupertlim/AI_Projects/ConferenceApp/scratchpad/r5tool/profile';
(async () => {
  const ctx = await chromium.launchPersistentContext(PROFILE, { channel: 'chrome', headless: false, viewport: { width: 1400, height: 900 },
    args: ['--disable-blink-features=AutomationControlled'] });
  const page = ctx.pages()[0] || await ctx.newPage();
  const waitChallenge = async () => {
    for (let i = 0; i < 30; i++) {
      const t = await page.title().catch(() => '');
      if (!/just a moment|attention required|checking your browser/i.test(t)) return t;
      await page.waitForTimeout(1000);
    }
    return await page.title();
  };
  try {
    if (mode === 'pdf') {
      const origin = new URL(url).origin;
      const warm = process.env.WARM_URL || origin;
      await page.goto(warm, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      const t = await waitChallenge();
      await page.waitForTimeout(1500);
      const r = await page.evaluate(async (u) => {
        const resp = await fetch(u, { credentials: 'include' });
        const buf = new Uint8Array(await resp.arrayBuffer());
        let bin = ''; for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
        return { status: resp.status, type: resp.headers.get('content-type'), b64: btoa(bin) };
      }, url);
      const buf = Buffer.from(r.b64, 'base64');
      fs.writeFileSync(out, buf);
      console.log(JSON.stringify({ warmTitle: t, status: r.status, type: r.type, bytes: buf.length }));
    } else if (mode === 'dl') {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await waitChallenge();
      await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(3000);
      const btn = page.locator('#downloadCommand, [data-automation-id="downloadCommand"]').first();
      const alt = page.getByRole('menuitem', { name: /download/i }).first();
      const [dl] = await Promise.all([
        page.waitForEvent('download', { timeout: 120000 }),
        (async () => { if (await btn.count()) await btn.click(); else if (await alt.count()) await alt.click(); else throw new Error('no Download control; title=' + await page.title()); })(),
      ]);
      await dl.saveAs(out);
      console.log(JSON.stringify({ suggested: dl.suggestedFilename(), bytes: fs.statSync(out).size, url: page.url().slice(0, 120) }));
    } else {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      const title = await waitChallenge();
      await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
      if (mode === 'html') { fs.writeFileSync(out, await page.content()); }
      else if (mode === 'text') { fs.writeFileSync(out, await page.evaluate(() => document.body.innerText)); }
      else if (mode === 'js') { const code = fs.readFileSync(jsfile, 'utf8'); const r = await page.evaluate(code); fs.writeFileSync(out, JSON.stringify(r, null, 1)); }
      console.log(JSON.stringify({ title, url: page.url(), bytes: fs.statSync(out).size }));
    }
  } catch (e) { console.log('ERROR ' + e.message.split('\n')[0]); process.exitCode = 1; }
  await ctx.close();
})();
