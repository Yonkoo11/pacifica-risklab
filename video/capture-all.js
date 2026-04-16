const pup = require('puppeteer');
const DIR = '/Users/yonko/Projects/pacifica-risklab/video/frames';

async function main() {
  const b = await pup.launch({ headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });
  await p.goto('http://localhost:5173', { waitUntil: 'load', timeout: 15000 });
  await p.waitForFunction(() => document.querySelector('select')?.options?.length > 5, { timeout: 15000 });
  await sleep(800);

  // 02: market selector visible (before any selection)
  await p.screenshot({ path: `${DIR}/02-problem-setup.png` });
  log('02');

  // 03: scenario list visible (same page, same view)
  await p.screenshot({ path: `${DIR}/03-gap.png` });
  log('03');

  // 04: empty state full view
  await p.screenshot({ path: `${DIR}/04-who.png` });
  log('04');

  // 05: empty state with flow diagram
  await p.screenshot({ path: `${DIR}/05-intro.png` });
  log('05');

  // 06: hover/active state on scenario
  const btns = await p.$$('button.scenario-btn');
  if (btns[0]) await btns[0].click();
  await sleep(300);
  await p.screenshot({ path: `${DIR}/06-fit.png` });
  log('06');

  // 07: market dropdown highlighted (scroll to top so market section shows)
  await p.evaluate(() => document.querySelector('.controls').scrollIntoView());
  await sleep(200);
  await p.screenshot({ path: `${DIR}/07-market.png` });
  log('07');

  // 08: scenario list focused
  await p.screenshot({ path: `${DIR}/08-scenario.png` });
  log('08');

  // 09: sliders area
  await p.evaluate(() => {
    const sliders = document.querySelectorAll('input[type="range"]');
    if (sliders.length > 0) sliders[0].scrollIntoView({ block: 'center' });
  });
  await sleep(200);
  await p.screenshot({ path: `${DIR}/09-parameters.png` });
  log('09');

  // RUN SIMULATION
  await p.click('button.run-btn');
  await p.waitForSelector('.stat-hero', { timeout: 25000 });
  await sleep(1000);

  // 11: stats grid visible
  await p.evaluate(() => document.querySelector('.summary').scrollIntoView({ block: 'start' }));
  await sleep(300);
  await p.screenshot({ path: `${DIR}/11-stats.png` });
  log('11');

  // 13: funding chart
  await p.evaluate(() => {
    const headings = document.querySelectorAll('h3');
    for (const h of headings) if (h.textContent.includes('Funding')) { h.scrollIntoView(); break; }
  });
  await sleep(300);
  await p.screenshot({ path: `${DIR}/13-funding.png` });
  log('13');

  // 15: limitations section
  await p.evaluate(() => {
    const lim = document.querySelector('.limitations');
    if (lim) lim.scrollIntoView({ block: 'center' });
  });
  await sleep(300);
  await p.screenshot({ path: `${DIR}/15-limits.png` });
  log('15');

  // 18: Full app clean shot (market info card)
  await p.evaluate(() => window.scrollTo(0, 0));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/18-builder.png` });
  log('18');

  // 19: Full view showing live OI at $445
  await p.evaluate(() => window.scrollTo(0, 0));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/19-who-uses.png` });
  log('19');

  // 20: results top with stats
  await p.evaluate(() => document.querySelector('.stat-hero').scrollIntoView({ block: 'center' }));
  await sleep(300);
  await p.screenshot({ path: `${DIR}/20-why-now.png` });
  log('20');

  // 21: full app clean
  await p.evaluate(() => window.scrollTo(0, 0));
  await sleep(200);
  await p.screenshot({ path: `${DIR}/21-roadmap.png` });
  log('21');

  await b.close();
  console.log('Main frames captured');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function log(n) { console.log(`Frame ${n} done`); }

main().catch(e => { console.error(e.message); process.exit(1); });
