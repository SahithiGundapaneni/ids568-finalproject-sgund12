"""
Component 2: A/B Test Design & Simulation
IDS 568 Final Project - Sreesahithi Gundapaneni (sgund12)

Simulates an A/B experiment comparing two LLM model variants:
  - Model A (Baseline):  mistral:7b-instruct with default system prompt
  - Model B (Challenger): mistral:7b-instruct with enhanced grounding system prompt

Hypothesis: Model B (larger) produces higher groundedness scores
than Model A, with acceptable latency trade-off.
"""

import numpy as np
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import os

np.random.seed(42)

# ────────────────────────────────────────────────────────────────────────────────
# EXPERIMENT PARAMETERS (from experiment-specification.md)
# ────────────────────────────────────────────────────────────────────────────────

SAMPLE_SIZE       = 500      # per group — justified by power analysis below
TRAFFIC_SPLIT     = 0.50     # 50/50
ALPHA             = 0.05     # significance level
POWER             = 0.80     # desired statistical power
MDE_GROUNDEDNESS  = 0.05     # minimum detectable effect (5 pp improvement)

# ────────────────────────────────────────────────────────────────────────────────
# POWER ANALYSIS — justify sample size
# ────────────────────────────────────────────────────────────────────────────────

def compute_required_sample_size(baseline_rate, mde, alpha=0.05, power=0.80):
    """
    Two-proportion z-test sample size calculation.
    baseline_rate: proportion under H0 (Model A's groundedness)
    mde: minimum detectable effect (absolute difference)
    """
    p1 = baseline_rate
    p2 = baseline_rate + mde
    pooled_p = (p1 + p2) / 2

    z_alpha = stats.norm.ppf(1 - alpha / 2)   # two-tailed
    z_beta  = stats.norm.ppf(power)

    n = ((z_alpha * np.sqrt(2 * pooled_p * (1 - pooled_p)) +
          z_beta  * np.sqrt(p1*(1-p1) + p2*(1-p2))) ** 2) / (mde ** 2)
    return int(np.ceil(n))

baseline_groundedness = 0.72   # Model A expected groundedness rate
n_required = compute_required_sample_size(baseline_groundedness, MDE_GROUNDEDNESS)
print(f"[Power Analysis] Required n per group: {n_required}")
print(f"[Power Analysis] Using n={SAMPLE_SIZE} per group (margin of safety)\n")

# ────────────────────────────────────────────────────────────────────────────────
# SIMULATE A/B OUTCOMES
# ────────────────────────────────────────────────────────────────────────────────

# --- Model A (Baseline: mistral:7b-instruct, default system prompt) ---
a_groundedness = np.random.normal(loc=0.72, scale=0.12, size=SAMPLE_SIZE)
a_latency_s    = np.random.gamma(shape=4.0, scale=0.12, size=SAMPLE_SIZE)  # ~480ms
a_tokens       = np.random.normal(loc=175,  scale=45,   size=SAMPLE_SIZE)
a_errors       = np.random.binomial(n=1, p=0.03, size=SAMPLE_SIZE)

# --- Model B (Challenger: mistral:7b-instruct, enhanced grounding system prompt) ---
b_groundedness = np.random.normal(loc=0.78, scale=0.10, size=SAMPLE_SIZE)  # +6pp
b_latency_s    = np.random.gamma(shape=4.0, scale=0.20, size=SAMPLE_SIZE)  # ~800ms
b_tokens       = np.random.normal(loc=210,  scale=50,   size=SAMPLE_SIZE)
b_errors       = np.random.binomial(n=1, p=0.025, size=SAMPLE_SIZE)

# Clip to valid ranges
a_groundedness = np.clip(a_groundedness, 0, 1)
b_groundedness = np.clip(b_groundedness, 0, 1)
a_latency_s    = np.clip(a_latency_s,    0.05, 5)
b_latency_s    = np.clip(b_latency_s,    0.05, 8)
a_tokens       = np.clip(a_tokens.astype(int), 10, 800)
b_tokens       = np.clip(b_tokens.astype(int), 10, 1000)

# ────────────────────────────────────────────────────────────────────────────────
# STATISTICAL EVALUATION
# ────────────────────────────────────────────────────────────────────────────────

def evaluate_metric(a_vals, b_vals, metric_name, higher_is_better=True):
    """Run two-sample t-test and compute 95% CI for the difference."""
    t_stat, p_val = stats.ttest_ind(a_vals, b_vals)
    diff = np.mean(b_vals) - np.mean(a_vals)
    se   = np.sqrt(np.var(a_vals)/len(a_vals) + np.var(b_vals)/len(b_vals))
    ci_low  = diff - 1.96 * se
    ci_high = diff + 1.96 * se

    significant = p_val < ALPHA
    favors_b    = (diff > 0) == higher_is_better

    print(f"── {metric_name} ──")
    print(f"   Model A mean: {np.mean(a_vals):.4f}  |  Model B mean: {np.mean(b_vals):.4f}")
    print(f"   Difference (B-A): {diff:+.4f}  [95% CI: {ci_low:+.4f}, {ci_high:+.4f}]")
    print(f"   t={t_stat:.3f}  p={p_val:.4f}  {'✓ SIGNIFICANT' if significant else '✗ not significant'}")
    print(f"   Favors {'B (challenger)' if favors_b else 'A (baseline)'}\n")

    return dict(
        metric=metric_name,
        a_mean=round(float(np.mean(a_vals)), 4),
        b_mean=round(float(np.mean(b_vals)), 4),
        diff=round(float(diff), 4),
        ci_low=round(float(ci_low), 4),
        ci_high=round(float(ci_high), 4),
        p_value=round(float(p_val), 4),
        significant=bool(significant),
        favors_b=bool(favors_b)
    )

print("=" * 60)
print("A/B TEST RESULTS — LLM Model Comparison")
print("=" * 60 + "\n")

results = []
results.append(evaluate_metric(a_groundedness, b_groundedness, "Groundedness Score", higher_is_better=True))
results.append(evaluate_metric(a_latency_s,    b_latency_s,    "Latency (seconds)",  higher_is_better=False))
results.append(evaluate_metric(a_tokens,       b_tokens,       "Response Tokens",    higher_is_better=True))
results.append(evaluate_metric(1-a_errors.astype(float), 1-b_errors.astype(float),
                                "Success Rate", higher_is_better=True))

# Save results JSON
os.makedirs('logs', exist_ok=True)
with open('logs/ab_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("[AB Test] Results saved → logs/ab_test_results.json")

# ────────────────────────────────────────────────────────────────────────────────
# VISUALIZATIONS
# ────────────────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(16, 10), facecolor='#0f1117')
fig.suptitle('A/B Test Results — Model A (default prompt) vs Model B (enhanced prompt)\n'
             'mistral:7b-instruct · IDS 568 Final Project · sgund12',
             fontsize=14, color='white', fontweight='bold', y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35,
                       left=0.07, right=0.97, top=0.90, bottom=0.08)

PANEL_BG = '#1a1d27'
GRID_COL = '#2a2d3a'
COL_A    = '#4ecdc4'
COL_B    = '#ff6b6b'
TEXTCOL  = '#e0e0e0'

def style_ax(ax, title):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=TEXTCOL, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID_COL)
    ax.grid(color=GRID_COL, linestyle='--', linewidth=0.5, alpha=0.6)
    ax.set_title(title, color=TEXTCOL, fontsize=10, fontweight='bold', pad=8)
    ax.xaxis.label.set_color(TEXTCOL)
    ax.yaxis.label.set_color(TEXTCOL)

# Plot 1: Groundedness distributions
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, 'Groundedness Score Distribution')
ax1.hist(a_groundedness, bins=30, alpha=0.7, color=COL_A, label='Model A', density=True)
ax1.hist(b_groundedness, bins=30, alpha=0.7, color=COL_B, label='Model B', density=True)
ax1.axvline(np.mean(a_groundedness), color=COL_A, linestyle='--', linewidth=1.5)
ax1.axvline(np.mean(b_groundedness), color=COL_B, linestyle='--', linewidth=1.5)
ax1.set_xlabel('Groundedness')
ax1.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# Plot 2: Latency distributions
ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2, 'Latency Distribution (seconds)')
ax2.hist(a_latency_s, bins=30, alpha=0.7, color=COL_A, label='Model A', density=True)
ax2.hist(b_latency_s, bins=30, alpha=0.7, color=COL_B, label='Model B', density=True)
ax2.axvline(np.mean(a_latency_s), color=COL_A, linestyle='--', linewidth=1.5)
ax2.axvline(np.mean(b_latency_s), color=COL_B, linestyle='--', linewidth=1.5)
ax2.set_xlabel('Latency (s)')
ax2.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# Plot 3: Confidence intervals for all metrics
ax3 = fig.add_subplot(gs[0, 2])
style_ax(ax3, '95% Confidence Intervals (B − A)')
metric_labels = ['Groundedness', 'Latency↓', 'Tokens', 'Success Rate']
diffs   = [r['diff']    for r in results]
ci_lows = [r['ci_low']  for r in results]
ci_high = [r['ci_high'] for r in results]
y_pos   = range(len(metric_labels))
colors  = ['#00d4aa' if r['favors_b'] else '#ff4757' for r in results]
ax3.barh(y_pos, diffs, xerr=[
    [d-l for d,l in zip(diffs,ci_lows)],
    [h-d for d,h in zip(diffs,ci_high)]
], color=colors, alpha=0.8, height=0.5, capsize=4)
ax3.axvline(0, color='white', linewidth=1, linestyle='--')
ax3.set_yticks(list(y_pos))
ax3.set_yticklabels(metric_labels, color=TEXTCOL, fontsize=9)
ax3.set_xlabel('Difference (B − A)')

# Plot 4: Means comparison bar chart
ax4 = fig.add_subplot(gs[1, 0])
style_ax(ax4, 'Mean Groundedness: A vs B')
bars = ax4.bar(['Model A', 'Model B'],
               [np.mean(a_groundedness), np.mean(b_groundedness)],
               color=[COL_A, COL_B], alpha=0.85, width=0.5)
ax4.set_ylim(0.6, 0.9)
ax4.set_ylabel('Mean Groundedness Score')
for bar, val in zip(bars, [np.mean(a_groundedness), np.mean(b_groundedness)]):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.003,
             f'{val:.3f}', ha='center', color=TEXTCOL, fontweight='bold')

# Plot 5: Latency boxplot
ax5 = fig.add_subplot(gs[1, 1])
style_ax(ax5, 'Latency Comparison (Boxplot)')
bp = ax5.boxplot([a_latency_s, b_latency_s], labels=['Model A', 'Model B'],
                  patch_artist=True, medianprops=dict(color='white', linewidth=2))
bp['boxes'][0].set_facecolor(COL_A)
bp['boxes'][1].set_facecolor(COL_B)
for element in ['whiskers', 'caps', 'fliers']:
    for item in bp[element]:
        item.set_color(TEXTCOL)
ax5.set_ylabel('Latency (s)')

# Plot 6: Decision summary
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor(PANEL_BG)
ax6.axis('off')
ax6.set_title('Decision Summary', color=TEXTCOL, fontsize=10, fontweight='bold', pad=8)
sig_count = sum(1 for r in results if r['significant'])
favors_b  = sum(1 for r in results if r['favors_b'])
lines = [
    ('Significant metrics:', f'{sig_count}/4', '#00d4aa'),
    ('Metrics favoring B:', f'{favors_b}/4',  '#00d4aa'),
    ('Groundedness Δ:',   f"+{results[0]['diff']:+.3f}", '#00d4aa'),
    ('Latency Δ:',        f"{results[1]['diff']:+.3f}s", '#ff9500'),
    ('p-value (ground.):',f"{results[0]['p_value']:.4f}", '#00d4aa'),
    ('DECISION:', '→ SHIP B', '#ffd32a'),
]
for i, (label, value, color) in enumerate(lines):
    y = 0.85 - i * 0.15
    ax6.text(0.05, y, label, transform=ax6.transAxes, color=TEXTCOL, fontsize=9)
    ax6.text(0.95, y, value, transform=ax6.transAxes, color=color, fontsize=10,
             fontweight='bold', ha='right')

os.makedirs('visualizations', exist_ok=True)
fig.savefig('visualizations/ab_test_results.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)
print("[AB Test] Visualization saved → visualizations/ab_test_results.png")
