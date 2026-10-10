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
computed as `P * (R / S)`. This is algebraically identical to `(1-K*C)*P`
but avoids cancellation when `K*C` rounds to one. The same repair is applied
to B0, B1, B2 and B3.

The IO residual component uses `(R/S)*innovation`, and its correction is
computed as `K*innovation + (component-clipped_component)/C`. This preserves
the classical-filter limit when `C` is very small. The update equations remain
the scalar RobKF mapping documented in `BASELINE_IMPLEMENTATION_NOTES.md`;
no new robust-filter mechanism is introduced.

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

The five files under `development/20261010/` exercise the pre-existing scenario
matrix at development ID 41 and length 32. They are engineering smoke records,
with all baseline outcomes retained. No hypothesis selection, statistical
victory margin, confirmatory execution or architecture-superiority claim is
derived from them.

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
