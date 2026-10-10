"""Replay a complete IRIS development-only record without writing results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from iris_baselines import verify_development_record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    with args.record.open(encoding="utf-8") as handle:
        record = json.load(handle)
    print(
        json.dumps(verify_development_record(record), sort_keys=True, allow_nan=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
