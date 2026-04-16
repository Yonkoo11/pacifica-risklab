const puppeteer = require('puppeteer');
const { PuppeteerScreenRecorder } = require('puppeteer-screen-recorder');

const OUT = '/Users/yonko/Projects/pacifica-risklab/video/screenrec';

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const b = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
    executablePath: '/Users/yonko/.cache/puppeteer/chrome/mac_arm-133.0.6943.126/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
  });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });
  await p.goto('http://localhost:5173', { waitUntil: 'load', timeout: 15000 });
  await p.waitForFunction(() => document.querySelector('select')?.options?.length > 5, { timeout: 15000 });

  // Select Oct 2025
  const scenarioBtns = await p.$$('button.scenario-btn');
  if (scenarioBtns[0]) await scenarioBtns[0].click();
  await sleep(500);

  const recorder = new PuppeteerScreenRecorder(p, { fps: 30, videoFrame: { width: 1920, height: 1080 } });
  await recorder.start(`${OUT}/run-results.mp4`);

  await sleep(500);
  await p.click('button.run-btn');
  await p.waitForSelector('.stat-hero', { timeout: 25000 });
  await sleep(1500);

  // Smooth scroll through results
  await p.evaluate(async () => {
    const smoothScroll = async (target) => {
      const start = window.scrollY;
      const steps = 60;
      for (let i = 0; i <= steps; i++) {
        window.scrollTo(0, start + (target - start) * (i / steps));
        await new Promise(r => setTimeout(r, 25));
      }
    };
    await smoothScroll(300);
    await new Promise(r => setTimeout(r, 1000));
    await smoothScroll(700);
    await new Promise(r => setTimeout(r, 1000));
    await smoothScroll(1050);
    await new Promise(r => setTimeout(r, 1500));
  });

  await recorder.stop();
  console.log('Run recording done');
  await b.close();
}

main().catch(e => { console.error(e.message); process.exit(1); });
