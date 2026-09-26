# IRIS Final Status

**As of:** 2026-09-26  
**Source branch baseline:** `main` at `10b61758d7e529538da3b5f64e5540be95940bbb`  
**Research state:** `PROTOCOL_BLOCKED_ON_CANONICAL_RAW_TRAJECTORY_PROVENANCE`

## Executive status

IRIS is **not submission-ready as a positive mechanism result**.

The retained evidence boundary is mixed/negative:

- the scalar heavy-tail advantage did not transfer to the learned recurrent pilot;
- the tested PABIM mechanism did not beat the strongest retained Huber/static robust controls in the learned-sequence gate;
- the common adaptation harness verdict is `NEGATIVE_OR_INCONCLUSIVE_DEVELOPMENT_GATE`;
- protected confirmatory experiment IDs `1000–1029` remain closed;
- canonical raw-trajectory provenance remains unresolved.

This file does not authorize new experiments.

## What is verified in-repository

- `RESEARCH_TRUTH.md` records the retained archive hashes and the negative/mixed evidence boundary.
- `ROBUST_BASELINE_PROTOCOL.md` freezes the admissible next baseline families and stop conditions.
- The executable baseline module currently implements only:
  - B0 classical linear-Gaussian filter;
  - B1 fixed-Huber robust filter.
- The test suite includes a fail-closed check for protected experiment ID 1000 and deterministic development generation.

## What is incomplete

1. Canonical raw-trajectory provenance is unresolved.
2. Faithful B2 AO-robust, B3 IO-robust, B4 joint AO/IO, and B5 robust BOCPD baselines are not implemented in the current code.
3. The exact numerical falsification margins required by the robust-baseline protocol are not frozen because the current metric semantics/development variance have not yet been recovered.
4. No protected confirmatory experiment is authorized.
5. Current CI status for this closeout branch is `UNVERIFIED` until GitHub Actions reports it.

## Admissible next work

- resolve canonical trajectory provenance from retained manifests/evidence;
- implement and test faithful strong robust baselines on development-only IDs;
- recover metric semantics and development variance;
- pre-freeze exact decision margins before any untouched evidence is evaluated.

## Prohibited interpretations

Do not claim:

- positive IRIS mechanism validation;
- superiority to robust BOCPD / AO / IO filtering baselines;
- external temporal generalization;
- state-of-the-art performance;
- submission readiness.

