# LINKBUILD AI OS Brains ⚡

Autonomous Multi-Agent Link Building & SEO Intelligence Operating System.

[![Vercel Deployment](https://img.shields.io/badge/Deployed-Vercel-black?logo=vercel)](https://vercel.com)
[![GitHub Repository](https://img.shields.io/badge/GitHub-ansari2951%2Flinkbuild--ai--os--brains-181717?logo=github)](https://github.com/ansari2951/linkbuild-ai-os-brains)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Unit Tests](https://img.shields.io/badge/Tests-9%20Passing-emerald)](https://github.com/ansari2951/linkbuild-ai-os-brains)

---

## 🚀 Key Highlights & Architecture

LINKBUILD AI OS Brains is a modular, high-performance platform engineered for complete link building automation, technical SEO auditing, publisher intelligence, and outreach lifecycle management.

### 🧠 Autonomous Multi-Agent Brains
- **Publisher Research Brain**: Uncovers high-authority niche publishers, scores editorial relevance, and isolates contact endpoints.
- **Email Intelligence Brain**: Discovers public communication endpoints, verifies DNS MX health (100% active), and classifies organizational roles (Editors, PR, Advertising).
- **Publisher Outreach Brain**: Auto-drafts hyper-personalized pitches for guest articles and editorial collaborations with safety approval gates.
- **Central SEO Pipeline Engine**: Orchestrates 12 independent diagnostic modules with graceful rate-limit fallbacks.
- **Central Brain Orchestrator**: SQLite-backed persistent task dispatch engine managing background agent queues.

---

## 🔍 SEO Intelligence Suite (12 Modules)

| # | Module | Capabilities |
|---|---|---|
| 1 | **Site Audit** | HTTP headers, canonical validation, meta descriptions, and H1 hierarchy. |
| 2 | **Website Crawler** | Recursive URL discovery, depth analysis, and internal linking web. |
| 3 | **Image Intelligence** | ALT text coverage, empty tags, lazy-loading check, and dimension shift prevention. |
| 4 | **Indexing Intelligence** | `robots.txt` directive parsing and XML sitemap auto-discovery. |
| 5 | **Internal Link Analysis** | Anchor text evaluation, empty/generic anchors, and internal-to-external link ratio. |
| 6 | **Core Web Vitals** | Real-time TTFB, latency timing, and PageSpeed metrics with HTTP fallback. |
| 7 | **Redirect Analysis** | 301/302/307/308 chain tracing and loop detection. |
| 8 | **Schema Analysis** | JSON-LD validation (LocalBusiness, Organization, WebSite, ContactPoint). |
| 9 | **Keyword Intelligence** | Search intent classification (Commercial, Transactional, Informational). |
| 10 | **Competitor Intelligence**| Domain Rating (DR), organic traffic, and backlink authority scoring. |
| 11 | **Content Gap Analysis** | Competitor keyword overlap and ranked link building opportunity scoring. |
| 12 | **Keyword Clustering** | Semantic topic grouping for content silos and campaign strategy. |

---

## 💻 Quick Start & Commands

### 1. Run Central Brain & Orchestrator
```bash
python run_central_brain.py
```

### 2. Run Full 12-Module SEO Pipeline
```bash
python run_seo_pipeline.py --mode manual
```

### 3. Run Unit Tests
```bash
python -m unittest discover tests
```

---

## 🌐 Web Dashboard & Vercel Deployment

The project features a sleek, responsive Glassmorphism dashboard located in `index.html` configured for instant zero-config deployment on Vercel (`vercel.json`).

### Deploy to Vercel via CLI
```bash
vercel --prod
```

Or connect `https://github.com/ansari2951/linkbuild-ai-os-brains` directly in the [Vercel Dashboard](https://vercel.com/new).
