/* ─── CSRF helper ─── */
function getCookie(name) {
  const v = document.cookie.split(';').map(c => c.trim());
  for (const c of v) {
    if (c.startsWith(name + '=')) return decodeURIComponent(c.slice(name.length + 1));
  }
  return null;
}

/* ─── State ─── */
let currentDirection = 'pt_to_sd';
let debounceTimer   = null;
const DEBOUNCE_MS   = 400;

/* ─── DOM refs ─── */
const inputText       = document.getElementById('input-text');
const outputText      = document.getElementById('output-text');
const translateBtn    = document.getElementById('translate-btn');
const clearBtn        = document.getElementById('clear-btn');
const copyBtn         = document.getElementById('copy-btn');
const swapBtn         = document.getElementById('swap-btn');
const btnPtSd         = document.getElementById('btn-pt-sd');
const btnSdPt         = document.getElementById('btn-sd-pt');
const inputLangLabel  = document.getElementById('input-lang-label');
const outputLangLabel = document.getElementById('output-lang-label');
const charCount       = document.getElementById('char-count');
const wordInfo        = document.getElementById('word-info');
const copyFeedback    = document.getElementById('copy-feedback');
const loadingOverlay  = document.getElementById('loading-overlay');

/* ─── Translate ─── */
async function translate() {
  const text = inputText.value.trim();
  if (!text) {
    setOutput('');
    wordInfo.textContent = '';
    return;
  }

  setLoading(true);

  try {
    const res = await fetch('/translate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ text, direction: currentDirection }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    setOutput(data.result || '');
    updateWordInfo(text, data.result || '');
  } catch (err) {
    setOutput('');
    console.error('Translation error:', err);
  } finally {
    setLoading(false);
  }
}

function setOutput(text) {
  if (!text) {
    outputText.innerHTML = '<span class="output-placeholder">A tradução aparecerá aqui...</span>';
    return;
  }
  // Highlight unknown words (wrapped in [ ])
  const highlighted = text.replace(
    /\[([^\]]+)\]/g,
    '<span class="unknown-word">[$1]</span>'
  );
  outputText.innerHTML = `<span class="output-result">${highlighted}</span>`;
}

function updateWordInfo(input, output) {
  if (!output) { wordInfo.textContent = ''; return; }
  const inputWords  = input.trim().split(/\s+/).length;
  const outputWords = output.trim().split(/\s+/).length;
  const unknown     = (output.match(/\[[^\]]+\]/g) || []).length;
  const parts = [`${inputWords} palavra${inputWords !== 1 ? 's' : ''}`];
  if (unknown > 0) parts.push(`${unknown} desconhecida${unknown !== 1 ? 's' : ''}`);
  wordInfo.textContent = parts.join(' · ');
}

function setLoading(active) {
  loadingOverlay.classList.toggle('active', active);
  translateBtn.classList.toggle('loading', active);
  loadingOverlay.setAttribute('aria-hidden', String(!active));
}

/* ─── Direction ─── */
function setDirection(dir) {
  currentDirection = dir;
  const isPtSd = dir === 'pt_to_sd';

  btnPtSd.classList.toggle('active', isPtSd);
  btnSdPt.classList.toggle('active', !isPtSd);
  btnPtSd.setAttribute('aria-pressed', String(isPtSd));
  btnSdPt.setAttribute('aria-pressed', String(!isPtSd));

  inputLangLabel.textContent  = isPtSd ? 'Português' : 'Sindarin';
  outputLangLabel.textContent = isPtSd ? 'Sindarin' : 'Português';
  inputText.placeholder = isPtSd
    ? 'Digite sua frase aqui...'
    : 'Havo dad, Legolas...';

  if (inputText.value.trim()) translate();
}

function swapLanguages() {
  const oldInput  = inputText.value;
  const oldOutput = outputText.querySelector('.output-result')?.textContent || '';

  swapBtn.classList.add('swapping');
  setTimeout(() => swapBtn.classList.remove('swapping'), 300);

  setDirection(currentDirection === 'pt_to_sd' ? 'sd_to_pt' : 'pt_to_sd');

  if (oldOutput) {
    inputText.value = oldOutput;
    updateCharCount();
    translate();
  }
}

/* ─── Char Count ─── */
function updateCharCount() {
  const len  = inputText.value.length;
  const max  = parseInt(inputText.getAttribute('maxlength'), 10) || 2000;
  charCount.textContent = `${len} / ${max}`;
  charCount.classList.toggle('near-limit', len > max * 0.8);
}

/* ─── Copy ─── */
async function copyResult() {
  const text = outputText.querySelector('.output-result')?.textContent || '';
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    copyFeedback.classList.add('visible');
    setTimeout(() => copyFeedback.classList.remove('visible'), 1800);
  } catch {
    /* clipboard unavailable */
  }
}

/* ─── Examples ─── */
document.querySelectorAll('.example-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const text = chip.dataset.text;
    const dir  = chip.dataset.dir;

    if (dir !== currentDirection) setDirection(dir);

    inputText.value = text;
    updateCharCount();
    translate();
    inputText.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
});

/* ─── Event Listeners ─── */
inputText.addEventListener('input', () => {
  updateCharCount();
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(translate, DEBOUNCE_MS);
});

inputText.addEventListener('keydown', e => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    clearTimeout(debounceTimer);
    translate();
  }
});

translateBtn.addEventListener('click', () => {
  clearTimeout(debounceTimer);
  translate();
});

clearBtn.addEventListener('click', () => {
  inputText.value = '';
  updateCharCount();
  setOutput('');
  wordInfo.textContent = '';
  inputText.focus();
});

copyBtn.addEventListener('click', copyResult);

swapBtn.addEventListener('click', swapLanguages);

btnPtSd.addEventListener('click', () => setDirection('pt_to_sd'));
btnSdPt.addEventListener('click', () => setDirection('sd_to_pt'));

/* ─── Init ─── */
updateCharCount();
