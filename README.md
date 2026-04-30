# IDS 568 Final Project — Monitoring, Governance & Reflection
**Sreesahithi Gundapaneni (sgund12)**  
**Course:** IDS 568 — MLOps  
**Date:** April 30, 2026

---

## System Overview

This project instruments a **local LLM Inference API** (Mistral 7B Instruct, served via Ollama on Apple Silicon — model ID: `mistral:7b-instruct`, 4.4 GB) with a complete production operations framework, covering monitoring, A/B testing, governance documentation, drift detection, and AI risk assessment.

The system processes natural language Q&A requests and is evaluated across five integrated components that collectively demonstrate production-grade MLOps practices.

---

## Repository Structure

```
ids568-finalproject-sgund12/
├── src/
│   ├── monitoring/
│   │   ├── instrumentation.py      # Prometheus metrics emission
│   │   └── generate_dashboard.py  # Dashboard visualization generator
│   ├── ab_test/
│   │   └── simulation.py          # A/B test simulation + statistical analysis
│   └── drift/
│       └── drift_detection.py     # PSI + KS drift detection + visualizations
├── docs/
│   ├── dashboard-interpretation.md
│   ├── experiment-specification.md
│   ├── recommendation-memo.md
│   ├── model-card.md
│   ├── risk-register.md
│   ├── lineage-diagram.png
│   ├── drift-diagnostic-report.md
│   ├── governance-review.md
│   ├── risk-matrix.md
│   ├── system-boundary-diagram.png
│   └── cto-memo.md
├── dashboards/
│   ├── prometheus.yml              # Prometheus scrape config
│   └── grafana_export.json        # Grafana dashboard JSON
├── logs/
│   ├── audit-trail.json           # Structured model change log
│   ├── ab_test_results.json       # A/B test statistical results
│   └── drift_report.json          # Drift PSI/KS results
├── visualizations/
│   ├── dashboard_screenshot.png   # Component 1 dashboard
│   ├── ab_test_results.png        # Component 2 A/B charts
│   └── drift_analysis.png         # Component 4 drift charts
├── requirements.txt
└── README.md
```

---

## Component Links

| Component | Points | Key Files |
|---|---|---|
| [C1: Production Monitoring Dashboard](#c1) | 5 | `src/monitoring/`, `visualizations/dashboard_screenshot.png`, `docs/dashboard-interpretation.md` |
| [C2: A/B Test Design & Simulation](#c2) | 5 | `src/ab_test/simulation.py`, `docs/experiment-specification.md`, `docs/recommendation-memo.md` |
| [C3: Model Card & Governance Packet](#c3) | 5 | `docs/model-card.md`, `docs/risk-register.md`, `docs/lineage-diagram.png`, `logs/audit-trail.json` |
| [C4: Data Integrity & Drift Detection](#c4) | 5 | `src/drift/drift_detection.py`, `visualizations/drift_analysis.png`, `docs/drift-diagnostic-report.md` |
| [C5: AI Risk Assessment](#c5) | 5 | `docs/governance-review.md`, `docs/risk-matrix.md`, `docs/system-boundary-diagram.png`, `docs/cto-memo.md` |

---

## Setup & Reproduction Instructions

### Prerequisites
- Python 3.9+
- macOS with Apple Silicon (or any OS with Python)
- Ollama installed (optional — scripts run without it using simulated data)

### Install Dependencies
```bash
pip3 install -r requirements.txt
```

### Run Component 1 — Generate Dashboard
```bash
python3 src/monitoring/generate_dashboard.py
# Output: visualizations/dashboard_screenshot.png
```

### Run Component 2 — A/B Test Simulation
```bash
python3 src/ab_test/simulation.py
# Output: visualizations/ab_test_results.png, logs/ab_test_results.json
```

### Run Component 4 — Drift Detection
```bash
python3 src/drift/drift_detection.py
# Output: visualizations/drift_analysis.png, logs/drift_report.json
```

### Regenerate All Diagrams
```bash
python3 generate_diagrams.py
# Output: docs/lineage-diagram.png, docs/system-boundary-diagram.png
```

All scripts are self-contained and reproducible — no external APIs, no credentials required.

---

## Component Cross-References

This project is intentionally integrated — each component informs the others:

- The **monitoring dashboard (C1)** tracks the drift score that is formally analyzed in **C4**
- The **A/B test (C2)** uses groundedness as the primary metric, which is also tracked in C1 and impacted by drift in C4
- The **model card (C3)** documents the limitations that manifest as risks in **C5**
- The **drift triggers (C4)** connect to retraining events documented in the **audit trail (C3)**
- The **risk mitigations (C5)** reference monitoring capabilities established in **C1**

---

## Academic Integrity & AI Tool Usage

Per the course academic integrity policy, AI tools were used in this project for **scaffolding, code structure suggestions, and document formatting assistance**. All code was executed, tested, and verified locally on my machine. All written analysis, interpretations, risk assessments, and conclusions reflect my own understanding of the system built across Milestones 1–6. The mistral:7b-instruct model used throughout this project is the same model from my Milestone 6 submission (Ollama ID: 6577803aa9a0), and the failure modes documented (RAG misinterpretation, agent reasoning gaps) were observed during that milestone.

---

**Monitoring is harder than modelling.** Building a robust observability layer required more careful design than the model itself. Deciding what to measure, when to alert, and how to interpret metrics required deep understanding of the system's behaviour.

**Drift is inevitable.** The drift analysis showed that even a well-performing model degrades over time as user behaviour evolves. Treating retraining as a one-time event rather than a continuous process is a fundamental MLOps mistake.

**Documentation is a first-class artifact.** The model card and governance documents forced me to articulate what the model can and cannot do, which revealed gaps I hadn't noticed during development. Writing the CTO memo especially clarified which risks were genuinely high-priority versus theoretical.

**Statistical rigour matters for A/B tests.** The power analysis showed that intuitive sample sizes (n=100) are far too small to detect a 5pp improvement. Running underpowered experiments leads to false conclusions about model quality.

**Integration across components tells a richer story.** The most valuable insight emerged from connecting the drift analysis (C4) to the monitoring dashboard (C1) — the drift score that appeared as a gradually rising line in C1 translates to a concrete 12% groundedness drop analyzed in C4.
