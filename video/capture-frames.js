const pup = require('puppeteer');
const path = require('path');
const DIR = path.join(__dirname, 'frames');

async function main() {
  const b = await pup.launch({ headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });

  // Load page and wait for data
  await p.goto('http://localhost:5173', { waitUntil: 'load', timeout: 10000 });
  await p.waitForFunction(() => document.querySelector('select')?.options?.length > 5, { timeout: 12000 });
  await sleep(1000);

  // --- PRE-SIMULATION FRAMES ---
  // 03: Market selector + scenarios
  await p.screenshot({ path: `${DIR}/03-problem.png` });
  log('03');

  // 05: Empty state (same page, same view - flow diagram visible)
  await p.screenshot({ path: `${DIR}/05-solution-intro.png` });
  log('05');

  // --- RUN BTC OCT 2025 SIMULATION ---
  await p.click('button.run-btn');
  await p.waitForSelector('.stat-hero', { timeout: 20000 });
  await sleep(800);

  // 01: Survival score hero centered
  await p.evaluate(() => document.querySelector('.stat-hero').scrollIntoView({ block: 'center' }));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/01-hook.png` });
  log('01');

  // 02: Full results top
  await p.evaluate(() => window.scrollTo(0, 50));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/02-hook-context.png` });
  log('02');

  // 06: Controls + cascade chart
  await p.evaluate(() => window.scrollTo(0, 350));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/06-walkthrough.png` });
  log('06');

  // 07: Cascade chart zoomed
  await p.evaluate(() => window.scrollTo(0, 520));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/07-cascade.png` });
  log('07');

  // 08: Funding chart
  await p.evaluate(() => window.scrollTo(0, 850));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/08-funding.png` });
  log('08');

  // --- LUNA SCENARIO for frame 04 ---
  await p.evaluate(() => window.scrollTo(0, 0));
  const btns = await p.$$('button.scenario-btn');
  if (btns[1]) await btns[1].click();
  await sleep(300);
  await p.click('button.run-btn');
  await p.waitForSelector('.stat-hero', { timeout: 20000 });
  await sleep(800);
  await p.evaluate(() => window.scrollTo(0, 50));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/04-agitation.png` });
  log('04');

  // --- COMPARE MODE for frame 09 ---
  // Switch back to Oct 2025
  await p.evaluate(() => window.scrollTo(0, 0));
  const btns2 = await p.$$('button.scenario-btn');
  if (btns2[0]) await btns2[0].click();
  await sleep(200);
  await p.click('input[type="checkbox"]');
  await sleep(300);
  await p.evaluate(() => {
    const sliders = document.querySelectorAll('.compare-controls input[type="range"]');
    if (sliders.length > 0) {
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(sliders[0], 20);
      sliders[0].dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await p.click('button.run-btn');
  await p.waitForSelector('.compare-diff', { timeout: 25000 });
  await sleep(800);
  await p.evaluate(() => window.scrollTo(0, 200));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/09-compare.png` });
  log('09');

  // 10: Close - clean header shot with results (uncheck compare, re-run)
  await p.click('input[type="checkbox"]');
  await sleep(200);
  await p.click('button.run-btn');
  await p.waitForSelector('.stat-hero', { timeout: 20000 });
  await sleep(500);
  await p.evaluate(() => window.scrollTo(0, 0));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/10-close.png` });
  log('10');

  await b.close();
  console.log('All 10 frames captured');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function log(n) { console.log(`Frame ${n} done`); }

main().catch(e => { console.error(e.message); process.exit(1); });
