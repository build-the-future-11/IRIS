# IRIS project state

## Scientific authority

`RESEARCH_TRUTH.md` remains the authority for the retained mixed/negative
findings and unresolved canonical trajectory provenance.
`ROBUST_BASELINE_PROTOCOL.md` remains the development-only baseline contract.
Protected confirmatory experiment IDs 1000–1029 are closed. B4 and B5 and the
canonical-corpus recovery remain incomplete; no positive mechanism or
submission-readiness claim follows from this engineering work.

## Engineering session — 10 October 2026

Default branch inspected: `2dbc623edbaf059643974d1c1fa352c438978954`.
This change builds on open PR #10 at
`0135c80eb751ea5eabfd1f048e33d0fc30d76c4a`, itself stacked on #9, so the existing
numerical and replay repairs are retained rather than duplicated.

The remaining state-correction underflow defect is repaired in the shared
scalar implementation. The initial 40 regression cases exposed 32 failures and
eight passing controls; four additional cases cover actual AO and B1 clipping.
The full suite and exact source-revision comparison are recorded in the draft
PR. `DEVELOPMENT_RECORDS.md` describes the algebra and replay boundary.

The admissible next steps remain review and integration of the stacked code
changes, recovery of canonical trajectory provenance, and faithful development
baseline work under the existing protocol. Frozen evidence is unchanged.
