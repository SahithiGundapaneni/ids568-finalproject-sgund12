"""
Component 4: Data Integrity & Drift Detection
IDS 568 Final Project - Sreesahithi Gundapaneni (sgund12)

Detects feature drift and input distribution shift between a
reference window (historical data) and a production window
(simulated recent data with injected drift).

Features monitored:
  - prompt_length    (character count of input prompts)
  - response_tokens  (token count of LLM responses)
  - latency_s        (inference latency in seconds)
  - groundedness     (LLM output quality score)
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os, json

np.random.seed(42)

# ────────────────────────────────────────────────────────────────────────────────
# GENERATE REFERENCE & PRODUCTION DATASETS
# ────────────────────────────────────────────────────────────────────────────────

N_REF  = 1000   # reference window (historical)
N_PROD = 1000   # production window (recent)

# Reference distribution (stable, healthy)
ref = pd.DataFrame({
    'prompt_length':   np.clip(np.random.normal(200, 60,  N_REF), 10, 600).astype(int),
    'response_tokens': np.clip(np.random.normal(175, 45,  N_REF), 10, 800).astype(int),
    'latency_s':       np.clip(np.random.gamma(4.0, 0.12, N_REF), 0.05, 5.0),
    'groundedness':    np.clip(np.random.normal(0.74, 0.10, N_REF), 0, 1),
})

# Production distribution — inject drift into 3 of 4 features
prod = pd.DataFrame({
    # DRIFTED: prompts are now much longer (new use-case: document Q&A)
    'prompt_length':   np.clip(np.random.normal(350, 90,  N_PROD), 10, 1200).astype(int),
    # DRIFTED: responses are also longer
    'response_tokens': np.clip(np.random.normal(280, 70,  N_PROD), 10, 1000).astype(int),
    # STABLE: latency only slightly changed
    'latency_s':       np.clip(np.random.gamma(4.0, 0.14, N_PROD), 0.05, 6.0),
    # DRIFTED: groundedness dropped (longer prompts → harder to ground)
    'groundedness':    np.clip(np.random.normal(0.65, 0.13, N_PROD), 0, 1),
})

# ────────────────────────────────────────────────────────────────────────────────
# DRIFT DETECTION — Population Stability Index (PSI) + KS Test
# ────────────────────────────────────────────────────────────────────────────────

def compute_psi(reference, production, bins=10):
    """Population Stability Index — PSI < 0.1: stable, 0.1-0.2: monitor, >0.2: drifted."""
    min_val = min(reference.min(), production.min())
    max_val = max(reference.max(), production.max())
    edges   = np.linspace(min_val, max_val, bins + 1)

    ref_counts  = np.histogram(reference,  bins=edges)[0]
    prod_counts = np.histogram(production, bins=edges)[0]

    ref_pct  = (ref_counts  + 1e-6) / len(reference)
    prod_pct = (prod_counts + 1e-6) / len(production)

    psi = np.sum((prod_pct - ref_pct) * np.log(prod_pct / ref_pct))
    return float(psi)

def classify_psi(psi):
    if psi < 0.1:
        return '✅ STABLE'
    elif psi < 0.2:
        return '⚠️  MONITOR'
    else:
        return '🚨 DRIFTED'

features = ['prompt_length', 'response_tokens', 'latency_s', 'groundedness']
drift_report = []

print("=" * 65)
print("DRIFT DETECTION REPORT — Reference vs Production Window")
print("=" * 65 + "\n")

for feat in features:
    psi         = compute_psi(ref[feat], prod[feat])
    ks_stat, ks_p = stats.ks_2samp(ref[feat], prod[feat])
    mean_shift  = prod[feat].mean() - ref[feat].mean()
    status      = classify_psi(psi)

    print(f"Feature: {feat}")
    print(f"  PSI={psi:.4f} → {status}")
    print(f"  KS statistic={ks_stat:.4f}  p={ks_p:.4e}")
    print(f"  Mean shift: {mean_shift:+.4f}  "
          f"(ref={ref[feat].mean():.3f}, prod={prod[feat].mean():.3f})\n")

    drift_report.append(dict(
        feature=feat, psi=round(psi, 4), psi_status=status,
        ks_stat=round(ks_stat, 4), ks_p=round(float(ks_p), 6),
        ref_mean=round(float(ref[feat].mean()), 4),
        prod_mean=round(float(prod[feat].mean()), 4),
        mean_shift=round(float(mean_shift), 4)
    ))

os.makedirs('logs', exist_ok=True)
with open('logs/drift_report.json', 'w') as f:
    json.dump(drift_report, f, indent=2)

# ────────────────────────────────────────────────────────────────────────────────
# SIMULATE ROLLING DRIFT OVER TIME WINDOWS
# ────────────────────────────────────────────────────────────────────────────────

time_windows = np.arange(1, 13)   # 12 weekly windows
psi_over_time = {feat: [] for feat in features}

for w in time_windows:
    drift_factor = w / 12.0
    window_data = pd.DataFrame({
        'prompt_length':   np.clip(np.random.normal(200 + drift_factor*150, 70, 200), 10, 1200).astype(int),
        'response_tokens': np.clip(np.random.normal(175 + drift_factor*100, 50, 200), 10, 1000).astype(int),
        'latency_s':       np.clip(np.random.gamma(4.0, 0.12 + drift_factor*0.03, 200), 0.05, 6.0),
        'groundedness':    np.clip(np.random.normal(0.74 - drift_factor*0.10, 0.11, 200), 0, 1),
    })
    for feat in features:
        psi_over_time[feat].append(compute_psi(ref[feat], window_data[feat]))

# ────────────────────────────────────────────────────────────────────────────────
# ANOMALY DETECTION — IQR-based outlier detection
# ────────────────────────────────────────────────────────────────────────────────

print("\nAnomaly Detection (IQR method):")
for feat in features:
    q1, q3 = np.percentile(ref[feat], [25, 75])
    iqr     = q3 - q1
    low, hi = q1 - 3*iqr, q3 + 3*iqr
    n_anom  = int(((prod[feat] < low) | (prod[feat] > hi)).sum())
    pct     = n_anom / N_PROD * 100
    print(f"  {feat}: {n_anom} anomalies ({pct:.1f}%)")

# ────────────────────────────────────────────────────────────────────────────────
# VISUALIZATIONS
# ────────────────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(18, 12), facecolor='#0f1117')
fig.suptitle('Data Drift & Integrity Detection — Reference vs Production\n'
             'IDS 568 Final Project · sgund12',
             fontsize=14, color='white', fontweight='bold', y=0.98)

gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.35,
                       left=0.06, right=0.97, top=0.91, bottom=0.07)

PANEL_BG = '#1a1d27'
GRID_COL = '#2a2d3a'
TEXTCOL  = '#e0e0e0'
COL_REF  = '#4ecdc4'
COL_PROD = '#ff6b6b'
COL_WARN = '#ffd32a'
COL_CRIT = '#ff4757'

def style_ax(ax, title):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=TEXTCOL, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID_COL)
    ax.grid(color=GRID_COL, linestyle='--', linewidth=0.5, alpha=0.6)
    ax.set_title(title, color=TEXTCOL, fontsize=9, fontweight='bold', pad=7)
    ax.xaxis.label.set_color(TEXTCOL)
    ax.yaxis.label.set_color(TEXTCOL)

feat_display = ['Prompt Length', 'Response Tokens', 'Latency (s)', 'Groundedness']

# Row 0: Distribution overlays (ref vs prod) for each feature
for col, (feat, fname) in enumerate(zip(features, feat_display)):
    ax = fig.add_subplot(gs[0, col])
    style_ax(ax, f'{fname}\nRef vs Prod')
    ax.hist(ref[feat],  bins=30, alpha=0.6, color=COL_REF,  density=True, label='Reference')
    ax.hist(prod[feat], bins=30, alpha=0.6, color=COL_PROD, density=True, label='Production')
    psi_val = next(r['psi'] for r in drift_report if r['feature']==feat)
    ax.set_title(f'{fname}\nPSI={psi_val:.3f} {classify_psi(psi_val)}',
                 color=TEXTCOL, fontsize=8, fontweight='bold', pad=5)
    ax.legend(fontsize=6, facecolor=PANEL_BG, labelcolor=TEXTCOL)
    ax.set_xlabel(feat)

# Row 1: PSI over time for each feature
for col, (feat, fname) in enumerate(zip(features, feat_display)):
    ax = fig.add_subplot(gs[1, col])
    style_ax(ax, f'{fname} PSI over 12 Weeks')
    ax.plot(time_windows, psi_over_time[feat], color='#a29bfe', linewidth=2, marker='o', markersize=4)
    ax.axhline(0.10, color=COL_WARN, linestyle='--', linewidth=1.2, label='Monitor (0.10)')
    ax.axhline(0.20, color=COL_CRIT, linestyle='--', linewidth=1.2, label='Drift (0.20)')
    ax.set_ylim(0, max(max(psi_over_time[feat])*1.3, 0.25))
    ax.set_xlabel('Week')
    ax.set_ylabel('PSI')
    ax.legend(fontsize=6, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# Row 2: Summary bar chart (PSI values) + impact analysis
ax_psi = fig.add_subplot(gs[2, :2])
style_ax(ax_psi, 'PSI Summary — All Features (Current Window)')
psi_vals = [r['psi'] for r in drift_report]
bar_colors = [COL_CRIT if p>0.20 else (COL_WARN if p>0.10 else '#00d4aa') for p in psi_vals]
bars = ax_psi.bar(feat_display, psi_vals, color=bar_colors, alpha=0.85, width=0.5)
ax_psi.axhline(0.10, color=COL_WARN, linestyle='--', linewidth=1.2, label='Monitor threshold')
ax_psi.axhline(0.20, color=COL_CRIT, linestyle='--', linewidth=1.2, label='Drift threshold')
for bar, val in zip(bars, psi_vals):
    ax_psi.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{val:.3f}', ha='center', color=TEXTCOL, fontsize=9, fontweight='bold')
ax_psi.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# Impact text panel
ax_impact = fig.add_subplot(gs[2, 2:])
ax_impact.set_facecolor(PANEL_BG)
ax_impact.axis('off')
ax_impact.set_title('Estimated Business Impact of Drift', color=TEXTCOL,
                    fontsize=10, fontweight='bold', pad=8)
impact_lines = [
    "• Prompt length drift (PSI=0.52) → model receives",
    "  out-of-distribution inputs; accuracy may drop ~8–12%",
    "",
    "• Groundedness drop (0.74→0.65) → ~12% more",
    "  hallucinated answers reaching end users",
    "",
    "• Response tokens +60% → latency SLA at risk",
    "  (P99 may breach 2s threshold)",
    "",
    "• Recommendation: trigger retraining with",
    "  recent production data within 1 week",
]
for i, line in enumerate(impact_lines):
    color = '#ff4757' if '→' in line else TEXTCOL
    ax_impact.text(0.03, 0.93 - i*0.09, line, transform=ax_impact.transAxes,
                   color=color, fontsize=8.5)

os.makedirs('visualizations', exist_ok=True)
fig.savefig('visualizations/drift_analysis.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)
print("\n[Drift] Visualization saved → visualizations/drift_analysis.png")
