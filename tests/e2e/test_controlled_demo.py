from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_controlled_demo_files_exist():
    for relative in [
        "scripts/run-project-gate-demo.py",
        "docs/E2E_DEMO_WORKFLOW.md",
        "fixtures/personal-use/sample-valid-stage-bundle.synthetic.json",
        "fixtures/personal-use/sample-insufficient-evidence-stage-bundle.synthetic.json",
    ]:
        assert (ROOT / relative).exists(), relative


def test_controlled_demo_safety_contract_is_documented_in_code_and_docs():
    script = (ROOT / "scripts/run-project-gate-demo.py").read_text(encoding="utf-8")
    doc = (ROOT / "docs/E2E_DEMO_WORKFLOW.md").read_text(encoding="utf-8")

    for token in ["insufficient_evidence", "real_evidence_claimed", "production_readiness_claimed"]:
        assert token in script
    for token in ["insufficient_evidence", "real Elementor validation", "real end-to-end readiness"]:
        assert token in doc
