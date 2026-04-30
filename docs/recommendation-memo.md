# Recommendation Memo — A/B Test EXP-001
**To:** ML Platform Team  
**From:** Sreesahithi Gundapaneni (sgund12)  
**Date:** April 30, 2026  
**Re:** Ship Decision — Model B (llama3.2:8b) vs Model A (llama3.2:3b)

---

## Recommendation: **SHIP MODEL B** ✅

---

## Summary of Findings

The A/B experiment (n=500 per group) comparing the 3B and 8B parameter Ollama models produced a clear and statistically significant result on the primary metric.

| Metric | Model A (3B) | Model B (8B) | Δ | Significant? |
|---|---|---|---|---|
| Groundedness | 0.720 | 0.784 | **+0.064** | ✅ Yes (p < 0.001) |
| Latency (s) | 0.487 | 0.821 | +0.334s | ✅ Yes (p < 0.001) |
| Response Tokens | 175 | 205 | +30 | ✅ Yes (p < 0.001) |
| Success Rate | 96.8% | 96.4% | −0.4pp | ✗ No (p = 0.727) |

## Reasoning

**Quality gain is material.** A +6.4 percentage point improvement in groundedness means roughly 1 in 16 previously hallucinated or poorly grounded answers will now be correctly grounded. At scale, this is a significant reduction in misinformation risk.

**Latency increase is acceptable.** Model B's mean latency of 0.82s remains within the 1-second interactive SLA. The +334ms increase is noticeable but not user-impacting. P99 latency should be monitored post-launch.

**Reliability is unchanged.** The −0.4pp difference in success rate is not statistically significant (p = 0.73), meaning Model B is equally reliable.

**No new risks introduced.** Model B produces longer responses (+30 tokens on average) which may slightly increase downstream rendering costs but does not raise safety or compliance concerns.

## Conditions for Shipping

1. Deploy with a **canary rollout** (10% → 50% → 100%) over 48 hours
2. Monitor P99 latency — if it exceeds **2.0 seconds** for 5+ minutes, pause rollout
3. Set a **drift score alert** at 0.30 to detect if Model B changes input distribution behaviour
4. Re-evaluate after 7 days of full production traffic
