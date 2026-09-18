import { chromium } from 'playwright';
import { randomUUID } from 'node:crypto';
import { mkdir, rename, writeFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';

let browser = null;
let browserHeadless = false; // default: headed (visible browser window)
const sessions = new Map();

const DEFAULT_OUTPUT_DIR = process.env.RECORDING_OUTPUT_DIR || './recordings';

/** Set headless mode. Call before first recording. */
export function setHeadless(headless) {
  browserHeadless = headless;
}

/** Launch browser lazily on first recording. */
async function ensureBrowser() {
  if (!browser || !browser.isConnected()) {
    browser = await chromium.launch({ headless: browserHeadless });
  }
  return browser;
}

/**
 * Start recording a page.
 * Creates a new BrowserContext with recordVideo enabled,
 * navigates to the URL, and stores the session.
 */
export async function startRecording(url, options = {}) {
  const b = await ensureBrowser();

  const width = options.width || 1280;
  const height = options.height || 720;
  const outputDir = options.outputDir || DEFAULT_OUTPUT_DIR;
  const sessionId = randomUUID().slice(0, 8);

  await mkdir(outputDir, { recursive: true });

  // Each context gets its own video recording
  const context = await b.newContext({
    recordVideo: {
      dir: outputDir,
      size: { width, height }
    },
    viewport: { width, height }
  });

  const page = await context.newPage();
  const cursorOverlay = options.cursorOverlay !== false;

  // Full-page navigations replace the DOM, including Pagecast's synthetic cursor.
  // Re-inject after every navigation so redirects, login flows, and hard reloads
  // do not make the cursor disappear from the recording.
  if (cursorOverlay) {
    page.on('domcontentloaded', () => {
      void injectDemoOverlay(page).catch(() => {});
    });
  }

  // Use 'load' instead of 'networkidle' — some pages never idle (WebSocket, polling)
  await page.goto(url, { waitUntil: 'load', timeout: 30_000 });

  // Inject cursor highlight + click ripple for demo visibility
  if (cursorOverlay) {
    await injectDemoOverlay(page);
  }

  const startedAt = new Date().toISOString();
  const timeline = {
    viewport: { width, height },
    startedAt,
    events: [],
  };
  sessions.set(sessionId, { context, page, url, startedAt, outputDir, width, height, timeline, cursorOverlay });

  return { sessionId, url, startedAt };
}

/**
 * Interact with a recording session's page.
 * Allows scrolling, clicking, waiting — so the recording captures real interactions.
 */
export async function interactWithPage(sessionId, actions) {
  const session = sessions.get(sessionId);
  if (!session) throw new Error(`Session ${sessionId} not found. Active sessions: ${[...sessions.keys()].join(', ') || 'none'}`);

  const { page, timeline } = session;
  const recordingStartMs = new Date(session.startedAt).getTime();
  const results = [];

  for (const action of actions) {
    // Restore an overlay removed by an SPA body replacement or a navigation whose
    // DOMContentLoaded callback raced with the next MCP action.
    if (session.cursorOverlay) {
      await injectDemoOverlay(page).catch(() => {});
    }

    // Capture timestamp relative to recording start (in seconds)
    const timestamp = (Date.now() - recordingStartMs) / 1000;

    // Try to get bounding box for zoomable actions
    let boundingBox = null;
    let recordedText = action.text || null;

    switch (action.type) {
      case 'wait':
        await new Promise(r => setTimeout(r, (action.ms || 1000)));
        results.push(`Waited ${action.ms || 1000}ms`);
        break;
      case 'scroll':
        await page.evaluate(({ x, y }) => window.scrollBy(x, y), { x: action.x || 0, y: action.y || 300 });
        results.push(`Scrolled by (${action.x || 0}, ${action.y || 300})`);
        break;
      case 'click':
        boundingBox = await safeBoundingBox(page, action.selector);
        await positionDemoCursor(page, boundingBox);
        await page.click(action.selector, { timeout: 5000 });
        results.push(`Clicked ${action.selector}`);
        break;
      case 'hover':
        if (action.x !== undefined && action.y !== undefined) {
          // Synthesize a small bounding box around cursor position
          boundingBox = { x: action.x - 20, y: action.y - 20, width: 40, height: 40 };
          await positionDemoCursor(page, boundingBox);
          results.push(`Hovered at (${action.x}, ${action.y})`);
        } else {
          boundingBox = await safeBoundingBox(page, action.selector);
          await positionDemoCursor(page, boundingBox);
          await page.hover(action.selector, { timeout: 5000 });
          results.push(`Hovered ${action.selector}`);
        }
        break;
      case 'type': {
        const sensitive = await isSensitiveInput(page, action.selector);
        if (action.selector) {
          boundingBox = await safeBoundingBox(page, action.selector);
          await positionDemoCursor(page, boundingBox);
          await page.click(action.selector, { timeout: 5000 });
        } else {
          // No selector — get bounding box of the currently focused element
          boundingBox = await activeElementBoundingBox(page);
        }
        await page.keyboard.type(action.text || '', { delay: action.delay || 80 });
        recordedText = sensitive ? '[REDACTED]' : recordedText;
        results.push(`Typed "${sensitive ? '[REDACTED]' : action.text}" ${action.selector ? 'in ' + action.selector : ''}`);
        break;
      }
      case 'press':
        await page.keyboard.press(action.key || 'Enter');
        results.push(`Pressed ${action.key || 'Enter'}`);
        break;
      case 'select':
        boundingBox = await safeBoundingBox(page, action.selector);
        await positionDemoCursor(page, boundingBox);
        await page.selectOption(action.selector, action.value, { timeout: 5000 });
        results.push(`Selected "${action.value}" in ${action.selector}`);
        break;
      case 'navigate':
        await page.goto(action.url, { waitUntil: 'load', timeout: 30_000 });
        if (session.cursorOverlay) {
          await injectDemoOverlay(page);
        }
        results.push(`Navigated to ${action.url}`);
        break;
      case 'waitForSelector':
        await page.waitForSelector(action.selector, { timeout: action.timeout || 15_000, state: action.state || 'visible' });
        results.push(`Waited for ${action.selector}`);
        break;
      default:
        results.push(`Unknown action: ${action.type}`);
    }

    // Record event in timeline
    timeline.events.push({
      timestamp,
      type: action.type,
      selector: action.selector || null,
      text: recordedText,
      delay: action.delay || null,
      boundingBox,
    });
  }

  return results;
}

/** Safely get bounding box for a selector. Returns null if element not found or not visible. */
async function safeBoundingBox(page, selector) {
  if (!selector) return null;
  try {
    const locator = page.locator(selector).first();
    const box = await locator.boundingBox({ timeout: 2000 });
    return box; // { x, y, width, height } or null
  } catch {
    return null;
  }
}

/**
 * Move both Playwright's virtual pointer and Pagecast's DOM cursor.
 * Some complex apps do not deliver synthetic mousemove events to document-level
 * listeners consistently, so setting left/top explicitly keeps recordings honest.
 */
async function positionDemoCursor(page, boundingBox) {
  if (!boundingBox) return;
  const x = boundingBox.x + boundingBox.width / 2;
  const y = boundingBox.y + boundingBox.height / 2;

  const setPosition = () => page.evaluate(({ x, y }) => {
    const cursor = document.getElementById('pagecast-cursor');
    if (!cursor) return;
    cursor.style.left = `${x}px`;
    cursor.style.top = `${y}px`;
    cursor.style.opacity = '1';
  }, { x, y });

  await setPosition();
  await page.mouse.move(x, y, { steps: 10 });
  // Preserve the explicit position even if app-level pointer handlers interfere.
  await setPosition();
  await new Promise((resolve) => setTimeout(resolve, 120));
}

/** Detect fields whose values must not be written to MCP output or timelines. */
async function isSensitiveInput(page, selector) {
  try {
    const locator = selector ? page.locator(selector).first() : page.locator(':focus');
    return await locator.evaluate((el) => {
      const type = (el.getAttribute('type') || '').toLowerCase();
      const identity = [el.getAttribute('name'), el.getAttribute('id'), el.getAttribute('autocomplete')]
        .filter(Boolean)
        .join(' ');
      return type === 'password' || /password|passwd|secret|token|one-time-code/i.test(identity);
    });
  } catch {
    return false;
  }
}

/** Get bounding box of the currently focused (active) element. */
async function activeElementBoundingBox(page) {
  try {
    return await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const rect = el.getBoundingClientRect();
      return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
    });
  } catch {
    return null;
  }
}

/**
 * Inject cursor highlight + click ripple CSS/JS into the page.
 * This makes the cursor and clicks visible in the recording —
 * critical for demo GIFs where there's no real mouse cursor captured.
 */
export async function injectDemoOverlay(page) {
  await page.evaluate(() => {
    let style = document.getElementById('pagecast-overlay');
    if (!style) {
      style = document.createElement('style');
      style.id = 'pagecast-overlay';
      style.textContent = `
      #pagecast-cursor {
        position: fixed;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: rgba(255, 82, 82, 0.7);
        border: 2px solid rgba(255, 255, 255, 0.9);
        pointer-events: none;
        z-index: 999999;
        transform: translate(-50%, -50%);
        transition: transform 0.1s ease, opacity 0.15s ease;
        box-shadow: 0 0 8px rgba(255, 82, 82, 0.4);
      }
      #pagecast-cursor.clicking {
        transform: translate(-50%, -50%) scale(0.7);
      }
      .pagecast-ripple {
        position: fixed;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: 2px solid rgba(255, 82, 82, 0.8);
        pointer-events: none;
        z-index: 999998;
        transform: translate(-50%, -50%) scale(1);
        animation: pagecast-ripple-expand 0.6s ease-out forwards;
      }
      @keyframes pagecast-ripple-expand {
        0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
        100% { transform: translate(-50%, -50%) scale(2.5); opacity: 0; }
      }
      `;
      document.head.appendChild(style);
    }

    // Restore the cursor if an SPA replaced body contents while keeping <head>.
    let cursor = document.getElementById('pagecast-cursor');
    if (!cursor) {
      cursor = document.createElement('div');
      cursor.id = 'pagecast-cursor';
      document.body.appendChild(cursor);
    }

    // Bind listeners once per Document. A full navigation creates a new Document,
    // so this marker naturally resets and listeners are installed again.
    if (!document.documentElement.dataset.pagecastOverlayBound) {
      document.documentElement.dataset.pagecastOverlayBound = 'true';

      document.addEventListener('mousemove', (e) => {
        const currentCursor = document.getElementById('pagecast-cursor');
        if (!currentCursor) return;
        currentCursor.style.left = e.clientX + 'px';
        currentCursor.style.top = e.clientY + 'px';
      }, true);

      document.addEventListener('mousedown', (e) => {
        const currentCursor = document.getElementById('pagecast-cursor');
        currentCursor?.classList.add('clicking');
        const ripple = document.createElement('div');
        ripple.className = 'pagecast-ripple';
        ripple.style.left = e.clientX + 'px';
        ripple.style.top = e.clientY + 'px';
        document.body.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
      }, true);

      document.addEventListener('mouseup', () => {
        document.getElementById('pagecast-cursor')?.classList.remove('clicking');
      }, true);
    }
  });
}

/**
 * Stop recording.
 * Closes the context (which flushes the video to disk),
 * renames the auto-generated file to a predictable name.
 */
export async function stopRecording(sessionId) {
  const session = sessions.get(sessionId);
  if (!session) throw new Error(`Session ${sessionId} not found. Active sessions: ${[...sessions.keys()].join(', ') || 'none'}`);

  // Get the auto-generated video path before closing
  const videoPath = await session.page.video().path();

  // Close context — this finalizes the video file
  await session.context.close();

  // Rename to predictable name
  const finalPath = join(session.outputDir, `recording-${sessionId}.webm`);
  await rename(videoPath, finalPath);

  const duration = ((Date.now() - new Date(session.startedAt).getTime()) / 1000).toFixed(1);

  // Save event timeline as JSON (used by zoom pipelines)
  const timeline = session.timeline;
  timeline.duration = parseFloat(duration);
  const timelinePath = finalPath.replace(/\.webm$/, '-timeline.json');
  await writeFile(timelinePath, JSON.stringify(timeline, null, 2));

  sessions.delete(sessionId);

  return { webmPath: finalPath, timelinePath, durationSeconds: parseFloat(duration) };
}

/** List active recording sessions. */
export function listSessions() {
  return [...sessions.entries()].map(([id, s]) => ({
    sessionId: id,
    url: s.url,
    startedAt: s.startedAt
  }));
}

/** Clean up: close all sessions and browser. */
export async function cleanup() {
  for (const [id, session] of sessions) {
    try { await session.context.close(); } catch {}
    sessions.delete(id);
  }
  if (browser) {
    try { await browser.close(); } catch {}
    browser = null;
  }
}
