"""
Generate lineage diagram and system boundary diagram as PNG files.
IDS 568 Final Project - sgund12
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import os

os.makedirs('docs', exist_ok=True)

# ── LINEAGE DIAGRAM ────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(16, 5), facecolor='#0f1117')
ax.set_facecolor('#0f1117')
ax.set_xlim(0, 16)
ax.set_ylim(0, 5)
ax.axis('off')
ax.set_title('Model Lineage Diagram — Data → Training → Evaluation → Deployment → Monitoring',
             color='white', fontsize=13, fontweight='bold', pad=12)

nodes = [
    (1.2, 2.5, 'Public Web\nCorpus\n(Mistral Training)', '#2d6a9f', '①'),
    (3.8, 2.5, 'Mistral 7B\nPre-training\n(Mistral AI)', '#2d6a9f', '②'),
    (6.4, 2.5, 'GGUF\nQuantization\n(Q4_K_M)', '#6c5ce7', '③'),
    (9.0, 2.5, 'Ollama\nLocal Serving\n(mistral:7b-instruct)', '#00b894', '④'),
    (11.6, 2.5, 'A/B Test\nEvaluation\n(EXP-001)', '#e17055', '⑤'),
    (14.2, 2.5, 'Production\nMonitoring\n(Prometheus)', '#fdcb6e', '⑥'),
]

for (x, y, label, color, num) in nodes:
    ax.add_patch(mpatches.FancyBboxPatch((x-0.9, y-0.9), 1.8, 1.8,
                  boxstyle='round,pad=0.1', facecolor=color, edgecolor='white',
                  linewidth=1.5, alpha=0.9))
    ax.text(x, y+0.15, label, ha='center', va='center', color='white',
            fontsize=7.5, fontweight='bold')
    ax.text(x, y-0.65, num, ha='center', va='center', color='white',
            fontsize=9, fontweight='bold')

# Arrows
for i in range(len(nodes)-1):
    x1 = nodes[i][0] + 0.9
    x2 = nodes[i+1][0] - 0.9
    y  = 2.5
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', color='#a0a0a0', lw=2))

# Bottom annotations
annotations = [
    (1.2, 1.1, 'Web, books, code\n~unknown volume'),
    (3.8, 1.1, 'Transformer arch\nknowledge cutoff ~2024'),
    (6.4, 1.1, '4-bit quantization\n4.4 GB on disk'),
    (9.0, 1.1, 'FastAPI wrapper\nlocal Metal GPU'),
    (11.6, 1.1, 'n=500/group\nGroundedness primary'),
    (14.2, 1.1, 'Prometheus metrics\nDrift + latency'),
]
for (x, y, note) in annotations:
    ax.text(x, y, note, ha='center', va='top', color='#a0a0a0', fontsize=6.5)

fig.savefig('docs/lineage-diagram.png', dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
plt.close(fig)
print("[Lineage] Saved → docs/lineage-diagram.png")


# ── SYSTEM BOUNDARY DIAGRAM ────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(14, 9), facecolor='#0f1117')
ax.set_facecolor('#0f1117')
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis('off')
ax.set_title('System Boundary Diagram — LLM Inference API\nIDS 568 Final Project · sgund12',
             color='white', fontsize=13, fontweight='bold', pad=12)

def box(ax, x, y, w, h, label, color, fontsize=9):
    ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h,
                  boxstyle='round,pad=0.15', facecolor=color,
                  edgecolor='white', linewidth=1.5, alpha=0.85))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center',
            color='white', fontsize=fontsize, fontweight='bold')

def arrow(ax, x1, y1, x2, y2, label='', color='#a0a0a0'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.1, my+0.1, label, color='#cccccc', fontsize=7)

# Main pipeline (vertical)
box(ax, 5.5, 7.4, 3.0, 0.9, '👤 User Request', '#2d6a9f', 10)
box(ax, 5.5, 6.0, 3.0, 0.9, '🛡 Input Validator\n(length, PII, injection)', '#6c5ce7', 8)
box(ax, 5.5, 4.6, 3.0, 0.9, '⚙️ FastAPI Wrapper\n(auth, rate limit, logging)', '#00b894', 8)
box(ax, 5.5, 3.2, 3.0, 0.9, 'Ollama LLM Engine\n(mistral:7b-instruct)', '#e17055', 8)
box(ax, 5.5, 1.8, 3.0, 0.9, '🔍 Output Filter\n(PII detect, content safety)', '#6c5ce7', 8)
box(ax, 5.5, 0.5, 3.0, 0.9, '📤 Response + Metrics', '#2d6a9f', 9)

# Side components
box(ax, 0.5, 4.6, 2.5, 0.9, '📊 Prometheus\nMetrics Server', '#fdcb6e', 8)
box(ax, 0.5, 3.2, 2.5, 0.9, '📈 Dashboard\n(Component 1)', '#fdcb6e', 8)
box(ax, 11.0, 4.6, 2.5, 0.9, '🔄 A/B Router\n(EXP-001)', '#fd79a8', 8)
box(ax, 11.0, 3.2, 2.5, 0.9, '📉 Drift Monitor\n(Component 4)', '#fd79a8', 8)
box(ax, 11.0, 1.8, 2.5, 0.9, '📋 Audit Trail\nLogger', '#b2bec3', 8)

# Vertical arrows (main pipeline)
for y_start, y_end in [(7.4, 6.9), (6.0, 6.5), (4.6, 5.1), (3.2, 4.2), (1.8, 3.2-0.1), (0.5+0.9, 1.8)]:
    pass

arrow(ax, 7.0, 7.4, 7.0, 6.9, '')
arrow(ax, 7.0, 6.0, 7.0, 5.5, '')
arrow(ax, 7.0, 4.6, 7.0, 4.1, '')
arrow(ax, 7.0, 3.2, 7.0, 2.7, '')
arrow(ax, 7.0, 1.8, 7.0, 1.4, '')

# Side arrows
arrow(ax, 5.5, 5.05, 3.0, 5.05, 'emit metrics', '#fdcb6e')
arrow(ax, 3.0, 4.6, 3.0, 4.1, '', '#fdcb6e')
arrow(ax, 8.5, 4.6+0.45, 11.0, 4.6+0.45, 'route 50/50', '#fd79a8')
arrow(ax, 11.0+1.25, 3.2, 11.0+1.25, 2.7, '', '#fd79a8')
arrow(ax, 8.5, 1.8+0.45, 11.0, 1.8+0.45, 'log events', '#b2bec3')

# Boundary box
ax.add_patch(mpatches.FancyBboxPatch((4.8, 0.2), 4.4, 8.4,
              boxstyle='round,pad=0.1', facecolor='none',
              edgecolor='#a29bfe', linewidth=2, linestyle='--', alpha=0.5))
ax.text(7.0, 8.7, 'System Boundary', ha='center', color='#a29bfe', fontsize=9)

fig.savefig('docs/system-boundary-diagram.png', dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
plt.close(fig)
print("[System] Saved → docs/system-boundary-diagram.png")
