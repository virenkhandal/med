# Med Study

Simple study tool for memorizing physical-exam checklists. Pick an exam, then:

- **Quiz** — randomized multiple-choice questions, fresh each run.
- **Oral practice** — recite the full exam aloud; get a scored coverage report.

## Local dev

```bash
cd app
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/uvicorn medstudy.main:app --reload --port 8002
```

## Deployment

Pushes to `main` auto-deploy to the droplet via `.github/workflows/deploy.yml`.
Served on port **8002**.
