"""Live-process source drift cannot relabel already imported numerical code."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

import iris_baselines


@pytest.fixture
def isolated(tmp_path):
    source = tmp_path / "iris_source_copy.py"
    source.write_bytes(Path(iris_baselines.__file__).read_bytes())
    name = "_isolated_iris_source_identity"
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        yield module, source
    finally:
        sys.modules.pop(name, None)


def run(module):
    return module.run_development(module.RunConfig(41, "mixed", length=8))


def change(source):
    source.write_bytes(source.read_bytes() + b"\n# persistent source drift after import\n")


def test_changed_source_is_rejected_before_any_generator_call(isolated, monkeypatch):
    module, source = isolated
    change(source)
    calls = []
    original = module.generate_sequence

    def traced(*args):
        calls.append(True)
        return original(*args)

    monkeypatch.setattr(module, "generate_sequence", traced)
    with pytest.raises(ValueError, match="source.*fresh interpreter"):
        run(module)
    assert not calls


def test_source_changed_during_execution_cannot_release_a_mislabeled_result(isolated, monkeypatch):
    module, source = isolated
    original = module.summarize

    def changed_summary(*args):
        result = original(*args)
        change(source)
        return result

    monkeypatch.setattr(module, "summarize", changed_summary)
    with pytest.raises(ValueError, match="source.*fresh interpreter"):
        run(module)


def test_same_process_verifier_cannot_certify_relabeling_to_new_file_bytes(isolated):
    module, source = isolated
    record = run(module)
    change(source)
    record["generator"]["implementation_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="source.*fresh interpreter"):
        module.verify_development_record(record)


def test_missing_source_is_an_explicit_identity_failure(isolated):
    module, source = isolated
    source.unlink()
    with pytest.raises(ValueError, match="source.*fresh interpreter"):
        run(module)


def test_unchanged_import_keeps_exact_numerical_and_replay_results(isolated):
    module, source = isolated
    expected = run(iris_baselines)
    observed = run(module)
    assert observed == expected
    assert observed["generator"]["implementation_sha256"] == hashlib.sha256(
        source.read_bytes()
    ).hexdigest()
    assert module.verify_development_record(observed)["status"] == "VERIFIED_DEVELOPMENT_REPLAY"
    assert module.verify_development_record(observed)["canonical_provenance_resolved"] is False
