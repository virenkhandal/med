const startRec = document.getElementById('startRec');
const stopRec = document.getElementById('stopRec');
const recStatus = document.getElementById('recStatus');
const transcriptEl = document.getElementById('transcript');
const reportEl = document.getElementById('report');

const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

let recognition = null;
let finalTranscript = '';
let interimTranscript = '';
let shouldKeepAlive = false;
let elapsedStart = 0;
let elapsedTimer = null;

if (!SR) {
  recStatus.textContent = 'Speech recognition not supported in this browser. Use Chrome, Edge, or Safari.';
  startRec.disabled = true;
}

function buildRecognition() {
  const rec = new SR();
  rec.continuous = true;
  rec.interimResults = true;
  rec.lang = 'en-US';
  rec.onresult = (event) => {
    interimTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const res = event.results[i];
      if (res.isFinal) {
        finalTranscript += res[0].transcript + ' ';
      } else {
        interimTranscript += res[0].transcript;
      }
    }
    renderTranscript();
  };
  rec.onend = () => {
    if (shouldKeepAlive) {
      try { rec.start(); } catch (_) { /* ignore restart race */ }
    }
  };
  rec.onerror = (e) => {
    if (e.error === 'no-speech' || e.error === 'aborted') return;
    recStatus.textContent = `Recognition error: ${e.error}`;
  };
  return rec;
}

function renderTranscript() {
  transcriptEl.textContent = '';
  const finalNode = document.createTextNode(finalTranscript);
  transcriptEl.appendChild(finalNode);
  if (interimTranscript) {
    const span = document.createElement('span');
    span.className = 'interim';
    span.textContent = interimTranscript;
    transcriptEl.appendChild(span);
  }
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

function formatElapsed(ms) {
  const s = Math.floor(ms / 1000);
  const mm = String(Math.floor(s / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

startRec.addEventListener('click', () => {
  finalTranscript = '';
  interimTranscript = '';
  renderTranscript();
  reportEl.textContent = '';
  shouldKeepAlive = true;
  recognition = buildRecognition();
  try {
    recognition.start();
  } catch (e) {
    recStatus.textContent = `Could not start: ${e.message}`;
    return;
  }
  startRec.disabled = true;
  stopRec.disabled = false;
  elapsedStart = Date.now();
  elapsedTimer = setInterval(() => {
    recStatus.textContent = `Recording… ${formatElapsed(Date.now() - elapsedStart)}`;
  }, 500);
});

stopRec.addEventListener('click', async () => {
  shouldKeepAlive = false;
  if (recognition) {
    try { recognition.stop(); } catch (_) { /* ignore */ }
  }
  if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null; }
  startRec.disabled = false;
  stopRec.disabled = true;
  recStatus.textContent = 'Scoring…';
  try {
    const res = await fetch(`/api/exam/${window.EXAM_SLUG}/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript: finalTranscript.trim() }),
    });
    if (!res.ok) throw new Error(`Server ${res.status}`);
    const data = await res.json();
    renderReport(data);
    recStatus.textContent = `Done — ${data.covered_items}/${data.total_items} items covered (${data.score_pct}%)`;
  } catch (err) {
    recStatus.textContent = `Error: ${err.message}`;
  }
});

function renderReport(data) {
  reportEl.textContent = '';

  const header = document.createElement('div');
  header.className = 'report-header';
  const stats = [
    { value: `${data.score_pct}%`, label: 'coverage' },
    { value: `${data.covered_items}/${data.total_items}`, label: 'items hit' },
    { value: `${data.word_count}`, label: 'words spoken' },
  ];
  stats.forEach(s => {
    const d = document.createElement('div');
    d.className = 'stat';
    const strong = document.createElement('strong');
    strong.textContent = s.value;
    const small = document.createElement('small');
    small.textContent = s.label;
    d.appendChild(strong);
    d.appendChild(small);
    header.appendChild(d);
  });
  reportEl.appendChild(header);

  const h = document.createElement('h3');
  h.textContent = 'Per-item breakdown';
  h.style.marginTop = '20px';
  reportEl.appendChild(h);

  const hitList = document.createElement('ol');
  hitList.className = 'hit-list missed-list';
  data.results.forEach(r => {
    const li = document.createElement('li');
    li.className = r.covered ? 'hit' : 'miss';
    const mark = r.covered ? '✓' : '✗';
    li.textContent = `${mark} ${r.item}`;
    hitList.appendChild(li);
  });
  reportEl.appendChild(hitList);

  reportEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
