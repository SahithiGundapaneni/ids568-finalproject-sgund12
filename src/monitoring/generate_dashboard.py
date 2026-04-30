"""
Component 1: Dashboard Generator
IDS 568 Final Project - Sreesahithi Gundapaneni (sgund12)

Generates a comprehensive monitoring dashboard PNG showing simulated
LLM API traffic: latency, throughput, error rate, token distribution,
and drift score over time.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import random
import os

random.seed(42)
np.random.seed(42)

# ── Simulate time-series data (120 seconds of traffic) ─────────────────────────

TIME = np.arange(0, 120, 5)          # every 5 seconds
N    = len(TIME)

# Latency: mostly ~450ms, two spikes at t=40 and t=85
latency_p50 = np.random.normal(0.45, 0.05, N)
latency_p99 = latency_p50 + np.random.normal(0.4, 0.1, N)
latency_p99[8]  += 2.8   # spike at t=40
latency_p99[17] += 3.1   # spike at t=85
latency_p50[8]  += 0.9
latency_p50[17] += 1.2
latency_p50 = np.clip(latency_p50, 0.05, 5.0)
latency_p99 = np.clip(latency_p99, 0.1,  6.0)

# Throughput (requests/min)
throughput = np.random.normal(85, 8, N)
throughput[8]  -= 30   # dip during spike
throughput[17] -= 25
throughput = np.clip(throughput, 10, 120)

# Error rate (%)
error_rate = np.random.normal(2.5, 0.5, N)
error_rate[8]  += 6.0   # error surge during latency spike
error_rate[17] += 4.5
error_rate = np.clip(error_rate, 0, 15)

# Token distribution (histogram data)
tokens_normal = np.random.normal(180, 50, 300)
tokens_slow   = np.random.normal(420, 80, 30)
all_tokens    = np.concatenate([tokens_normal, tokens_slow])
all_tokens    = np.clip(all_tokens, 10, 900)

# Drift score (grows over time)
drift_base  = 0.12 + (TIME / 120) * 0.38
drift_score = drift_base + np.random.normal(0, 0.02, N)
drift_score = np.clip(drift_score, 0, 1)

# Input prompt lengths
prompt_lengths = np.random.normal(200, 70, 200)
prompt_lengths = np.clip(prompt_lengths, 10, 600)

# ── Build dashboard ─────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(18, 12), facecolor='#0f1117')
fig.suptitle(
    'LLM Inference API — Production Monitoring Dashboard\n'
    'IDS 568 Final Project · sgund12',
    fontsize=16, color='white', fontweight='bold', y=0.98
)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35,
                       left=0.06, right=0.97, top=0.91, bottom=0.07)

PANEL_BG  = '#1a1d27'
GRID_COL  = '#2a2d3a'
GREEN     = '#00d4aa'
ORANGE    = '#ff9500'
RED       = '#ff4757'
BLUE      = '#4ecdc4'
PURPLE    = '#a29bfe'
YELLOW    = '#ffd32a'
TEXTCOL   = '#e0e0e0'

def style_ax(ax, title):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=TEXTCOL, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID_COL)
    ax.grid(color=GRID_COL, linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_title(title, color=TEXTCOL, fontsize=10, fontweight='bold', pad=8)
    ax.xaxis.label.set_color(TEXTCOL)
    ax.yaxis.label.set_color(TEXTCOL)


# ── Panel 1: Latency over time ──────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
style_ax(ax1, '① Request Latency over Time (seconds)')
ax1.plot(TIME, latency_p50, color=GREEN,  linewidth=2,   label='P50 latency')
ax1.plot(TIME, latency_p99, color=ORANGE, linewidth=2,   label='P99 latency')
ax1.axhline(y=2.0, color=RED, linestyle='--', linewidth=1.2, label='Alert threshold (2s)')
ax1.fill_between(TIME, latency_p50, latency_p99, alpha=0.15, color=ORANGE)
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Latency (s)')
ax1.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXTCOL, framealpha=0.8)
# Annotate spikes
ax1.annotate('⚠ Spike', xy=(40, latency_p99[8]),
             xytext=(45, latency_p99[8]+0.5),
             arrowprops=dict(arrowstyle='->', color=RED),
             color=RED, fontsize=8)

# ── Panel 2: KPI summary boxes ──────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
ax2.set_facecolor(PANEL_BG)
ax2.axis('off')
ax2.set_title('② Live KPIs', color=TEXTCOL, fontsize=10, fontweight='bold', pad=8)

kpis = [
    ('Avg P50 Latency', f'{np.mean(latency_p50):.2f}s',  GREEN),
    ('Avg P99 Latency', f'{np.mean(latency_p99):.2f}s',  ORANGE),
    ('Avg Throughput',  f'{np.mean(throughput):.0f} rpm', BLUE),
    ('Avg Error Rate',  f'{np.mean(error_rate):.1f}%',   RED),
    ('Drift Score',     f'{drift_score[-1]:.2f}',         PURPLE),
]
for i, (label, value, color) in enumerate(kpis):
    y = 0.85 - i * 0.18
    ax2.text(0.05, y,       label, transform=ax2.transAxes,
             color=TEXTCOL, fontsize=9)
    ax2.text(0.95, y,       value, transform=ax2.transAxes,
             color=color,   fontsize=11, fontweight='bold', ha='right')

# ── Panel 3: Throughput ─────────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
style_ax(ax3, '③ Throughput (req/min)')
ax3.fill_between(TIME, throughput, alpha=0.4, color=BLUE)
ax3.plot(TIME, throughput, color=BLUE, linewidth=2)
ax3.axhline(y=60, color=YELLOW, linestyle='--', linewidth=1, label='Min SLA (60 rpm)')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Requests/min')
ax3.legend(fontsize=7, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# ── Panel 4: Error rate ─────────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
style_ax(ax4, '④ Error Rate (%)')
ax4.fill_between(TIME, error_rate, alpha=0.4, color=RED)
ax4.plot(TIME, error_rate, color=RED, linewidth=2)
ax4.axhline(y=5.0, color=YELLOW, linestyle='--', linewidth=1, label='Alert threshold (5%)')
ax4.set_xlabel('Time (s)')
ax4.set_ylabel('Error %')
ax4.legend(fontsize=7, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# ── Panel 5: Token distribution ─────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
style_ax(ax5, '⑤ Response Token Distribution')
ax5.hist(all_tokens, bins=30, color=PURPLE, alpha=0.8, edgecolor=PANEL_BG)
ax5.axvline(np.mean(all_tokens), color=YELLOW, linewidth=1.5,
            linestyle='--', label=f'Mean={np.mean(all_tokens):.0f}')
ax5.set_xlabel('Tokens')
ax5.set_ylabel('Count')
ax5.legend(fontsize=7, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# ── Panel 6: Drift score over time ──────────────────────────────────────────────
ax6 = fig.add_subplot(gs[2, :2])
style_ax(ax6, '⑥ Input Distribution Drift Score over Time')
ax6.plot(TIME, drift_score, color=PURPLE, linewidth=2.5)
ax6.fill_between(TIME, drift_score, alpha=0.2, color=PURPLE)
ax6.axhline(y=0.3, color=YELLOW, linestyle='--', linewidth=1.2,
            label='Warning threshold (0.30)')
ax6.axhline(y=0.45, color=RED, linestyle='--', linewidth=1.2,
            label='Critical threshold (0.45)')
ax6.set_ylim(0, 0.7)
ax6.set_xlabel('Time (s)')
ax6.set_ylabel('Drift Score')
ax6.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# ── Panel 7: Prompt length histogram ────────────────────────────────────────────
ax7 = fig.add_subplot(gs[2, 2])
style_ax(ax7, '⑦ Input Prompt Length (chars)')
ax7.hist(prompt_lengths, bins=25, color=GREEN, alpha=0.8, edgecolor=PANEL_BG)
ax7.axvline(np.mean(prompt_lengths), color=YELLOW, linewidth=1.5,
            linestyle='--', label=f'Mean={np.mean(prompt_lengths):.0f}')
ax7.set_xlabel('Characters')
ax7.set_ylabel('Count')
ax7.legend(fontsize=7, facecolor=PANEL_BG, labelcolor=TEXTCOL)

# ── Save ─────────────────────────────────────────────────────────────────────────
os.makedirs('visualizations', exist_ok=True)
out_path = 'visualizations/dashboard_screenshot.png'
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)
print(f"[Dashboard] Saved → {out_path}")
