# MisconfigExplained: walkthrough script (about 2.5 min; screenshots in /screenshots)
Example run on 8 Nov 2026 (Groq gpt-oss-120b, Checkov). LLM output varies from run to run, so re-record it before submitting.

| t | Screen | Narration |
|---|---|---|
| 0:00 | Title + `01-input.png` | "Cloud config files often ship with insecure defaults. Scanner output is cryptic, and AI fixes get trusted blindly. MisconfigExplained explains each finding and then checks the fix instead of trusting it." |
| 0:20 | Paste `samples/pod.yaml` (privileged pod) and click Explain and fix | "This is a synthetic Kubernetes pod running privileged. No real systems and no secrets." |
| 0:35 | `02-result-pod.png`, finding cards | "Checkov found 20 issues. For each one you get what it means, what could go wrong, and the fix, all in plain English." |
| 1:10 | Verdict box | "The fix is re-scanned. Verdict: partial. 1 finding still remains, and the YAML parses. We never call it safe unless the evidence says so." |
| 1:30 | `02-result-s3.png` (S3 bucket) | "This is the limitation. For a bare S3 bucket the AI's fix closed 6 checks but added new resources, which raised their own findings, so 15 remain. That is exactly what our EASE research found: scanner-passing or 'fixed' code is not automatically safe or deployable." |
| 2:05 | README limitations | "Responsible design means synthetic data only, a do-not-paste-secrets warning, every fix verified, and the limitations shown up front." |
| 2:20 | Repo URL | "It's open source under MIT. Thanks!" |
