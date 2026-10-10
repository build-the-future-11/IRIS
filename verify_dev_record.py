"""Replay a complete IRIS development-only record without writing results."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from iris_baselines import verify_development_record


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("JSON number exceeds the finite float64 range")
    return number


def _reject_constant(value):
    raise ValueError(f"nonstandard JSON numeric constant: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        content = args.record.read_bytes()
        record = json.loads(content, object_pairs_hook=_unique_object,
                            parse_constant=_reject_constant, parse_float=_finite_float)
        if not isinstance(record, dict):
            raise ValueError("development record must be a JSON object")
        result = verify_development_record(record)
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    result["input_sha256"] = hashlib.sha256(content).hexdigest()
    print(
        json.dumps(result, sort_keys=True, allow_nan=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
