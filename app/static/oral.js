const startRec = document.getElementById('startRec');
const stopRec = document.getElementById('stopRec');
const recStatus = document.getElementById('recStatus');
const transcriptEl = document.getElementById('transcript');
const reportEl = document.getElementById('report');
const checklistEl = document.getElementById('checklist');
const toggleChecklistBtn = document.getElementById('toggleChecklist');
const toggleLabel = toggleChecklistBtn ? toggleChecklistBtn.querySelector('.toggle-label') : null;
const checklistPanel = toggleChecklistBtn ? toggleChecklistBtn.closest('.checklist-panel') : null;

if (toggleChecklistBtn && checklistEl) {
  toggleChecklistBtn.addEventListener('click', () => {
    const hidden = checklistEl.classList.toggle('checklist-hidden');
    const revealed = !hidden;
    toggleChecklistBtn.setAttribute('aria-pressed', revealed ? 'true' : 'false');
    toggleChecklistBtn.setAttribute('aria-label', revealed ? 'Hide checklist' : 'Reveal checklist');
    if (toggleLabel) toggleLabel.textContent = revealed ? 'Hide' : 'Reveal';
    if (checklistPanel) checklistPanel.classList.toggle('revealed', revealed);
  });
}

let mediaRecorder = null;
let audioChunks = [];
let stream = null;
let elapsedStart = 0;
let elapsedTimer = null;

function formatElapsed(ms) {
  const s = Math.floor(ms / 1000);
  const mm = String(Math.floor(s / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  return `${mm}:${ss}`;
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

function setBusy(busy) {
  startRec.disabled = busy;
  stopRec.disabled = !busy;
}

const isSecure = window.isSecureContext;

if (!navigator.mediaDevices || !window.MediaRecorder) {
  if (!isSecure) {
    const httpsUrl = 'https://med.67-205-142-127.nip.io' + window.location.pathname;
    recStatus.innerHTML = '';  // we'll set via DOM to avoid injection
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

startRec.addEventListener('click', async () => {
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
  mediaRecorder.start(1000);  // timeslice 1s — chunks accumulate

  setBusy(true);
  elapsedStart = Date.now();
  elapsedTimer = setInterval(() => {
    recStatus.textContent = `● Recording ${formatElapsed(Date.now() - elapsedStart)}`;
  }, 500);
});

stopRec.addEventListener('click', () => {
  if (!mediaRecorder) return;
  if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null; }
  recStatus.textContent = 'Finalizing recording…';
  try { mediaRecorder.stop(); } catch (e) { /* ignore */ }
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

    recStatus.textContent = 'Scoring…';
    const sResp = await fetch(`/api/exam/${window.EXAM_SLUG}/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript: tData.text || '' }),
    });
    if (!sResp.ok) throw new Error(`score ${sResp.status}`);
    const sData = await sResp.json();
    renderReport(sData, tData);
    recStatus.textContent = `Done — ${sData.covered_items}/${sData.total_items} items covered (${sData.score_pct}%)`;
  } catch (err) {
    recStatus.textContent = `Error: ${err.message}`;
    transcriptEl.textContent = '';
  } finally {
    setBusy(false);
  }
}

function gaugeClass(pct) {
  if (pct >= 75) return 'good';
  if (pct >= 40) return 'warn';
  return 'poor';
}

function renderReport(data, tData) {
  reportEl.textContent = '';

  // Summary stats row
  const header = document.createElement('div');
  header.className = 'report-header';
  const stats = [
    { value: `${data.score_pct}%`, label: 'overall coverage' },
    { value: `${data.covered_items}/${data.total_items}`, label: 'items hit' },
    { value: `${data.word_count}`, label: 'words spoken' },
    { value: `${tData && tData.duration ? Math.round(tData.duration) + 's' : '—'}`, label: 'audio duration' },
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

  // Section-by-section report
  const secReport = document.createElement('div');
  secReport.className = 'sections-report';

  const h = document.createElement('h3');
  h.textContent = 'Per-section coverage';
  secReport.appendChild(h);

  // Sort sections by score ascending so weakest are on top
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
    const summary = document.createElement('summary');
    summary.textContent = 'Show';
    details.appendChild(summary);
    sec.subsections.forEach(sub => {
      const block = document.createElement('div');
      block.className = 'sub-report';
      const h5 = document.createElement('h5');
      const nameSpan = document.createElement('span');
      nameSpan.textContent = sub.name;
      const small = document.createElement('small');
      small.textContent = `${sub.covered}/${sub.total} · ${sub.score_pct}%`;
      h5.appendChild(nameSpan);
      h5.appendChild(small);
      block.appendChild(h5);
      const ul = document.createElement('ul');
      sub.items.forEach(item => {
        const li = document.createElement('li');
        li.className = item.covered ? 'hit' : 'miss';
        li.textContent = item.item;
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
