# IRIS GitHub integration review — 22 October 2026

## Decision and scope

The existing engineering work in PRs #9, #10 and #11 is ready for integration,
subject to independent root review and the unchanged full hosted workflow on
the newly published head. One predeclared local command passed all **179**
existing cases with warnings treated as errors (0.34 seconds reported by pytest;
0.6172168709963444 seconds process time). No source or historical evidence file
changed during that command. Raw stdout, stderr, JUnit and structured receipt
are retained under `research/integration_20261022/`.

This is an engineering integration. The mixed/negative research outcome remains
retained; canonical raw trajectory provenance remains unresolved.
`research_complete` stays false. IDs1000–1029 remain closed. No scientific
experiment, protected evaluation, training campaign, provider call or paid
computation was performed. No old development budget is reopened.

## Exact source and complete branch ancestry

Main: `2dbc623edbaf059643974d1c1fa352c438978954`.

PR #11: `d37a2fe5c240d06fdf020caac37b839258827411`, actual Git tree
`5995674658792eb4cbe9ed4ed9bdf63b09862314`.

PR #10: `beb6648da764bf580aa9e1d23562fb28de4c59cc` is an ancestor of #11
(ahead3/behind0; exact merge base #10). Main is also an ancestor of #11
(ahead6/behind0; exact merge base main).

PR #9: `4dd3aa70633c88a7e8aa2e2fe56bc4806538daa8`, actual Git tree
`a4186ce6a0255d3b4b8876b4047fb9a1f6e5c92a`, has one additional
commit after common ancestor `5943f7b7c135bd83e22d5cc1df5ba0a07c955e9a`.
PR #9 and #11 diverge ahead5/behind1. That one commit changes exactly the
strict replay CLI, adds seven existing CLI regression cases and appends a
historical documentation section.

The integration keeps #11's full numerical, source-identity and historical
evidence tree. It imports #9's CLI and new test module byte-for-byte and
preserves #9's documentation appendix with an explicit original-revision
context. The obsolete historical 113-test and unchanged-core statements are
not claims about the integrated revision. The commit must preserve #11 as
first parent and #9 as an additional parent. No branch content is discarded.
The pre-integration import receipt verifies all40 leaf Git blobs and modes;
the original canonical state and #9 development document are retained.

Retarget PR #11 to main before publishing the two-parent checkpoint. Do not use
a skip-CI commit message. After a green new-head merge, prove both #9 and #10
are ancestors of main before closing them as integrated if GitHub has not
already marked them merged.

## Source review

The scalar B0/B1/B2/B3 implementations retain their finite-domain and
fail-closed validation. Binary exponent scaling preserves representable
posterior variance, gain and state corrections without changing normal-range
multiplication order. Direct clipping avoids multiplying by underflowed
weights. The 100- and 200-digit Decimal tests independently check extreme
ranges, signed clipping, classical limits and genuinely unrepresentable
results. The IO and AO scalar algebra was checked against the maintained
RobKF source at pinned commit
`0c4287545034bace38b1e8fb795726add61032b5`:
[AO reference](https://github.com/Fisch-Alex/Robkf/blob/0c4287545034bace38b1e8fb795726add61032b5/src/aorkf_huber_matrix.cpp)
and [IO reference](https://github.com/Fisch-Alex/Robkf/blob/0c4287545034bace38b1e8fb795726add61032b5/src/iorkf_huber_matrix.cpp).
This equation review makes no new statistical-performance claim.

The strict CLI reads one byte snapshot, rejects duplicate keys, NaN/Infinity,
overflowing JSON numbers and non-object roots before replay, hashes that same
snapshot and never writes its input. Source-identity checks run before
generation, after generation and before verifier replay. They detect persistent
post-import source drift; they are not general bytecode attestation or a guarantee
against every transient race. Atomic result publication remains no-clobber.

All172 existing PR #11 cases and the seven exact PR #9 strict-CLI cases were
reviewed. No algorithm, threshold, regression expectation, dependency,
workflow or protected-family policy was changed for integration.

## Verification and boundaries

The prospective contract is
`research/ENGINEERING_INTEGRATION_CONTRACT_20261022.md`.
One120-second maximum local command was consumed and the local budget closed.
The complete suite returned exit0,179passed,0failed,0skipped; all40 imported
source/evidence files retained their pre-test SHA-256. No historical raw record
was regenerated, replayed with a different implementation, or relabelled.

Existing hosted CI remains mandatory: exact source checkout/clean check,
Python3.11 installation and pip check, the full suite, five bounded
development-only smoke records (IDs31–35,200 observations each), and rejection
of protected ID1000. Historical passes on #9/#10 and an earlier #11 head do
not substitute for this new-head gate. No required gate is disabled.

The retained negative/mixed science, canonical trajectory provenance blocker,
unimplemented B4/B5 scope and original raw hashes are unchanged. Engineering
readiness does not imply scientific superiority, historical provenance recovery
or permission for protected evaluation.
