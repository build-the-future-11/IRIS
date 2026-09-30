# IRIS — Final Research Status (2026-09-30)

## Disposition
**CLOSED FOR THE CURRENT EVIDENCE LINE; FRONTIER CONFIRMATION REMAINS PROTOCOL-BLOCKED.**

The retained v0.2 package is a mixed/negative research result. The protected confirmatory family (experiment IDs 1000–1029) must remain unopened until canonical raw-trajectory provenance is recovered.

## Retained supported findings
- EXP-004 scalar-v2 was reproduced byte-identically in the retained reproducibility audit.
- EXP-003 learned-sequence v2 was reproduced within floating-point-scale deltas without changing the negative scientific verdict.
- The development-only common adaptation harness retained 720 raw rows over seeds 0–9 and reproduced its frozen negative verdict.
- The tested PABIM mechanism did not beat the strong Huber/static robust controls in the learned-sequence gate.
- The common-harness verdict remains `NEGATIVE_OR_INCONCLUSIVE_DEVELOPMENT_GATE`.

## Not established
This evidence does not establish real-world temporal generalization, superiority to faithful robust BOCPD/generalized-Bayes/AO-IO baselines, superiority to GRU/LSTM/SSM controls, a positive mechanism contribution, state-of-the-art performance, or submission readiness.

## Hard blocker
The exact canonical observation/state trajectory identity required by the frontier protocol has not been recovered. Source hashes and deterministic runners are not substitutes for exact input identity.

Therefore:
1. do not regenerate approximate trajectories and relabel them canonical;
2. do not execute experiment IDs 1000–1029;
3. recover an explicit identity defined by generator source hash + config hash + exact outer seed list + dependency/PRNG version;
4. if that identity cannot be recovered, preserve v0.2 as the final mixed/negative package.

## Final rule
The current research line is finished as a negative/inconclusive package. Any new positive mechanism claim requires a newly frozen successor study after the provenance problem is resolved.
