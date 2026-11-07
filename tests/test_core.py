import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import core

POD = (pathlib.Path(__file__).parents[1] / "samples/pod.yaml").read_text()


def fake_scanner(content, kind):
    return [{"check_id": "CKV_K8S_16", "name": "privileged", "resource": "Pod.demo", "lines": [1, 2]}] if "privileged: true" in content else []


def make_llm(fixed):
    return lambda prompt: json.dumps({"explanations": [{"check_id": "CKV_K8S_16", "plain_english": "x", "risk": "y", "fix_summary": "z"}], "fixed_file": fixed})


def test_detect_kind():
    assert core.detect_kind("a.tf", "") == "terraform"
    assert core.detect_kind("a.yml", "") == "kubernetes"


def test_verified_fix():
    r = core.analyse(POD, "pod.yaml", llm=make_llm(POD.replace("true", "false")), scanner=fake_scanner)
    assert r["verdict"].startswith("verified") and r["fixed_ids"] == ["CKV_K8S_16"]


def test_invalid_fix_rejected():
    r = core.analyse(POD, "pod.yaml", llm=make_llm("::: not yaml ["), scanner=fake_scanner)
    assert r["verdict"].startswith("rejected")


def test_partial_fix():
    r = core.analyse(POD, "pod.yaml", llm=make_llm(POD), scanner=fake_scanner)
    assert r["verdict"].startswith("partial")


def test_clean_file_skips_llm():
    def boom(p): raise AssertionError("LLM should not be called")
    assert core.analyse("apiVersion: v1\nkind: Pod\n", "p.yaml", llm=boom, scanner=fake_scanner)["verdict"] == "clean"


def test_too_large():
    import pytest
    with pytest.raises(ValueError):
        core.analyse("x" * 20000, "a.tf")


def test_real_checkov_finds_privileged():
    ids = {f["check_id"] for f in core.scan(POD, "kubernetes")}
    assert "CKV_K8S_16" in ids


def test_flask_index():
    import app
    assert app.app.test_client().get("/").status_code == 200
