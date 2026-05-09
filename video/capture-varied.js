const pup = require('puppeteer');
const DIR = '/Users/yonko/Projects/pacifica-risklab/video/frames';

async function main() {
  const b = await pup.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });
  await p.goto('http://localhost:5173', { waitUntil: 'load', timeout: 15000 });
  await p.waitForFunction(() => document.querySelector('select')?.options?.length > 5, { timeout: 15000 });
  await sleep(800);

  // 02: Market dropdown opened — shows "up to 50x leverage across 63 markets"
  // Click to open the select, then click the select again to keep it showing options visually
  await p.evaluate(() => {
    const s = document.querySelector('select');
    s.size = 8;  // Make select display as a list
    s.focus();
  });
  await sleep(400);
  await p.screenshot({ path: `${DIR}/02-problem-setup.png` });
  log('02 market list');

  // Reset select
  await p.evaluate(() => {
    const s = document.querySelector('select');
    s.size = 1;
  });
  await sleep(200);

  // 03: Zoom in on the Crash Scenario card — hover over LUNA which is CATASTROPHIC
  const btns = await p.$$('button.scenario-btn');
  await p.evaluate(() => {
    const section = document.querySelector('.controls section:nth-child(2)');
    if (section) section.scrollIntoView({ block: 'center' });
  });
  if (btns[1]) await btns[1].hover();
  await sleep(400);
  await p.screenshot({ path: `${DIR}/03-gap.png` });
  log('03 scenario focus');

  // 04: Full app zoomed — show the run button highlighted/hovered
  await p.evaluate(() => window.scrollTo(0, 0));
  await p.hover('button.run-btn');
  await sleep(400);
  await p.screenshot({ path: `${DIR}/04-who.png` });
  log('04 run button focus');

  await b.close();
  console.log('Varied frames captured');
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function log(msg) { console.log(msg); }

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
