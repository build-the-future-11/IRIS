# IRIS — Research Truth

**Recovered:** 2026-08-30  
**State:** `PROTOCOL_BLOCKED_ON_CANONICAL_RAW_TRAJECTORY_PROVENANCE`

This file is a truth-first recovery marker for the IRIS repository. It does not create new experimental evidence and does not authorize the reserved confirmatory experiment family.

## Verified retained archive identities

The following Library archives were recovered and independently SHA-256 checked during repository recovery:

- `IRIS_v0.2_bundle.zip` — `41a8e117b6922c3a6641bd12608d5e4246d305a9c3776a62252869045d83dacf`
- `IRIS_v0.2_research_package(1).zip` — `5d689ade164d80216d0ab6d4376b8acf53b8e0ba13d4bd5e909a94f00ec86b56`
- `IRIS_v0.2_repro_addendum_20260813.zip` — `7653c87d5effb08da9068630259802d77b34b930083dd160ccea4ce23311175b`
- `IRIS_common_adaptation_harness_v1_negative_20260813.zip` — `5643b59e9272099e54f04491aa63906d0d186a1a2c525a574f960008e5f19b90`

These hashes match the retained provenance cross-hash audit.

## Supported evidence boundary

### Reproduced / retained

- The v0.2 release package contains the scalar and learned-sequence experiment runners, raw result tables, manifests, paper source, research freeze, evidence ledger, tests, and checksum manifest.
- The reproducibility addendum records `4 passed` for the retained package tests.
- EXP-004 scalar-v2 numerical payload was reproduced byte-identically in the retained reproducibility audit.
- EXP-003 learned-sequence v2 was reproduced numerically within floating-point-scale deltas; the negative scientific verdict was unchanged.
- A development-only common adaptation harness used seeds `0–9`, retained 720 raw rows, and independently reproduced its frozen negative verdict.

### Negative / falsified

- The scalar HTAM heavy-tail advantage did **not** transfer to the learned recurrent pilot.
- The tested PABIM mechanism did **not** beat the strong Huber/static robust controls in the learned-sequence gate.
- In the common adaptation harness, PABIM passed clean non-inferiority, a limited heavy-tail information-gain gate, and the false-open guardrail, but failed the strong-fixed-robust-control guardrail and the persistent-shift gate.
- The retained common-harness verdict is `NEGATIVE_OR_INCONCLUSIVE_DEVELOPMENT_GATE`.

### Not established

IRIS currently does **not** establish:

- external real-world temporal generalization;
- superiority to faithful robust BOCPD / generalized-Bayes / AO-IO filtering baselines;
- GRU/LSTM/SSM superiority;
- a positive architecture/mechanism contribution;
- state-of-the-art performance;
- broad novelty over robust filtering and changepoint literature;
- submission readiness.

## Protected confirmatory family

The planned final confirmatory **experiment IDs** `1000–1029` remain unevaluated in the retained evidence ledger and MUST NOT be executed while the frontier protocol remains blocked.

Historical development code did use some numerically overlapping derived RNG values internally (for example `1000 + seed` while outer experiment IDs were `0–4`). Therefore do not make the broader and inaccurate claim that the integers 1000–1029 never appeared in any RNG call.

## Current blocker

The retained provenance audit did not locate a separately stored canonical observation/state trajectory corpus. Deterministic runner/source hashes are useful lineage evidence, but they do not by themselves prove the exact canonical input identity required by the frontier protocol.

Therefore:

1. do not regenerate approximate trajectories and relabel them canonical;
2. do not open the protected confirmatory experiment family;
3. search retained manifests/evidence for an explicit trajectory identity defined by generator source hash + config hash + exact outer seed list + dependency/PRNG version;
4. if that record cannot be recovered, keep the frontier blocked and treat v0.2 as a mixed/negative research package.

## Next admissible scientific work

Before designing another named IRIS mechanism:

- recover/resolve canonical trajectory provenance;
- implement faithful strong change-aware robust baselines in the common learned harness;
- use development-only data/seeds for any successor design;
- freeze a new falsifier before touching any untouched confirmatory evidence;
- add external temporal datasets only after the source/protocol boundary is sound.

**Do not rescue a negative result by renaming the mechanism.**
