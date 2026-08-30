# IRIS Robust Baseline Protocol

**Date:** 2026-08-30  
**Status:** DEVELOPMENT-ONLY; protected confirmatory experiment IDs `1000–1029` remain closed.

## Purpose

The current IRIS evidence is mixed/negative and the frontier is blocked on canonical trajectory provenance. The next admissible scientific task is therefore not a new named mechanism. It is to implement faithful, strong change-aware and outlier-robust baselines in a common development harness.

This protocol freezes that baseline work before implementation so that later comparisons cannot be weakened post hoc.

## Baseline families to implement

### B0 — Classical state-space filter

A correctly specified non-robust reference filter for the common state-space model. This is a calibration reference, not a straw-man competitor.

### B1 — Fixed Huber robust filter

Implement a Huberised robust update with thresholds fixed before evaluation. Keep the strongest existing static robust control already used by IRIS and expose all clipping/tuning values in the result manifest.

### B2 — AO-robust filter

Implement an additive-outlier robust filter, with contamination acting in the observation/measurement channel. The implementation must follow a published AO-robust formulation rather than an informal residual clipping approximation.

### B3 — IO-robust filter

Implement an innovation-outlier robust filter, with contamination acting in the latent/process channel. This must be kept conceptually distinct from AO robustness because genuine regime/state changes can look like process innovations.

### B4 — Joint AO/IO robust filter

Implement a method explicitly designed to distinguish or jointly handle additive and innovation outliers. CE-BASS is an admissible reference implementation family because it is designed for both and can represent multimodality.

### B5 — Robust Bayesian online changepoint detector

Implement a generalized-Bayes robust BOCPD baseline faithful to the published method, including its run-length/changepoint posterior rather than replacing it with a heuristic detector.

The preferred primary reference is Altamirano, Briol & Knoblauch (ICML 2023), *Robust and Scalable Bayesian Online Changepoint Detection*. A beta-divergence BOCPD implementation is also admissible as a separately named baseline if it is implemented faithfully.

## Development-only protocol

- Use only development experiment IDs/seeds that are disjoint from protected experiment IDs `1000–1029`.
- Do not use any protected confirmatory outcome for parameter selection, model selection, stopping, debugging, or threshold tuning.
- Do not claim canonical-trajectory reproduction until exact provenance is resolved.
- Every run must record generator/source identity, configuration, outer seed or experiment ID, dependency versions, and baseline hyperparameters.
- Preserve every baseline result, including failures and cases where IRIS loses.

## Minimum scenario matrix

Evaluate every baseline on the same development scenarios already represented by the common learned harness, including at minimum:

1. clean/non-contaminated sequence;
2. isolated heavy-tailed/additive contamination;
3. persistent latent/process shift;
4. false-open/no-change guardrail;
5. mixed contamination if the generator supports it without changing the frozen scenario semantics.

Do not introduce a scenario solely because it favors the IRIS mechanism.

## Metrics

Record the metrics already used by the common harness. Additionally, where meaningful for a baseline, retain:

- predictive loss / state-estimation error;
- changepoint detection delay;
- false-positive / false-open rate;
- recovery time after contamination or shift;
- calibration of uncertainty or changepoint posterior;
- wall-clock runtime and peak memory.

Any new metric must be computed for all applicable methods, not only IRIS.

## Falsification gates

A successor IRIS claim must remain blocked unless it beats the strongest faithful robust baseline under a pre-frozen rule. At minimum:

- **Clean non-inferiority:** no material degradation on clean data.
- **Strong robust-control gate:** outperform the best faithful fixed/robust baseline on the target contamination regime by the predeclared margin.
- **Persistent-shift gate:** do not trade robustness to isolated outliers for failure to adapt to genuine persistent shifts.
- **False-open guardrail:** robust adaptation must not create an unacceptable increase in false change/adaptation events.

Exact numerical margins must be frozen only after the current metric definitions and development variance are recovered from the retained package. They must be fixed before any new untouched confirmatory evidence is evaluated.

## Verification requirements before calling a baseline faithful

For each implementation:

1. cite the exact paper/algorithm or maintained reference package used;
2. add at least one deterministic unit test for a small synthetic case;
3. test limiting behavior against the classical filter where the robustification parameter tends to the non-robust regime, when the method permits this;
4. document every deviation from the reference algorithm;
5. preserve raw per-seed/per-sequence outputs;
6. run the same harness entry point and metric code across all methods.

## Primary references

- Altamirano, M., Briol, F.-X., & Knoblauch, J. (2023). *Robust and Scalable Bayesian Online Changepoint Detection*. ICML / PMLR 202:642–663.
- Fisch, A. T. M., Eckley, I. A., & Fearnhead, P. (2022). *Innovative and Additive Outlier Robust Kalman Filtering With a Robust Particle Filter*. IEEE Transactions on Signal Processing 70:47–56. DOI: 10.1109/TSP.2021.3125136.
- Maintained implementation reference: `RobKF` (CRAN), which exposes classical, AO-robust, IO-robust, and joint AO/IO robust filtering implementations.

## Stop conditions

Stop and record `BLOCKED` rather than improvising if:

- the retained common harness cannot be recovered;
- metric semantics are ambiguous;
- a reference algorithm requires assumptions not satisfied by the common model and no faithful mapping exists;
- implementing the method would require reading protected confirmatory outcomes;
- trajectory provenance is being implicitly treated as resolved when it is not.

This protocol does **not** reopen the protected confirmatory family and does **not** change the negative/mixed IRIS verdict.