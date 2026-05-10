# AI Document Processing Assistant — Portfolio Case Study

![Vite](https://img.shields.io/badge/Vite-Project-646CFF)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E)
![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-222222)
![AI Integrator](https://img.shields.io/badge/Role-AI%20Integrator-7C3AED)
![Portfolio](https://img.shields.io/badge/Type-Case%20Study-0F766E)

**Live demo:** https://stebenix.github.io/ai-document-processing-assistant/

An AI Integrator portfolio case study for automating document-heavy finance operations — from document intake and OCR/LLM extraction to validation rules, human review, audit trail, and ERP-ready export.

## What this project shows

- AI document intake from email, DMS and PDF upload
- OCR + LLM-style field extraction workflow
- Validation rules for IBAN, VAT, PO matching and ERP export readiness
- Human review queue and audit-ready governance logic
- Integrations screen with connected systems and connector health
- Analytics dashboard with operational KPIs
- Responsive desktop, tablet and mobile navigation

## Tech stack

- Vite
- Vanilla JavaScript
- HTML/CSS
- Responsive dashboard UI

## Run locally

```bash
npm install
npm run dev
```

Then open the local URL shown in the terminal.

## Build for production

```bash
npm run build
npm run preview
```

The production build is generated in `dist/`.

## Deploy

This project can be deployed to GitHub Pages, Vercel or Netlify.

## GitHub Pages auto-deploy

A ready GitHub Actions workflow is included in `.github/workflows/deploy.yml`. After pushing to the `main` branch, enable GitHub Pages in repository settings and select **GitHub Actions** as the source.

For Vercel/Netlify: import the GitHub repository and use:

- Build command: `npm run build`
- Publish directory: `dist`


## Python automation engine

This project includes a Python simulation engine that demonstrates the operational logic behind the dashboard:

- document intake
- OCR/LLM-style field extraction simulation
- validation rules
- risk scoring
- human review routing
- audit trail
- ERP export readiness
- AI recommendations

The frontend is a static product demo. The Python engine simulates the business logic and generates structured output data for the case study. Python does not need to run on GitHub Pages; it writes `outputs/demo_results.json` as static evidence and refreshes `public/demo_results.json` as the Vite/GitHub Pages-compatible static frontend copy.

### Static data bridge

The Python engine writes `outputs/demo_results.json`. For the static GitHub Pages dashboard, selected summary values can be exposed to the frontend through a static JSON copy, allowing the UI to display pipeline-generated metrics without a backend runtime. In this project, `outputs/demo_results.json` is the Python-generated source and `public/demo_results.json` is the static frontend copy loaded by the dashboard.

Intended refresh flow:

```bash
python -m python_engine.main
npm run build
```

Run it locally:

```bash
python -m python_engine.main
```

Run tests:

```bash
pytest
```

The automation layer is intentionally lightweight and portfolio-friendly: standard-library pipeline modules, deterministic sample data, explainable validation/risk logic, and clean JSON output without databases, APIs, Docker, Flask, FastAPI, or heavy ML dependencies.

## Portfolio note

Portfolio case study by Oleksandr Stebeniev · 2026.
