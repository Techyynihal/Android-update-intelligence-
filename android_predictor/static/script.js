/* ═══════════════════════════════════════════════════════════════
   DroidSense AI — Frontend JavaScript
   Handles: API calls, animations, dynamic UI, mock fallback
   ═══════════════════════════════════════════════════════════════ */

'use strict';

// ─── State ────────────────────────────────────────────────────────
let brandsData = {};
let currentPrediction = null;

// ─── DOM References ───────────────────────────────────────────────
const brandSelect  = document.getElementById('brand-select');
const modelSelect  = document.getElementById('model-select');
const androidSel   = document.getElementById('android-select');
const uiInput      = document.getElementById('ui-input');
const uiHint       = document.getElementById('ui-hint');
const predictBtn   = document.getElementById('predict-btn');
const resetBtn     = document.getElementById('reset-btn');
const skeleton     = document.getElementById('skeleton');
const results      = document.getElementById('results');
const errorToast   = document.getElementById('error-toast');
const toastMsg     = document.getElementById('toast-msg');

// ─── Mock Fallback Data ───────────────────────────────────────────
const MOCK_PREDICTIONS = {
  "Samsung": {
    next_android: "Android 15",
    next_ui: "One UI 7.0",
    features: ["Galaxy AI Suite", "Now Bar Live Activities", "Cross-App Actions", "AI Photo Remaster", "Sketch to Image", "RAM optimization"],
    security_patch: "Monthly — Next patch: June 2025",
    eta: "2–3 months (Q3 2025)",
    confidence: 87,
    likelihood: "High",
    history: ["One UI 4.0 (Android 12)", "One UI 5.0 (Android 13)", "One UI 6.0 (Android 14)"]
  },
  "Google": {
    next_android: "Android 15",
    next_ui: "Stock Android 15",
    features: ["Gemini Nano integration", "Circle to Search 2.0", "Live transcription", "AI Photo unblur", "Adaptive charging", "Satellite SOS"],
    security_patch: "Monthly — Next patch: June 2025",
    eta: "~1 month (Q2 2025)",
    confidence: 95,
    likelihood: "High",
    history: ["Android 12", "Android 13", "Android 14"]
  },
  "default": {
    next_android: "Android 15",
    next_ui: "Next UI Version",
    features: ["AI assistant integration", "Privacy dashboard upgrade", "Improved RAM management", "Smoother animations", "Enhanced camera algorithms", "New gesture nav"],
    security_patch: "Monthly — Next patch: June 2025",
    eta: "4–5 months (Q3 2025)",
    confidence: 72,
    likelihood: "Medium",
    history: ["Android 12", "Android 13", "Android 14"]
  }
};

// ─── SVG Gradient for Gauge ───────────────────────────────────────
function injectGaugeDefs() {
  const svgDefs = document.createElementNS("http://www.w3.org/2000/svg","defs");
  svgDefs.innerHTML = `
    <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#7b2ff7"/>
      <stop offset="100%" stop-color="#00d4ff"/>
    </linearGradient>`;
  const gauge = document.querySelector('.radial-gauge');
  if (gauge) gauge.prepend(svgDefs);
}

// ─── Init: Load Brands ────────────────────────────────────────────
async function loadBrands() {
  try {
    const res = await fetch('/brands');
    if (!res.ok) throw new Error('Failed');
    brandsData = await res.json();
  } catch {
    brandsData = buildMockBrandsData();
  }
  populateBrandDropdown();
}

function buildMockBrandsData() {
  const brands = {
    "Samsung": { ui: "One UI", models: ["Galaxy S24 Ultra","Galaxy S24+","Galaxy S24","Galaxy S23 Ultra","Galaxy S23","Galaxy S22","Galaxy A55","Galaxy A54","Galaxy A34","Galaxy Z Fold 5","Galaxy Z Flip 5"], history: ["One UI 4.0 (Android 12)","One UI 5.0 (Android 13)","One UI 6.0 (Android 14)"] },
    "Google": { ui: "Stock Android", models: ["Pixel 9 Pro","Pixel 9","Pixel 8 Pro","Pixel 8","Pixel 8a","Pixel 7 Pro","Pixel 7","Pixel 7a","Pixel 6 Pro","Pixel 6","Pixel Fold"], history: ["Android 12","Android 13","Android 14"] },
    "OnePlus": { ui: "OxygenOS", models: ["OnePlus 12","OnePlus 12R","OnePlus 11","OnePlus Nord 4","OnePlus Nord CE 4","OnePlus Nord 3","OnePlus Open"], history: ["OxygenOS 12 (Android 12)","OxygenOS 13 (Android 13)","OxygenOS 14 (Android 14)"] },
    "Xiaomi": { ui: "HyperOS", models: ["Xiaomi 14 Ultra","Xiaomi 14 Pro","Xiaomi 14","Xiaomi 13T Pro","Xiaomi 13T","Xiaomi 13","Xiaomi Mix Fold 3"], history: ["MIUI 13 (Android 12)","HyperOS 1.0 (Android 13)","HyperOS 2.0 (Android 14)"] },
    "Redmi": { ui: "HyperOS", models: ["Redmi Note 13 Pro+","Redmi Note 13 Pro","Redmi Note 13","Redmi Note 12 Pro","Redmi Note 12","Redmi K70 Pro","Redmi A3"], history: ["MIUI 13 (Android 12)","HyperOS 1.0 (Android 13)","HyperOS 2.0 (Android 14)"] },
    "POCO": { ui: "HyperOS", models: ["POCO F6 Pro","POCO F6","POCO F5 Pro","POCO F5","POCO X6 Pro","POCO X6","POCO X5 Pro","POCO M6 Pro"], history: ["MIUI 13 (Android 12)","HyperOS 1.0 (Android 13)","HyperOS 2.0 (Android 14)"] },
    "Realme": { ui: "Realme UI", models: ["Realme GT 6","Realme GT 5 Pro","Realme GT Neo 6","Realme 12 Pro+","Realme 12 Pro","Realme 11 Pro+","Realme Narzo 70 Pro"], history: ["Realme UI 3.0 (Android 12)","Realme UI 4.0 (Android 13)","Realme UI 5.0 (Android 14)"] },
    "iQOO": { ui: "FuntouchOS", models: ["iQOO 13","iQOO 12 Pro","iQOO 12","iQOO 11 Pro","iQOO Neo 9 Pro","iQOO Neo 9","iQOO Z9 Turbo","iQOO Z9 Pro","iQOO Z9"], history: ["FuntouchOS 12","FuntouchOS 13","FuntouchOS 14"] },
    "Vivo": { ui: "FuntouchOS", models: ["Vivo X100 Ultra","Vivo X100 Pro","Vivo X100","Vivo X Fold 3 Pro","Vivo V40 Pro","Vivo V40","Vivo V30 Pro","Vivo Y200 Pro","Vivo Y200","Vivo Y100","Vivo T3 Pro","Vivo T3x"], history: ["FuntouchOS 12 (Android 12)","FuntouchOS 13 (Android 13)","FuntouchOS 14 (Android 14)"] },
    "OPPO": { ui: "ColorOS", models: ["OPPO Find X8 Ultra","OPPO Find X8 Pro","OPPO Find X8","OPPO Find X7 Ultra","OPPO Find N3 Flip","OPPO Reno 12 Pro","OPPO Reno 12","OPPO Reno 11 Pro","OPPO A3 Pro"], history: ["ColorOS 12 (Android 12)","ColorOS 13 (Android 13)","ColorOS 14 (Android 14)"] },
    "Huawei": { ui: "HarmonyOS", models: ["Huawei Mate 60 Pro+","Huawei Mate 60 Pro","Huawei Mate X5","Huawei P60 Pro","Huawei Nova 12 Ultra","Huawei Pura 70 Ultra","Huawei Pura 70 Pro+"], history: ["HarmonyOS 3.0","HarmonyOS 3.1","HarmonyOS 4.0"] },
    "Honor": { ui: "MagicOS", models: ["Honor Magic 6 Pro","Honor Magic 6","Honor Magic V3","Honor 200 Pro","Honor 200","Honor 90 Pro","Honor 90","Honor X9b"], history: ["MagicOS 7.0 (Android 13)","MagicOS 7.1","MagicOS 8.0 (Android 14)"] },
    "Motorola": { ui: "Hello UI", models: ["Motorola Edge 50 Ultra","Motorola Edge 50 Pro","Motorola Edge 50","Motorola Razr 50 Ultra","Motorola Razr 50","Moto G85","Moto G84","Moto G54 5G"], history: ["Android 12","Android 13","Android 14"] },
    "Nothing": { ui: "Nothing OS", models: ["Nothing Phone 2a Plus","Nothing Phone 2a","Nothing Phone 2","Nothing Phone 1","Nothing CMF Phone 1"], history: ["Nothing OS 1.5 (Android 12)","Nothing OS 2.0 (Android 13)","Nothing OS 2.5 (Android 14)"] },
    "Tecno": { ui: "HiOS", models: ["Tecno Phantom V Fold 2","Tecno Phantom V Fold","Tecno Camon 30 Premier","Tecno Camon 30 Pro 5G","Tecno Spark 20 Pro+","Tecno Pova 6 Pro"], history: ["HiOS 12 (Android 12)","HiOS 13 (Android 13)","HiOS 14 (Android 14)"] },
    "Infinix": { ui: "XOS", models: ["Infinix Zero 40","Infinix Zero 30 5G","Infinix Note 40 Pro+","Infinix Note 40 Pro","Infinix Hot 40 Pro","Infinix Hot 40"], history: ["XOS 12 (Android 12)","XOS 13 (Android 13)","XOS 14 (Android 14)"] },
    "Sharp": { ui: "Stock-based UI", models: ["Sharp Aquos R9 Pro","Sharp Aquos R9","Sharp Aquos R8 Pro","Sharp Aquos R8","Sharp Aquos Sense 9","Sharp Aquos Sense 8"], history: ["Android 12","Android 13","Android 14"] }
  };
  return brands;
}

function populateBrandDropdown() {
  brandSelect.innerHTML = '<option value="">— Select Brand —</option>';
  const sorted = Object.keys(brandsData).sort();
  sorted.forEach(brand => {
    const opt = document.createElement('option');
    opt.value = brand;
    opt.textContent = brand;
    brandSelect.appendChild(opt);
  });
}

// ─── Brand Change Handler ─────────────────────────────────────────
brandSelect.addEventListener('change', () => {
  const brand = brandSelect.value;
  modelSelect.innerHTML = '<option value="">— Select Model —</option>';
  modelSelect.disabled = true;
  uiInput.value = '';
  uiHint.textContent = '';
  predictBtn.disabled = true;

  if (!brand) return;

  const info = brandsData[brand];
  if (!info) return;

  const models = info.models || [];
  models.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m;
    opt.textContent = m;
    modelSelect.appendChild(opt);
  });
  modelSelect.disabled = false;

  // Set UI hint
  uiHint.textContent = `💡 e.g. "${info.ui}"`;
  uiInput.placeholder = `e.g. ${info.ui} (latest)`;
});

// ─── Model Change Handler ─────────────────────────────────────────
modelSelect.addEventListener('change', () => {
  predictBtn.disabled = !modelSelect.value;
});

// ─── Predict Button ───────────────────────────────────────────────
predictBtn.addEventListener('click', async () => {
  const brand = brandSelect.value;
  const model = modelSelect.value;
  const androidVer = androidSel.value;
  const uiVer = uiInput.value.trim() || brandsData[brand]?.ui || '';

  if (!brand || !model) {
    showToast('Please select a brand and model first.');
    return;
  }

  await runPrediction(brand, model, androidVer, uiVer);
});

// ─── Reset ────────────────────────────────────────────────────────
resetBtn.addEventListener('click', () => {
  brandSelect.value = '';
  modelSelect.innerHTML = '<option value="">— Select Model —</option>';
  modelSelect.disabled = true;
  androidSel.value = '14';
  uiInput.value = '';
  uiHint.textContent = '';
  predictBtn.disabled = true;

  results.style.display = 'none';
  results.style.opacity = '0';
  skeleton.style.display = 'none';
});

// ─── Core Prediction Flow ─────────────────────────────────────────
async function runPrediction(brand, model, androidVer, uiVer) {
  showSkeleton();
  predictBtn.classList.add('loading');
  predictBtn.disabled = true;

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        brand, model,
        android_version: androidVer,
        ui_version: uiVer
      })
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    data.brand = brand;
    data.model = model;
    renderResults(data, androidVer);

  } catch (err) {
    console.warn('[Prediction Error]', err.message, '— Using mock data');
    const mock = MOCK_PREDICTIONS[brand] || MOCK_PREDICTIONS['default'];
    mock.brand = brand;
    mock.model = model;
    renderResults(mock, androidVer);
  } finally {
    hideSkeleton();
    predictBtn.classList.remove('loading');
    predictBtn.disabled = false;
  }
}

// ─── Render Results ───────────────────────────────────────────────
function renderResults(data, currentAndroid) {
  currentPrediction = data;

  // Device identity
  document.getElementById('result-brand-initial').textContent = data.brand[0].toUpperCase();
  document.getElementById('result-device-name').textContent = `${data.brand} ${data.model}`;
  document.getElementById('result-android-current').textContent = `Running Android ${currentAndroid}`;

  // Prediction values
  document.getElementById('next-android').textContent = data.next_android || '—';
  document.getElementById('next-ui').textContent = data.next_ui || '—';
  document.getElementById('eta-val').textContent = data.eta || '—';
  document.getElementById('security-val').textContent = data.security_patch || '—';

  // Confidence
  animateConfidence(data.confidence || 0);

  // Likelihood
  renderLikelihood(data.likelihood || 'Medium');

  // Features
  renderFeatures(data.features || []);

  // Timeline
  renderTimeline(data.history || [], data.next_android, data.next_ui);

  // Show results
  results.style.display = 'flex';
  results.style.flexDirection = 'column';
  results.style.gap = '24px';

  requestAnimationFrame(() => {
    results.style.opacity = '1';
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

// ─── Confidence Animation ─────────────────────────────────────────
function animateConfidence(targetVal) {
  const circle = document.getElementById('gauge-circle');
  const gaugeText = document.getElementById('gauge-text');
  const confBar = document.getElementById('conf-bar');
  const confPct = document.getElementById('conf-pct');

  const circumference = 2 * Math.PI * 60; // r=60 → 377
  const targetOffset = circumference - (targetVal / 100) * circumference;

  // Reset first
  circle.style.strokeDashoffset = circumference;
  confBar.style.width = '0%';
  gaugeText.textContent = '0%';

  setTimeout(() => {
    circle.style.strokeDashoffset = targetOffset;
    confBar.style.width = `${targetVal}%`;

    // Animate counter
    let current = 0;
    const step = targetVal / 60;
    const timer = setInterval(() => {
      current = Math.min(current + step, targetVal);
      const rounded = Math.round(current);
      gaugeText.textContent = `${rounded}%`;
      confPct.textContent = `${rounded}%`;
      if (current >= targetVal) clearInterval(timer);
    }, 25);
  }, 200);
}

// ─── Likelihood Render ────────────────────────────────────────────
function renderLikelihood(level) {
  const ring = document.getElementById('likelihood-ring');
  const label = document.getElementById('likelihood-label');
  const dotsWrap = document.getElementById('likelihood-dots');
  const desc = document.getElementById('likelihood-desc');

  ring.className = 'likelihood-ring ' + level.toLowerCase();
  label.textContent = level;

  const dots = dotsWrap.querySelectorAll('.ldot');
  const descMap = {
    'High': 'Strong update history & manufacturer commitment',
    'Medium': 'Moderate update cadence — likely but not guaranteed',
    'Low': 'Limited update history — update may not arrive'
  };

  const dotCounts = { 'High': 3, 'Medium': 2, 'Low': 1 };
  const dotClass = { 'High': '', 'Medium': 'med', 'Low': 'low-c' };
  const count = dotCounts[level] || 2;

  dots.forEach((d, i) => {
    d.className = 'ldot';
    if (i < count) {
      d.classList.add('active');
      if (dotClass[level]) d.classList.add(dotClass[level]);
    }
  });

  desc.textContent = descMap[level] || '';
}

// ─── Features Render ──────────────────────────────────────────────
function renderFeatures(features) {
  const grid = document.getElementById('features-grid');
  grid.innerHTML = '';

  features.forEach((feat, i) => {
    const chip = document.createElement('div');
    chip.className = 'feature-chip';
    chip.style.animationDelay = `${i * 0.07}s`;
    chip.textContent = feat;
    grid.appendChild(chip);
  });
}

// ─── Timeline Render ──────────────────────────────────────────────
function renderTimeline(history, nextAndroid, nextUI) {
  const hist2 = document.getElementById('hist-2');
  const hist1 = document.getElementById('hist-1');
  const hist0 = document.getElementById('hist-0');
  const timelineNext = document.getElementById('timeline-next');

  hist2.textContent = history[0] || '—';
  hist1.textContent = history[1] || '—';
  hist0.textContent = history[2] || '—';
  timelineNext.textContent = `${nextAndroid}`;
}

// ─── Skeleton Loader ──────────────────────────────────────────────
function showSkeleton() {
  results.style.display = 'none';
  skeleton.style.display = 'grid';
}

function hideSkeleton() {
  skeleton.style.display = 'none';
}

// ─── Toast ────────────────────────────────────────────────────────
function showToast(msg, duration = 3500) {
  toastMsg.textContent = msg;
  errorToast.classList.add('show');
  setTimeout(() => errorToast.classList.remove('show'), duration);
}

// ─── Keyboard Enter shortcut ──────────────────────────────────────
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !predictBtn.disabled) {
    predictBtn.click();
  }
});

// ─── Boot ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  injectGaugeDefs();
  loadBrands();
});
