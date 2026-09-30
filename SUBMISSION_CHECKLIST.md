# IRIS Submission Checklist

**Current decision:** `NOT READY FOR POSITIVE-MECHANISM SUBMISSION`

## Research truth

- [x] Retained archive hashes recorded.
- [x] Mixed/negative evidence boundary recorded.
- [x] Protected confirmatory IDs 1000–1029 explicitly closed.
- [ ] Canonical raw-trajectory provenance resolved.
- [ ] Exact trajectory identity bound to generator source + config + outer IDs/seeds + dependency/PRNG versions.

## Baselines

- [x] B0 classical baseline implemented.
- [x] B1 fixed-Huber baseline implemented.
- [ ] B2 faithful AO-robust baseline implemented and tested.
- [ ] B3 faithful IO-robust baseline implemented and tested.
- [ ] B4 faithful joint AO/IO baseline implemented and tested.
- [ ] B5 faithful robust BOCPD baseline implemented and tested.
- [ ] Every algorithm deviation from its reference documented.

## Protocol and statistics

- [x] Development-only protocol documented.
- [x] Stop conditions documented.
- [ ] Metric semantics recovered and frozen.
- [ ] Development variance recovered.
- [ ] Numerical falsification margins pre-frozen.
- [ ] No tuning uses protected confirmatory outcomes.

## Reproducibility

- [x] Local verification commands documented.
- [ ] Closeout-branch CI verified green.
- [ ] Raw per-seed/per-sequence outputs retained for all implemented strong baselines.
- [ ] Environment/dependency identities retained for every comparison.

## Paper / claims

- [x] Positive mechanism claim currently blocked.
- [x] State-of-the-art claim currently unsupported.
- [x] External temporal generalization claim currently unsupported.
- [ ] Every manuscript table and figure bound to an immutable evidence artifact.
- [ ] References and algorithm attributions independently checked.

## Submission gate

Do **not** mark submission-ready until every unchecked item required by the intended claim is resolved.

A negative-results or research-audit writeup may be considered separately, but it must preserve the mixed/negative verdict and clearly state the unresolved provenance boundary.
