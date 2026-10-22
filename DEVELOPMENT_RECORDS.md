# Scalar development records and numerical stability

## Scope

The `iris.scalar_baselines.development.v2` record retains the full state and
observation sequence, every baseline's per-step output, summary metrics,
generator/configuration/trajectory hashes, seed recipe, PRNG identity, pinned
baseline references and environment. These are new scalar development inputs.
They do not recover the historical canonical IRIS trajectory corpus or change
the mixed/negative finding recorded in `RESEARCH_TRUTH.md`.

Experiment IDs 1000–1029 remain closed. The API rejects noninteger or negative
experiment IDs before random-number generation. Configurations, observations
and outputs must be finite; JSON publication refuses nonfinite numbers.

## Numerical repairs

For scalar predicted variance `P`, observation map `C`, measurement variance
`R`, and innovation variance `S = C*C*P + R`, the posterior variance is now
computed as `P*R/S` with binary exponent scaling. This is algebraically
identical to `(1-K*C)*P` but avoids cancellation when `K*C` rounds to one
and premature underflow when the intermediate fraction `R/S` is below the
float64 range. The same repair is applied to B0, B1, B2 and B3.

The IO residual component uses the same scaled product for `R*innovation/S`.
Its correction is `K*innovation + (component-clipped_component)/C`. This preserves
the classical-filter limit when `C` is very small. The update equations remain
the scalar RobKF mapping documented in `BASELINE_IMPLEMENTATION_NOTES.md`;
no new robust-filter mechanism is introduced.

The AO correction clips directly to the signed threshold instead of multiplying
by a weight that may have underflowed to zero. The B1 Huber correction similarly
uses the clipped residual magnitude. A representable clipped update is retained
even when its ratio to the unbounded correction is too small to represent.
The recorded multiplicative weight may still round to zero in that case.

The additional regressions check independent 100-digit decimal calculations,
signed extreme clipping and genuine unrepresentable-output rejection. The
development generator and protected experiment-ID policy are unchanged.

### State-correction underflow follow-up — 10 October 2026

PR #10's binary-scaled gain repair preserves an underflowing gain numerator.
The gain itself can still underflow before multiplication by the innovation.
For example, `P=2e-200`, `C=1e-100`, `R=1e100` and innovation
`1e100` have a representable correction near `2e-300`, although `K` alone is
below the float64 range. Computing `K * innovation` had silently returned zero
in B0/B1/B2 and the unclipped B3 limit.

Building on that gain repair, when the gain or correction is subnormal, the
state update combines `P*C*innovation/S` before its final
binary scaling. Ordinary normal-range corrections retain the original
multiplication order. The same helper is used by every baseline, including
the effective clipped B1 innovation and the AO correction before clipping.

`tests/test_scaled_state_corrections.py` compares all four baseline limits with
200-digit Decimal arithmetic for both signs and both underflow mechanisms. It
also checks the robust clipped cases and genuine zero-rounding controls. These
are arithmetic regressions, not new scientific scenarios or success criteria.
The source hash changes; earlier retained records still require their exact
recorded source revision and are not rewritten.

RMSE and MAE use max-error scaling so finite errors such as `1e200` do not
overflow merely because they are squared or summed. Mismatched array lengths
are rejected rather than broadcast. Arithmetic outside the representable
positive/finite domain raises an error instead of publishing invalid evidence.

## Execute and verify

```bash
python run_dev_baselines.py --experiment-id 41 --scenario mixed --length 32 --output /tmp/iris-mixed-v2.json
python verify_dev_record.py /tmp/iris-mixed-v2.json
python -m pytest -q
```

Publication is atomic and refuses to replace an existing path. Use a new
destination for another attempt. The verifier requires the exact generator
implementation hash and regenerates the development input and all four
baseline outputs, then checks raw values and metrics. Exact replay may require
the recorded NumPy version; a mismatch is not permission to rewrite evidence.
Source revisions containing a numerical repair have a new implementation hash.
Replay the pre-repair records with their original source revision; the retained
files are not regenerated or overwritten to make the new code match old hashes.

The five files under `development/20261010/` exercise the pre-existing scenario
matrix at development ID 41 and length 32. They are engineering smoke records,
with all baseline outcomes retained. No hypothesis selection, statistical
victory margin, confirmatory execution or architecture-superiority claim is
derived from them.

## 22 October 2026 integration of the strict replay parser

The following historical appendix is retained verbatim from PR #9 head
`4dd3aa70633c88a7e8aa2e2fe56bc4806538daa8`. Its 113-test count and statement that
the scientific implementation was unchanged refer to that earlier branch only.
The integrated implementation retains PR #11's later numerical and source-identity
repairs. Its source hash differs from the original development records; those
records still require their recorded original source and are not rewritten.

## 10 October 2026 follow-up: strict replay input

The replay CLI now rejects duplicate object keys at any depth, nonstandard
NaN/Infinity constants, exponent overflow such as `1e999`, and a non-object
record before replay begins. This prevents a JSON parser's last-key-wins rule
from selecting one of two conflicting configuration or experiment identities.
The success receipt includes the SHA-256 of the exact byte snapshot parsed.
Inputs remain read-only and the scientific `iris_baselines.py` implementation is
unchanged, so its five source-bound development records still replay exactly.

Seven new CLI cases failed before the correction; all 113 repository tests now
pass locally. The five retained scenario files were separately verified through
the actual CLI, each reporting its original input hash. Duplicate protected IDs
are rejected before replay; IDs 1000–1029 remain closed. This is parsing and
traceability validation, not a new filter result or canonical-provenance repair.

The integration combines the exact strict CLI and seven original CLI regressions
with the exact PR #11 core and its 172 existing cases. One predeclared local
correctness command passed all 179 cases with warnings treated as errors; source
and evidence bytes remained unchanged. The local budget is closed. The unchanged
hosted workflow must pass on the new integration head before merge. See
`research/GITHUB_INTEGRATION_REVIEW_20261022.md` for ancestry, receipts and limits.
