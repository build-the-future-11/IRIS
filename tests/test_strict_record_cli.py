"""The exact-replay CLI must reject ambiguous or nonstandard JSON evidence."""
import hashlib
import json

import pytest

from iris_baselines import RunConfig, run_development
import verify_dev_record


def invoke(path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["verify_dev_record", str(path)])
    return verify_dev_record.main()


def test_successful_cli_receipt_binds_the_exact_input_bytes(tmp_path, monkeypatch, capsys):
    path = tmp_path / "development.json"
    path.write_text(json.dumps(run_development(RunConfig(51, "clean", length=8)), indent=3) + "\n")
    before = path.read_bytes()
    assert invoke(path, monkeypatch) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["input_sha256"] == hashlib.sha256(before).hexdigest()
    assert result["status"] == "VERIFIED_DEVELOPMENT_REPLAY"
    assert path.read_bytes() == before


@pytest.mark.parametrize("kind", ["duplicate", "nested_duplicate", "nan", "inf", "overflow", "array"])
def test_ambiguous_or_nonstandard_json_is_rejected_before_replay(tmp_path, monkeypatch, kind):
    record = run_development(RunConfig(51, "clean", length=8))
    content = json.dumps(record)
    if kind == "duplicate":
        content = content.replace('"schema":', '"schema":"forged", "schema":', 1)
    elif kind == "nested_duplicate":
        content = content.replace('"experiment_id":', '"experiment_id":1000, "experiment_id":', 1)
    elif kind == "array":
        content = "[]"
    else:
        value = {"nan": "NaN", "inf": "Infinity", "overflow": "1e999"}[kind]
        content = content[:-1] + ', "extra":' + value + '}'
    path = tmp_path / "ambiguous.json"
    path.write_text(content)
    monkeypatch.setattr(verify_dev_record, "verify_development_record", lambda *a: pytest.fail("invalid JSON reached replay"))
    with pytest.raises(SystemExit) as raised:
        invoke(path, monkeypatch)
    assert raised.value.code == 2
    assert path.read_text() == content
