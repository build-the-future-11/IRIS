# IRIS Results Manifest

This manifest distinguishes retained scientific evidence from the current development-only baseline code.

| Result / artifact | Evidence role | Status | Notes |
|---|---|---|---|
| EXP-004 scalar-v2 payload | retained research evidence | REPRODUCED | Byte-identical according to `RESEARCH_TRUTH.md`. |
| EXP-003 learned-sequence v2 | retained research evidence | REPRODUCED_NEGATIVE | Reproduced within floating-point-scale deltas; verdict unchanged. |
| Common adaptation harness, seeds 0–9 | development evidence | REPRODUCED_NEGATIVE | 720 retained raw rows; verdict `NEGATIVE_OR_INCONCLUSIVE_DEVELOPMENT_GATE`. |
| B0 classical filter | current development code | IMPLEMENTED | Implemented in `iris_baselines.py`. |
| B1 fixed-Huber filter | current development code | IMPLEMENTED | Implemented in `iris_baselines.py`. |
| B2 AO-robust filter | planned development baseline | NOT_IMPLEMENTED | Must follow a faithful published AO-robust formulation. |
| B3 IO-robust filter | planned development baseline | NOT_IMPLEMENTED | Must remain conceptually distinct from AO robustness. |
| B4 joint AO/IO filter | planned development baseline | NOT_IMPLEMENTED | CE-BASS family is admissible per protocol. |
| B5 robust BOCPD | planned development baseline | NOT_IMPLEMENTED | Must preserve run-length/changepoint posterior semantics. |
| Confirmatory IDs 1000–1029 | protected confirmatory evidence | NOT_RUN / CLOSED | Execution prohibited while the frontier is blocked. |

## Scientific verdict

The supported verdict remains **mixed/negative**. Nothing in the current development baseline code changes the retained negative result.

