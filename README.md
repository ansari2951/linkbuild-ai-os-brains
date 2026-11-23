# LINKBUILD AI OS Brains ⚡

Autonomous Multi-Agent Link Building & SEO Intelligence Operating System (24/7 Autonomous Daemon & Cloud Automation Edition).

[![Vercel Deployment](https://img.shields.io/badge/Deployed-Vercel-black?logo=vercel)](https://linkbuild-ai-os-brains.vercel.app)
[![GitHub Repository](https://img.shields.io/badge/GitHub-ansari2951%2Flinkbuild--ai--os--brains-181717?logo=github)](https://github.com/ansari2951/linkbuild-ai-os-brains)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Unit Tests](https://img.shields.io/badge/Tests-9%20Passing-emerald)](https://github.com/ansari2951/linkbuild-ai-os-brains)
[![24/7 Automation](https://img.shields.io/badge/24%2F7-Autonomous-green)](https://github.com/ansari2951/linkbuild-ai-os-brains/actions)

---

## 🚀 Key Highlights & Architecture

LINKBUILD AI OS Brains is a modular, high-performance platform engineered for complete link building automation, technical SEO auditing, publisher intelligence, outreach lifecycle management, and **24/7 continuous autonomous execution**.

### 🧠 Autonomous Multi-Agent Brains (All 6 Connected)
- **Publisher Research Brain**: Discovers authority publishers, scores editorial relevance, and isolates contact endpoints.
- **Publisher Outreach Brain**: Auto-drafts hyper-personalized pitches for guest articles and editorial collaborations with safety approval gates.
- **Publisher Deal Brain**: Analyzes publisher fee structures, budget thresholds, and drafts intelligent counter-offers.
- **Client Research Brain**: Identifies and scores high-fit client prospects based on SEO and link building service demand.
- **Client Outreach Brain**: Drafts custom authority backlink growth proposals and audit pitches.
- **Email Intelligence Brain**: Discovers public communication endpoints, verifies DNS MX health (100% active), and classifies organizational roles (Editors, PR, Advertising).
- **Central SEO Pipeline Engine**: Orchestrates 12 independent diagnostic modules with graceful rate-limit fallbacks.
- **Central Brain Orchestrator**: SQLite-backed persistent task dispatch engine managing background agent queues.

---

## 🕒 24/7 Continuous Autonomous Operation

The system can run completely 24/7 in two complementary modes:

### Mode A: 24/7 Cloud Automation (GitHub Actions)
Runs in the cloud on GitHub's free infrastructure without needing your laptop to stay powered on.
* Runs on a cron schedule every 6 hours (`0 */6 * * *`).
* Executes full test suites, processes Central Brain queues, runs the 12-module SEO pipeline, and automatically syncs intelligence reports back to the repository.
* Workflow configuration: `.github/workflows/central_brain_247.yml`.

### Mode B: Local 24/7 Autonomous Daemon
Continuously runs on your machine with auto-recovery, task claiming, and periodic heartbeats:
```bash
python run_247_daemon.py --interval 30
```
Or simply double-click:
* `scripts/start_247_daemon.bat` (Interactive terminal runner with auto-restart)
* `scripts/start_background.vbs` (Silent invisible background runner)
* `scripts/stop_daemon.bat` (Graceful shutdown)

Heartbeats and daemon health are continuously recorded in `data/private/system/heartbeat.json`.

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

### 1. Start 24/7 Autonomous Daemon
```bash
python run_247_daemon.py
```

### 2. Run Single Central Brain Cycle
```bash
python run_central_brain.py
```

### 3. Run Full 12-Module SEO Pipeline
```bash
python run_seo_pipeline.py --mode manual
```

### 4. Run Test Suite
```bash
python -m unittest discover tests
```

---

## 🌐 Web Dashboard & Vercel Deployment

Live Production URL: **[https://linkbuild-ai-os-brains.vercel.app](https://linkbuild-ai-os-brains.vercel.app)**
* Glassmorphism dark mode UI
* Real-time metrics and agent monitor
* Interactive link opportunity scanner
* Production deployment configured via `vercel.json`
