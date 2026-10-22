# IRIS branch integration engineering contract — 2026-10-22

Declared before any local execution at 2026-10-22 12:12:39 UTC.

## Scope and stopping rule

Integrate the exact reviewed numerical and imported-source-identity implementation from PR 11 head d37a2fe5c240d06fdf020caac37b839258827411 with the exact strict replay CLI and seven existing regressions from PR 9 head 4dd3aa70633c88a7e8aa2e2fe56bc4806538daa8. PR 10 head beb6648da764bf580aa9e1d23562fb28de4c59cc is already an ancestor of PR 11. Main 2dbc623edbaf059643974d1c1fa352c438978954 is already an ancestor of PR 11. Preserve both branch heads as integration commit parents. Do not alter numerical algorithms, thresholds, tests, dependency constraints or CI gates.

One local complete existing correctness suite command is authorized, with a 120 second process limit, one numerical thread, no plugin autoload and no installed packages. Expected count: 172 existing PR 11 cases plus seven PR 9 strict CLI cases = 179. The command uses pytest -q -W error -p no:cacheprovider. Capture exact stdout, stderr, return code, elapsed time, runtime versions and pre/post source digests. Preserve any failure and stop after this command; no repeat to obtain a positive result.

The existing tests use bounded constructed regressions and temporary development records; no new fixtures or scientific sample families are introduced. Existing ordinary record fixtures use at most 80 observations. Source-identity temporary-copy cases use at most eight observations. Tests for all 30 protected IDs reject before generation; invalid configuration inputs reject before generation. No historical raw record will be regenerated or rewritten.

The final new-head hosted workflow remains required, unchanged. Its existing five development-only CLI smoke records use IDs 31–35 and 200 observations each, followed by a rejection check for protected ID 1000. These are bounded engineering checks, not scientific evidence or a reopened study.

## Protected boundaries

Scientific runs: zero. Paid compute, provider calls, training campaigns and protected evaluation runs: zero. Protected confirmatory IDs 1000–1029 remain closed. The retained mixed/negative evidence line remains closed; canonical raw trajectory provenance remains unresolved. Original records must replay against their recorded original source. The combined numerical implementation has a different source digest and must not relabel old records.

All prior development budgets, negative findings, source-identity counterexamples and closed sessions remain unchanged. This contract authorizes one separate integration correctness command only. Successful engineering integration does not establish scientific superiority, recover historical provenance, implement B4/B5, or promote any research claim.
