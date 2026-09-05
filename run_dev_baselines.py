from __future__ import annotations

import argparse

from iris_baselines import LinearGaussianModel, RunConfig, run_development, write_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run IRIS development-only B0/B1 baselines")
    parser.add_argument("--experiment-id", type=int, required=True)
    parser.add_argument("--scenario", choices=["clean", "additive_outlier", "persistent_shift", "false_open", "mixed"], required=True)
    parser.add_argument("--length", type=int, default=200)
    parser.add_argument("--huber-c", type=float, default=1.5)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    cfg = RunConfig(
        experiment_id=args.experiment_id,
        scenario=args.scenario,
        length=args.length,
        huber_c=args.huber_c,
    )
    result = run_development(cfg, LinearGaussianModel())
    write_result(result, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
