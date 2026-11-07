# SafeSpace Hacks submission draft: MisconfigExplained

**Deadline:** 22 Nov 2026 5:00pm EST = **Mon 23 Nov 8:30am Adelaide**. Aim to submit Sun 22 Nov.

## Tagline
Plain-English explanations and verified fixes for cloud misconfigurations.

## Problem
Students, small teams and non-specialists deploy Terraform/Kubernetes files with insecure defaults (public buckets, privileged pods). Scanner output is cryptic, and AI "fixes" are often trusted blindly even when they break things.

## Solution
Checkov scan → plain-English explanation per finding (meaning, risk, fix) → proposed fix → syntax check and re-scan → honest verdict (verified / partial / rejected) with fixed and newly introduced findings listed.

## Safety benefit
Helps people understand and close misconfigurations that expose data. Refuses to present unverified fixes as safe.

## Trust & responsible design
- Synthetic sample files only; warning not to paste secrets.
- Every fix is re-scanned; new findings are shown.
- Limitations stated in the UI and README (re-scan ≠ deployable; see EASE results).

## Built during the event (17 Oct – 22 Nov) vs pre-existing
- New: MisconfigExplained app, UI, explanation prompt, verification verdicts, tests.
- Pre-existing: EASE research harness ideas (author's own), Checkov, Flask.
- AI assistance: built with AI coding assistance (declare as required).

## Demo evidence (run 8 Nov 2026)
- `samples/pod.yaml`: 20 Checkov findings before the fix. After the fix the verdict was **partial**: the YAML parses and 1 finding remains.
- `samples/s3_bucket.tf`: 7 findings before. The verdict was **partial**: 6 checks were fixed, but the added resources raised new ones, so 15 findings remain (terraform was not installed, so only a brace-balance syntax check ran). This is the stated limitation: one safer outcome plus one honest limitation.
- Screenshots: `screenshots/01-input.png`, `02-result-pod.png`, `02-result-s3.png`. Walkthrough: `WALKTHROUGH.md`.

## Built with
Python, Flask, Checkov, Groq (gpt-oss-120b), PyYAML.

## TODO (Niaz)
- [ ] Confirm "Join hackathon" on safespace-hacks.devpost.com and student status (UniSC MSc) + geographic eligibility.
- [x] Public repo: https://github.com/shohrabniaz/misconfig-explained
- [x] Screenshots (required): done in `screenshots/` (retake if the UI changes).
- [ ] Accessible demo: hosted URL (e.g. Render/Vercel free) or recorded walkthrough (video optional).
- [ ] Team/credits section; fill your name.
- [ ] Keep links working through 24 Nov.
