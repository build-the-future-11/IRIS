# IRIS Reproducibility

## Evidence boundary

Reproducibility claims in this repository are limited to the retained evidence documented in `RESEARCH_TRUTH.md`.

The retained audit reports:

- byte-identical reproduction of the EXP-004 scalar-v2 numerical payload;
- numerical reproduction of EXP-003 learned-sequence v2 within floating-point-scale deltas with unchanged negative scientific verdict;
- a development-only common adaptation harness with seeds 0–9 and 720 retained raw rows whose frozen verdict was independently reproduced.

The canonical observation/state trajectory corpus required by the frontier protocol has **not** been proven by a separately retained trajectory artifact. Therefore the frontier remains blocked.

## Current executable development baseline

The top-level development harness consists of:

- `iris_baselines.py`
- `run_dev_baselines.py`
- `tests/test_baselines.py`

The current implementation covers only B0 classical and B1 fixed-Huber baselines.

### Local verification commands

```bash
python -m pip install ".[test]"
python -m pip check
pytest -q

python run_dev_baselines.py --experiment-id 31 --scenario clean --output out/clean.json
python run_dev_baselines.py --experiment-id 32 --scenario additive_outlier --output out/additive.json
python run_dev_baselines.py --experiment-id 33 --scenario persistent_shift --output out/shift.json
python run_dev_baselines.py --experiment-id 34 --scenario false_open --output out/false_open.json
python run_dev_baselines.py --experiment-id 35 --scenario mixed --output out/mixed.json
```

### Protected-family guardrail

This command must fail closed:

```bash
python run_dev_baselines.py --experiment-id 1000 --scenario clean --output out/forbidden.json
```

Expected behavior: a `ValueError` indicating that the protected confirmatory experiment ID is closed.

## Current run status

No new experiment was executed as part of this closeout documentation change.

- New scientific results: `NOT RUN`
- Closeout-branch CI: `UNVERIFIED`
- Protected confirmatory family: `CLOSED`

