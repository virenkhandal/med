// Scenarios page: generate → chart → record → grade → report.
// Reuses the same MediaRecorder → /api/transcribe flow from oral.js but
// posts the transcript to /api/scenarios/{id}/score instead.

const generateBtn = document.getElementById('generateBtn');
const regenerateBtn = document.getElementById('regenerateBtn');
const categorySel = document.getElementById('category');
const genStatus = document.getElementById('genStatus');

const chartCard = document.getElementById('chartCard');
const chartEl = document.getElementById('chart');
const scenarioTitleEl = document.getElementById('scenarioTitle');
const scenarioCategoryEl = document.getElementById('scenarioCategory');

const recordCard = document.getElementById('recordCard');
const transcriptCard = document.getElementById('transcriptCard');
const transcriptEl = document.getElementById('transcript');
const startRec = document.getElementById('startRec');
const stopRec = document.getElementById('stopRec');
const recStatus = document.getElementById('recStatus');
const reportEl = document.getElementById('report');

let currentScenarioId = null;
let mediaRecorder = null;
let audioChunks = [];
let stream = null;
let elapsedStart = 0;
let elapsedTimer = null;

// ---------- scenario generation ----------

generateBtn.addEventListener('click', () => generateScenario());
regenerateBtn.addEventListener('click', () => generateScenario());

async function generateScenario() {
  const cat = categorySel.value || 'any';
  genStatus.textContent = 'Generating scenario (5–10 seconds)…';
  generateBtn.disabled = true;
  regenerateBtn.disabled = true;
  reportEl.textContent = '';
  transcriptEl.textContent = 'Your recitation will appear here after you stop recording…';
  try {
    const res = await fetch('/api/scenarios/new', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: cat }),
    });
    if (!res.ok) throw new Error(`server ${res.status}`);
    const data = await res.json();
    currentScenarioId = data.scenario_id;
    renderChart(data);
    genStatus.textContent = '';
  } catch (err) {
    genStatus.textContent = `Error: ${err.message}`;
  } finally {
    generateBtn.disabled = false;
    regenerateBtn.disabled = false;
  }
}

function renderChart(data) {
  scenarioTitleEl.textContent = data.title || '(untitled)';
  scenarioCategoryEl.textContent = data.category_label || data.body_system || '';
  chartEl.textContent = '';

  const chart = data.chart || {};
  const fieldOrder = [
    ['chief_complaint', 'Chief Complaint'],
    ['hpi', 'History of Present Illness'],
    ['pmh', 'Past Medical History'],
    ['medications', 'Medications'],
    ['allergies', 'Allergies'],
    ['family_history', 'Family History'],
    ['social_history', 'Social History'],
    ['review_of_systems', 'Review of Systems'],
  ];

  if (chart.vitals && typeof chart.vitals === 'object') {
    const row = document.createElement('div');
    row.className = 'chart-vitals';
    const pairs = [
      ['T', chart.vitals.T],
      ['HR', chart.vitals.HR],
      ['BP', chart.vitals.BP],
      ['RR', chart.vitals.RR],
      ['SpO₂', chart.vitals.SpO2],
    ];
    pairs.forEach(([k, v]) => {
      if (!v) return;
      const chip = document.createElement('div');
      chip.className = 'vital-chip';
      const key = document.createElement('small');
      key.textContent = k;
      const val = document.createElement('strong');
      val.textContent = v;
      chip.appendChild(key);
      chip.appendChild(val);
      row.appendChild(chip);
    });
    if (row.children.length) chartEl.appendChild(row);
  }

  fieldOrder.forEach(([key, label]) => {
    const v = chart[key];
    if (!v) return;
    const wrap = document.createElement('div');
    wrap.className = 'chart-field';
    const h = document.createElement('h5');
    h.textContent = label;
    const p = document.createElement('p');
    p.textContent = v;
    wrap.appendChild(h);
    wrap.appendChild(p);
    chartEl.appendChild(wrap);
  });

  chartCard.style.display = '';
  recordCard.style.display = '';
  transcriptCard.style.display = '';
  chartCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ---------- recording (clone of oral.js) ----------

const isSecure = window.isSecureContext;

if (!navigator.mediaDevices || !window.MediaRecorder) {
  if (!isSecure) {
    const httpsUrl = 'https://med.67-205-142-127.nip.io' + window.location.pathname;
    recStatus.textContent = '';
    const msg = document.createElement('span');
    msg.textContent = 'Microphone access requires HTTPS. Open ';
    const link = document.createElement('a');
    link.href = httpsUrl;
    link.textContent = httpsUrl;
    link.style.color = 'var(--accent-strong)';
    link.style.textDecoration = 'underline';
    const tail = document.createElement('span');
    tail.textContent = ' instead.';
    recStatus.appendChild(msg);
    recStatus.appendChild(link);
    recStatus.appendChild(tail);
  } else {
    recStatus.textContent = 'Browser does not support audio recording. Use Chrome, Firefox, Edge, or Safari 14+.';
  }
  startRec.disabled = true;
}

function pickMimeType() {
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/mp4',
  ];
  for (const t of candidates) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(t)) return t;
  }
  return '';
}

function formatElapsed(ms) {
  const s = Math.floor(ms / 1000);
  const mm = String(Math.floor(s / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

startRec.addEventListener('click', async () => {
  if (!currentScenarioId) {
    recStatus.textContent = 'Generate a scenario first.';
    return;
  }
  transcriptEl.textContent = 'Recording…';
  reportEl.textContent = '';
  audioChunks = [];
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (e) {
    recStatus.textContent = `Microphone access denied: ${e.message}`;
    return;
  }
  const mimeType = pickMimeType();
  try {
    mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
  } catch (e) {
    recStatus.textContent = `Could not start recorder: ${e.message}`;
    stream.getTracks().forEach(t => t.stop());
    return;
  }
  mediaRecorder.ondataavailable = (e) => { if (e.data && e.data.size > 0) audioChunks.push(e.data); };
  mediaRecorder.onerror = (e) => { recStatus.textContent = `Recorder error: ${e.error?.name || 'unknown'}`; };
  mediaRecorder.onstop = handleStop;
  mediaRecorder.start(1000);

  startRec.disabled = true;
  stopRec.disabled = false;
  elapsedStart = Date.now();
  elapsedTimer = setInterval(() => {
    recStatus.textContent = `● Recording ${formatElapsed(Date.now() - elapsedStart)}`;
  }, 500);
});

stopRec.addEventListener('click', () => {
  if (!mediaRecorder) return;
  if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null; }
  recStatus.textContent = 'Finalizing recording…';
  try { mediaRecorder.stop(); } catch (_) { /* ignore */ }
});

async function handleStop() {
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
  const mimeType = (mediaRecorder && mediaRecorder.mimeType) || 'audio/webm';
  const blob = new Blob(audioChunks, { type: mimeType });
  audioChunks = [];
  mediaRecorder = null;

  const sizeMb = (blob.size / (1024 * 1024)).toFixed(2);
  recStatus.textContent = `Transcribing ${sizeMb} MB (this may take up to a minute)…`;
  transcriptEl.textContent = 'Transcribing…';

  try {
    const fd = new FormData();
    const ext = mimeType.includes('mp4') ? 'm4a' : (mimeType.includes('ogg') ? 'ogg' : 'webm');
    fd.append('audio', blob, `recording.${ext}`);
    const tResp = await fetch('/api/transcribe', { method: 'POST', body: fd });
    if (!tResp.ok) {
      const txt = await tResp.text();
      throw new Error(`transcribe ${tResp.status}: ${txt.slice(0, 200)}`);
    }
    const tData = await tResp.json();
    transcriptEl.textContent = tData.text || '(no speech detected)';

    recStatus.textContent = 'Grading…';
    const sResp = await fetch(`/api/scenarios/${currentScenarioId}/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript: tData.text || '' }),
    });
    if (!sResp.ok) throw new Error(`score ${sResp.status}`);
    const sData = await sResp.json();
    renderReport(sData, tData);
    const passing = sData.passing ? 'PASS' : 'FAIL (<70% or critical miss)';
    recStatus.textContent = `Done — ${sData.score_pct}% (${passing})`;
  } catch (err) {
    recStatus.textContent = `Error: ${err.message}`;
    transcriptEl.textContent = '';
  } finally {
    startRec.disabled = false;
    stopRec.disabled = true;
  }
}

// ---------- report rendering ----------

function gaugeClass(pct) {
  if (pct >= 75) return 'good';
  if (pct >= 40) return 'warn';
  return 'poor';
}

function renderReport(data, tData) {
  reportEl.textContent = '';

  // Pass/Fail banner
  const banner = document.createElement('div');
  banner.className = 'pass-banner ' + (data.passing ? 'passing' : 'failing');
  const bannerIcon = document.createElement('span');
  bannerIcon.className = 'pass-icon';
  bannerIcon.textContent = data.passing ? '✓' : '✗';
  const bannerText = document.createElement('div');
  const bannerTitle = document.createElement('strong');
  bannerTitle.textContent = data.passing
    ? `PASS — ${data.score_pct}%`
    : `NEEDS REMEDIATION — ${data.score_pct}%`;
  const bannerSub = document.createElement('small');
  if (data.critical_missed && data.critical_missed.length) {
    bannerSub.textContent = `Missed ${data.critical_missed.length} critical item(s). Passing threshold: ${data.passing_threshold}%.`;
  } else {
    bannerSub.textContent = `Passing threshold: ${data.passing_threshold}%.`;
  }
  bannerText.appendChild(bannerTitle);
  bannerText.appendChild(document.createElement('br'));
  bannerText.appendChild(bannerSub);
  banner.appendChild(bannerIcon);
  banner.appendChild(bannerText);
  reportEl.appendChild(banner);

  // Grader badge
  const graderBadge = document.createElement('div');
  graderBadge.className = 'grader-badge';
  const dot = document.createElement('span');
  dot.className = 'dot dot-llm';
  graderBadge.appendChild(dot);
  const label = document.createElement('span');
  label.textContent = `Graded by ${data.model || 'Claude'} — scenario-specific rubric`;
  graderBadge.appendChild(label);
  reportEl.appendChild(graderBadge);

  // Critical missed highlight
  if (data.critical_missed && data.critical_missed.length) {
    const cm = document.createElement('div');
    cm.className = 'critical-missed';
    const h = document.createElement('h4');
    h.textContent = 'Critical items missed';
    cm.appendChild(h);
    const ul = document.createElement('ul');
    data.critical_missed.forEach(m => {
      const li = document.createElement('li');
      li.textContent = `${m.section}: ${m.item}`;
      ul.appendChild(li);
    });
    cm.appendChild(ul);
    reportEl.appendChild(cm);
  }

  // Stats
  const header = document.createElement('div');
  header.className = 'report-header';
  const stats = [
    { value: `${data.score_pct}%`, label: 'coverage' },
    { value: `${data.covered_items}/${data.total_items}`, label: 'rubric items' },
    { value: `${data.word_count}`, label: 'words spoken' },
    { value: tData && tData.duration ? `${Math.round(tData.duration)}s` : '—', label: 'audio duration' },
  ];
  stats.forEach(s => {
    const card = document.createElement('div');
    card.className = 'stat-card';
    const v = document.createElement('span');
    v.className = 'value';
    v.textContent = s.value;
    const l = document.createElement('span');
    l.className = 'label';
    l.textContent = s.label;
    card.appendChild(v);
    card.appendChild(l);
    header.appendChild(card);
  });
  reportEl.appendChild(header);

  // Per-section report
  const secReport = document.createElement('div');
  secReport.className = 'sections-report';
  const h = document.createElement('h3');
  h.textContent = 'Per-section breakdown';
  secReport.appendChild(h);

  const sortedSections = [...data.sections].sort((a, b) => a.score_pct - b.score_pct);
  sortedSections.forEach(sec => {
    const row = document.createElement('div');
    row.className = 'section-row';

    const hdr = document.createElement('div');
    hdr.className = 'section-row-header';
    const name = document.createElement('span');
    name.className = 'name';
    name.textContent = `${sec.name} (${sec.covered}/${sec.total})`;
    const pct = document.createElement('span');
    pct.className = 'pct';
    pct.textContent = `${sec.score_pct}%`;
    hdr.appendChild(name);
    hdr.appendChild(pct);
    row.appendChild(hdr);

    const gauge = document.createElement('div');
    gauge.className = 'gauge';
    const fill = document.createElement('div');
    fill.className = `gauge-fill ${gaugeClass(sec.score_pct)}`;
    fill.style.width = `${Math.max(2, sec.score_pct)}%`;
    gauge.appendChild(fill);
    row.appendChild(gauge);

    const details = document.createElement('details');
    details.className = 'section-details';
    details.open = true;
    const summary = document.createElement('summary');
    summary.textContent = 'Items';
    details.appendChild(summary);

    sec.subsections.forEach(sub => {
      const block = document.createElement('div');
      block.className = 'sub-report';
      const ul = document.createElement('ul');
      sub.items.forEach(item => {
        const li = document.createElement('li');
        li.className = item.covered ? 'hit' : 'miss';
        if (item.critical) li.classList.add('critical');
        const txt = document.createElement('span');
        txt.textContent = item.item;
        li.appendChild(txt);
        if (item.critical) {
          const tag = document.createElement('span');
          tag.className = 'crit-tag';
          tag.textContent = ' CRITICAL';
          li.appendChild(tag);
        }
        if (item.reason) {
          const rsn = document.createElement('span');
          rsn.className = 'item-reason';
          rsn.textContent = ' — ' + item.reason;
          li.appendChild(rsn);
        }
        ul.appendChild(li);
      });
      block.appendChild(ul);
      details.appendChild(block);
    });
    row.appendChild(details);
    secReport.appendChild(row);
  });

  reportEl.appendChild(secReport);
  reportEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
