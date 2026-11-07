"""MisconfigExplained core: scan -> explain (LLM) -> propose fix -> re-scan to verify."""
import json, os, shutil, subprocess, tempfile, pathlib
import requests
import yaml

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_CHARS = 12000  # keep within Groq free-tier token limits


def detect_kind(filename, content):
    n = (filename or "").lower()
    if n.endswith(".tf"):
        return "terraform"
    if n.endswith((".yaml", ".yml")):
        return "kubernetes"
    return "terraform" if "resource \"" in content else "kubernetes"


def checkov_bin():
    local = pathlib.Path(__file__).parent / ".venv" / "bin" / "checkov"
    return str(local) if local.exists() else (shutil.which("checkov") or "checkov")


def scan(content, kind):
    """Run Checkov on content; return list of failed checks."""
    ext = ".tf" if kind == "terraform" else ".yaml"
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / ("main" + ext)
        p.write_text(content)
        fw = "terraform" if kind == "terraform" else "kubernetes"
        r = subprocess.run([checkov_bin(), "-f", str(p), "--framework", fw, "-o", "json", "--quiet", "--compact"],
                           capture_output=True, text=True, timeout=180)
    out = r.stdout.strip()
    if not out:
        return []
    data = json.loads(out)
    if isinstance(data, list):
        data = data[0] if data else {}
    fails = (data.get("results") or {}).get("failed_checks", []) if isinstance(data, dict) else []
    return [{"check_id": f["check_id"], "name": f.get("check_name", ""), "resource": f.get("resource", ""),
             "lines": f.get("file_line_range")} for f in fails]


def syntax_ok(content, kind):
    """Cheap structural check; Terraform also uses `terraform validate` when installed."""
    if kind == "kubernetes":
        try:
            docs = [d for d in yaml.safe_load_all(content) if d]
            return bool(docs) and all(isinstance(d, dict) and "kind" in d for d in docs), "YAML parses"
        except Exception as e:
            return False, f"YAML error: {e}"
    tf = shutil.which("terraform")
    if not tf:
        return (content.count("{") == content.count("}")), "brace balance only (terraform not installed)"
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, "main.tf").write_text(content)
        i = subprocess.run([tf, "init", "-backend=false", "-input=false"], cwd=d, capture_output=True, text=True, timeout=300)
        if i.returncode:
            return False, "terraform init failed: " + i.stderr[-300:]
        v = subprocess.run([tf, "validate", "-no-color"], cwd=d, capture_output=True, text=True, timeout=120)
        return v.returncode == 0, (v.stdout + v.stderr).strip()[-300:]


PROMPT = """You are a cloud security teacher. The {kind} file below has these Checkov findings:
{findings}
Return ONLY a JSON object with keys:
"explanations": list of {{"check_id", "plain_english" (1-2 sentences a non-expert understands), "risk" (what could go wrong), "fix_summary"}} one per finding,
"fixed_file": the full corrected file. Change only what is needed; do not rename resources or change names, images, ports or replicas.
File:
{content}"""


def groq_llm(prompt):
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY not set")
    r = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {key}"}, timeout=120, json={
        "model": GROQ_MODEL, "temperature": 0, "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}]})
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def analyse(content, filename="input", llm=groq_llm, scanner=scan):
    if len(content) > MAX_CHARS:
        raise ValueError(f"File too large for the free tier demo (>{MAX_CHARS} chars)")
    kind = detect_kind(filename, content)
    before = scanner(content, kind)
    res = {"kind": kind, "before": before, "explanations": [], "fixed_file": None, "after": None, "verdict": "clean"}
    if not before:
        return res
    fl = "\n".join(f"- {f['check_id']}: {f['name']} ({f['resource']})" for f in before)
    out = json.loads(llm(PROMPT.format(kind=kind, findings=fl, content=content)))
    res["explanations"] = out.get("explanations", [])
    fixed = out.get("fixed_file") or ""
    res["fixed_file"] = fixed
    ok, msg = syntax_ok(fixed, kind)
    res["syntax_ok"], res["syntax_msg"] = ok, msg
    after = scanner(fixed, kind) if ok else None
    res["after"] = after
    b = {(f["check_id"], f["resource"]) for f in before}
    a = {(f["check_id"], f["resource"]) for f in (after or [])}
    res["fixed_ids"] = sorted(c for c, _ in b - a)
    res["new_ids"] = sorted(c for c, _ in a - b)
    if not ok:
        res["verdict"] = "rejected: fix is not valid " + kind
    elif not after:
        res["verdict"] = "verified: re-scan clean"
    else:
        res["verdict"] = f"partial: {len(after)} finding(s) remain"
    return res
