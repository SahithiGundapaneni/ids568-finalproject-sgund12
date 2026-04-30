# A/B Experiment Specification
**IDS 568 Final Project · Sreesahithi Gundapaneni (sgund12)**

---

## Experiment ID
`EXP-001-model-size-comparison`

## Experiment Title
Comparing LLM Model Size on Groundedness and Latency for a Q&A Inference API

---

## 1. Hypothesis

**Null Hypothesis (H₀):** There is no statistically significant difference in groundedness score between Model A (llama3.2:3b, baseline) and Model B (llama3.2:8b, challenger).

**Alternative Hypothesis (H₁):** Model B produces a higher groundedness score than Model A by at least 5 percentage points (the Minimum Detectable Effect).

**Rationale:** Larger parameter models generally produce better-grounded responses for factual Q&A tasks, but incur higher latency. This experiment quantifies whether the quality gain justifies the latency cost.

---

## 2. Success Metrics

| Metric | Type | Direction | Primary? |
|---|---|---|---|
| Groundedness Score | Quality (0–1) | Higher is better | ✅ Primary |
| Inference Latency (s) | Performance | Lower is better | ✅ Primary (guardrail) |
| Response Token Count | Quality proxy | Higher is better | Secondary |
| Success Rate (1 - error rate) | Reliability | Higher is better | Secondary (guardrail) |

**Decision rule:** Recommend Model B only if groundedness improvement is statistically significant AND P99 latency does not exceed 2.5 seconds (1.5× the current SLA of 1.67s at P99).

---

## 3. Randomization Method

- **Unit of randomization:** Individual inference request (not user session), since LLM Q&A is stateless
- **Traffic split:** 50% to Model A (control), 50% to Model B (treatment)
- **Assignment mechanism:** Hash of `request_id % 2` — deterministic, reproducible, with no session stickiness required
- **Exclusion criteria:** Requests with malformed prompts (empty string, >2000 chars) are excluded from analysis

---

## 4. Required Sample Size & Duration

### Power Analysis

Using a two-proportion z-test with:
- Baseline groundedness (Model A): μ = 0.72
- Minimum Detectable Effect (MDE): Δ = 0.05 (absolute)
- Significance level: α = 0.05 (two-tailed)
- Desired power: 1 − β = 0.80

**Formula:**
```
n = [(z_α/2 × √(2p̄(1-p̄)) + z_β × √(p₁(1-p₁) + p₂(1-p₂)))² ] / Δ²
```

This yields **n ≥ 1,192 per group** for the primary metric.

### Simulation Note
The simulation uses n=500 per group as a demonstration. In production, the experiment would run until reaching n=1,200 per arm. At ~85 requests/minute throughput with 50% split, this requires **~14 minutes** of real traffic — making the experiment extremely fast to run.

### Duration recommendation
Run for at least **24 hours** to capture time-of-day variation, even if statistical significance is reached earlier (avoids novelty effect bias).

---

## 5. Statistical Test

- **Primary test:** Two-sample independent t-test on groundedness scores
- **Secondary test:** Two-sample t-test on latency values
- **Confidence intervals:** 95% CI for all mean differences
- **Multiple comparisons:** Bonferroni correction applied (4 metrics → α_adjusted = 0.0125 per test)
- **Stopping rules:** No early stopping — run to predetermined sample size to control Type I error

---

## 6. Ethical Considerations

- No PII is processed during the experiment
- Both model variants produce output of sufficient quality for the use case (neither is harmful)
- Experiment is reversible — traffic can be returned 100% to Model A within seconds
