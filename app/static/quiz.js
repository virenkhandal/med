const startBtn = document.getElementById('startBtn');
const quizEl = document.getElementById('quiz');
const countInput = document.getElementById('count');

startBtn.addEventListener('click', startQuiz);

async function startQuiz() {
  const count = Math.max(1, Math.min(30, parseInt(countInput.value, 10) || 10));
  quizEl.textContent = '';
  const loading = document.createElement('p');
  loading.className = 'status';
  loading.textContent = 'Loading…';
  quizEl.appendChild(loading);
  try {
    const res = await fetch(`/api/exam/${window.EXAM_SLUG}/quiz`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count }),
    });
    if (!res.ok) throw new Error(`Server ${res.status}`);
    const data = await res.json();
    renderQuiz(data.questions);
  } catch (err) {
    quizEl.textContent = '';
    const p = document.createElement('p');
    p.className = 'status';
    p.textContent = `Error: ${err.message}`;
    quizEl.appendChild(p);
  }
}

function renderQuiz(questions) {
  quizEl.textContent = '';
  const state = {
    answers: new Array(questions.length).fill(null),
    correct: 0,
  };
  questions.forEach((q, qi) => {
    const qDiv = document.createElement('div');
    qDiv.className = 'question';
    const prompt = document.createElement('div');
    prompt.className = 'q-prompt';
    prompt.textContent = `${qi + 1}. ${q.prompt}`;
    qDiv.appendChild(prompt);
    q.choices.forEach((choice, ci) => {
      const btn = document.createElement('button');
      btn.className = 'choice';
      btn.type = 'button';
      btn.textContent = choice;
      btn.addEventListener('click', () => {
        if (state.answers[qi] !== null) return;
        state.answers[qi] = ci;
        const isCorrect = ci === q.answer_index;
        if (isCorrect) state.correct++;
        Array.from(qDiv.querySelectorAll('.choice')).forEach((el, idx) => {
          el.classList.add('locked');
          if (idx === q.answer_index) el.classList.add('correct');
          if (idx === ci && !isCorrect) el.classList.add('wrong');
        });
        if (state.answers.every(a => a !== null)) renderSummary(state, questions.length);
      });
      qDiv.appendChild(btn);
    });
    quizEl.appendChild(qDiv);
  });
}

function renderSummary(state, total) {
  const div = document.createElement('div');
  div.className = 'quiz-summary';
  const pct = ((state.correct / total) * 100).toFixed(0);
  const h = document.createElement('h3');
  h.textContent = `Score: ${state.correct} / ${total} (${pct}%)`;
  div.appendChild(h);
  const btn = document.createElement('button');
  btn.className = 'secondary';
  btn.textContent = 'New quiz';
  btn.addEventListener('click', () => location.reload());
  div.appendChild(btn);
  quizEl.appendChild(div);
  div.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
