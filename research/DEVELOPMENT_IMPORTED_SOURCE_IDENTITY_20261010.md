# Development source identity across a live module session

Parent: `83e97b1a1e10c3f6f59895312bc20ef4324a08b6` (draft #11).
Record this contract before the new regression witnesses or implementation.

`run_development` currently hashes `__file__` only when constructing the result.
Python executes already imported functions. If the source file changes during a
long-lived process, old functions can produce new records labeled with the new
on-disk source hash; the verifier repeats that error in the same process.

Capture the source-file SHA-256 at import, then require that identity before any
development generator/filter execution and again before releasing a complete
record. The verifier must use the same checked imported identity. The numerical
generator, B0–B3 filters, seeds, methods and estimands remain byte-for-byte outside
the identity/reporting edits. A changed or missing source fails and tells the
caller to use a fresh interpreter with its exact checkout; it is never relabeled
as current merely because the path changed.

Falsifier: a persistent source replacement after import or during execution can
still acquire a development/replay success bearing its different bytes. Positive
control: unchanged source produces exactly the same numerical trajectories,
baseline outputs and metrics and retains the exact imported source hash.

This detects ordinary persistent source drift. It is not a defense against
malicious monkeypatching, forged imports, stale bytecode caches, or a source file
changed and restored between boundary checks. Historical source identities stay
historical; the missing canonical trajectory corpus is not recovered.

Bounded fresh engineering budget: two focused baseline/fixed test commands and
one affected full-suite command, at most 120 command seconds total, one numerical
thread; generated fixtures no longer than 8 observations in each new case. Zero
scientific campaigns, paid compute, or protected experiment IDs 1000–1029. Retain
failures and source-bound receipts. No new numerical performance claim.

## Observed verification

The five new checks produced **four failures and one control pass** on the exact
parent source. Three cases accepted changed source identities; the missing-file
case raised a late filesystem error after execution instead of rejecting source
identity before the generator. The corrected implementation passes **all 172
tests** (five new, 167 inherited), warnings treated as errors. Critical Ruff and
source/docs/state patch whitespace checks pass; raw pytest failure output retains
its original whitespace. Both commands, raw failure/success outputs and
source hashes are retained in `research/verification/imported_source_20261010/`.

Two commands consumed 3.295 command seconds. The unchanged-source control compares
complete generated records between two independently imported copies of the exact
same source. This establishes deterministic replay for the generated fixture,
not recovery of historical raw inputs. No further optional test was run.
