const puppeteer = require('puppeteer');
const { PuppeteerScreenRecorder } = require('puppeteer-screen-recorder');
const path = require('path');

const OUT = '/Users/yonko/Projects/pacifica-risklab/video/screenrec';

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function recordSelection() {
  const b = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage'], executablePath: '/Users/yonko/.cache/puppeteer/chrome/mac_arm-133.0.6943.126/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });

  const recorder = new PuppeteerScreenRecorder(p, { fps: 30, videoFrame: { width: 1920, height: 1080 } });

  await p.goto('http://localhost:5173', { waitUntil: 'load', timeout: 15000 });
  await p.waitForFunction(() => document.querySelector('select')?.options?.length > 5, { timeout: 15000 });
  await sleep(500);

  // Record 07-09: market + scenario + parameters (~20s)
  await recorder.start(`${OUT}/selection.mp4`);

  await sleep(1000);

  // Hover over market dropdown
  await p.hover('select');
  await sleep(800);

  // Click scenario 0 (Oct 2025)
  const scenarioBtns = await p.$$('button.scenario-btn');
  if (scenarioBtns[0]) await scenarioBtns[0].click();
  await sleep(1500);

  // Adjust OI slider to 250M
  await p.evaluate(() => {
    const sliders = document.querySelectorAll('input[type="range"]');
    const oiSlider = sliders[0];
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(oiSlider, 250_000_000);
    oiSlider.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await sleep(1000);

  // Slide back down to 100M
  await p.evaluate(() => {
    const sliders = document.querySelectorAll('input[type="range"]');
    const oiSlider = sliders[0];
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(oiSlider, 100_000_000);
    oiSlider.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await sleep(1500);

  // Hover run button
  await p.hover('button.run-btn');
  await sleep(1500);

  await recorder.stop();
  console.log('Selection recording done');

  // Record run + results: click run, wait, scroll through results (~20s)
  await recorder.start(`${OUT}/run.mp4`);
  await sleep(500);

  await p.click('button.run-btn');
  await p.waitForSelector('.stat-hero', { timeout: 25000 });
  await sleep(1500);

  // Scroll through results slowly
  await p.evaluate(async () => {
    const smoothScroll = async (target) => {
      const start = window.scrollY;
      const steps = 30;
      for (let i = 0; i <= steps; i++) {
        window.scrollTo(0, start + (target - start) * (i / steps));
        await new Promise(r => setTimeout(r, 30));
      }
    };
    await smoothScroll(400);
    await new Promise(r => setTimeout(r, 1500));
    await smoothScroll(900);
    await new Promise(r => setTimeout(r, 1500));
  });

  await recorder.stop();
  console.log('Run recording done');

  await b.close();
}

async function recordCompare() {
  const b = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage'], executablePath: '/Users/yonko/.cache/puppeteer/chrome/mac_arm-133.0.6943.126/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });

  await p.goto('http://localhost:5173', { waitUntil: 'load', timeout: 15000 });
  await p.waitForFunction(() => document.querySelector('select')?.options?.length > 5, { timeout: 15000 });
  await sleep(500);

  // Enable compare mode first so it's set up
  await p.click('input[type="checkbox"]');
  await sleep(300);
  await p.evaluate(() => {
    const sliders = document.querySelectorAll('.compare-controls input[type="range"]');
    if (sliders.length > 0) {
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(sliders[0], 20);
      sliders[0].dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(500);

  const recorder = new PuppeteerScreenRecorder(p, { fps: 30, videoFrame: { width: 1920, height: 1080 } });
  await recorder.start(`${OUT}/compare.mp4`);

  await sleep(1500);
  await p.click('button.run-btn');
  await p.waitForSelector('.compare-diff', { timeout: 25000 });
  await sleep(1500);

  await p.evaluate(async () => {
    const smoothScroll = async (target) => {
      const start = window.scrollY;
      const steps = 30;
      for (let i = 0; i <= steps; i++) {
        window.scrollTo(0, start + (target - start) * (i / steps));
        await new Promise(r => setTimeout(r, 30));
      }
    };
    await smoothScroll(400);
    await new Promise(r => setTimeout(r, 1500));
    await smoothScroll(800);
    await new Promise(r => setTimeout(r, 2000));
  });

  await recorder.stop();
  console.log('Compare recording done');
  await b.close();
}

async function main() {
  require('fs').mkdirSync(OUT, { recursive: true });
  await recordSelection();
  await recordCompare();
  console.log('All recordings complete');
}

main().catch(e => { console.error(e.message); process.exit(1); });
