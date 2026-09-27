# IRIS B2/B3 Robust-Filter Implementation Notes

**Date:** 2026-09-27  
**Scope:** development-only baseline engineering. Protected confirmatory experiment IDs `1000-1029` remain closed.

## Purpose

This note records exactly how B2 and B3 in `iris_baselines.py` map to the maintained RobKF implementation required by `ROBUST_BASELINE_PROTOCOL.md`. It does not establish that canonical IRIS trajectory provenance has been recovered, and it does not authorize a confirmatory run.

## Pinned reference implementation

Repository: `Fisch-Alex/Robkf`  
Pinned commit: `0c4287545034bace38b1e8fb795726add61032b5`

Relevant maintained files at that commit:

- `R/AORKF_huber.R`
- `src/aorkf_huber_list.cpp`
- `src/aorkf_huber_matrix.cpp`
- `R/IORKF_huber.R`
- `src/iorkf_huber_list.cpp`
- `src/iorkf_huber_matrix.cpp`

The R wrappers describe the AO and IO filters as Huberisation-based robust Kalman filters and pass each observation through the corresponding C++ update. The scalar IRIS implementation follows the update equations in the two `*_matrix.cpp` files.

## Common scalar Kalman terms

For scalar state (x_t), observation (y_t), transition (A), observation map (C), process variance (Q), and observation variance (R):

[
m^-_t = A m_{t-1},
qquad
P^-_t = A^2 P_{t-1} + Q,
]

[

u_t = y_t - C m^-_t,
qquad
K_t = rac{P^-_t C}{C^2 P^-_t + R}.
]

Both B2 and B3 keep the same covariance update used by the pinned RobKF source:

[
P_t = (1-K_t C)P^-_t.
]

## B2: AO-robust Huber filter

The pinned `aorkf_huber_matrix.cpp` first computes the ordinary Kalman state correction

[
u_t = K_t
u_t
]

and clips its Euclidean norm at threshold (h_{mathrm{AO}}). In one dimension this is exactly

[
psi_h(u)=
egin{cases}
u, & |u|le h,\\
h,operatorname{sign}(u), & |u|>h.
end{cases}
]

The state update is therefore

[
m_t = m^-_t + psi_{h_{mathrm{AO}}}(K_t
u_t).
]

This is intentionally **not** the same algorithm as the historical B1 control. B1 clips a standardized observation residual before multiplying by the Kalman gain; B2 clips the resulting state correction, matching the maintained AO implementation.

Default development threshold: `ao_h=2.0`, matching the maintained RobKF wrapper default.

## B3: IO-robust Huber filter

The pinned `iorkf_huber_matrix.cpp` computes

[
v_t = (1-CK_t)
u_t
]

and clips that component at (h_{mathrm{IO}}). For scalar nonzero (C),

[
m_t
=
m^-_t
+
C^{-1}left[

u_t-psi_{h_{mathrm{IO}}}ig((1-CK_t)
u_tig)
ight].
]

This is behaviorally different from AO robustness. Under a large isolated measurement spike, AO can suppress the state correction. IO robustness instead treats a sufficiently large unexplained residual component as potential latent/process innovation and can follow the observation much more aggressively.

Default development threshold: `io_h=2.0`, matching the maintained RobKF wrapper default.

## Faithfulness checks encoded in tests

The test suite requires:

1. both B2 and B3 converge numerically to the classical Kalman filter as (h	oinfty);
2. B2 clips the scalar state correction exactly;
3. B2 and B3 react differently to a large observation in the direction implied by their respective update equations;
4. all result manifests retain the pinned upstream commit;
5. protected confirmatory experiment IDs still fail closed.

## Deliberate scope limitation

This is a scalar translation because the current IRIS common development harness is scalar. It should not be represented as a general matrix reimplementation of RobKF.

B4 joint AO/IO filtering and B5 robust BOCPD remain unimplemented by this change. They require their own faithful reference mapping and tests. No placeholder approximation is substituted for either method.

## Scientific boundary

This branch changes baseline code and unit tests only. It does not:

- recover canonical raw-trajectory provenance;
- execute or inspect protected experiment IDs `1000-1029`;
- change the retained mixed/negative IRIS result;
- freeze numerical victory margins;
- establish superiority over B2/B3;
- establish submission readiness.

Any later development result using B2/B3 must be labeled development-only and retained with generator/config/seed/dependency provenance.
