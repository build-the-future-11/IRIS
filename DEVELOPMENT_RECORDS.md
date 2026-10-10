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
