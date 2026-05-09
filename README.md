# AI Document Processing Assistant — Portfolio Case Study

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

## Portfolio note

Portfolio case study by Oleksandr Stebeniev · 2026.
