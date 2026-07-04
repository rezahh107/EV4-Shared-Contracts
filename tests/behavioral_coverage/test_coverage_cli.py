from __future__ import annotations

from pathlib import Path

from ev4_transition.cli import main

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/behavioral-coverage/behavioral-coverage.v1.schema.json"
FIXTURES = ROOT / "tests/fixtures/behavioral_coverage"


def test_coverage_cli_returns_2_when_source_missing_or_unparseable(tmp_path, capsys):
    missing = tmp_path / "missing.json"
    assert main(["coverage", "validate", str(missing), "--schema", str(SCHEMA)]) == 2
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    assert main(["coverage", "validate", str(bad), "--schema", str(SCHEMA)]) == 2


def test_coverage_cli_returns_2_when_schema_unreadable_or_invalid(tmp_path, capsys):
    source = FIXTURES / "valid/critical_rule_fixture_tested.json"
    schema_dir = tmp_path / "schema-dir"
    schema_dir.mkdir()
    assert main(["coverage", "validate", str(source), "--schema", str(schema_dir)]) == 2
    invalid_schema = tmp_path / "invalid-schema.json"
    invalid_schema.write_text('{"type": 123}', encoding="utf-8")
    assert main(["coverage", "validate", str(source), "--schema", str(invalid_schema)]) == 2
    output = capsys.readouterr().out
    assert "Traceback" not in output
    assert "PG_BRC_SOURCE_UNPARSEABLE" in output


def test_coverage_cli_returns_1_when_thresholds_fail(capsys):
    source = FIXTURES / "invalid/critical_rule_prose_only.json"
    assert main(["coverage", "validate", str(source), "--schema", str(SCHEMA)]) == 1


def test_coverage_cli_returns_0_when_thresholds_met(capsys):
    source = FIXTURES / "valid/critical_rule_fixture_tested.json"
    assert main(["coverage", "validate", str(source), "--schema", str(SCHEMA)]) == 0


def test_coverage_cli_inspect_returns_0_for_parseable_source(capsys):
    source = FIXTURES / "valid/critical_rule_fixture_tested.json"
    assert main(["coverage", "inspect", str(source), "--schema", str(SCHEMA)]) == 0
