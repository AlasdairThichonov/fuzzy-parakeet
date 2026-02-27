# Autonomous Deployment Validator (deploy-guard)

`deploy-guard` is a production-oriented validator for deployment artifacts in PR/CI pipelines: Kubernetes manifests, Helm chart templates, and Terraform.

## Why this project

The tool automatically identifies deployment risks, computes an aggregate risk score (`0..100`), generates JSON/Markdown reports, and can optionally add an AI summary (with safe redaction).

## Quick start

```bash
make install
make test
make demo
```

CLI examples:

```bash
deploy-guard scan --path . --format both --output artifacts/report.json --risk-threshold 70 --no-llm
python -m deploy_guard scan --path demo --format md --no-llm
```

## CLI commands

- `deploy-guard scan --path <dir> [--format json|md|both] [--output <file>] [--risk-threshold 70] [--no-llm] [--llm-provider openai|ollama|dummy] [--fail-on high|medium|low]`
- `deploy-guard explain --report <json>`
- `deploy-guard rules list`
- `deploy-guard rules test --path <dir>`

## Scoring model

- Each rule has `severity` and `score_impact`.
- Total impact is normalized to `100`.
- `pass=true` when `score < threshold`.
- `--fail-on` can fail the pipeline when findings at or above the specified severity are present.

## GitHub Actions integration

Workflow example: `.github/workflows/deploy-guard.yml`

- runs on `pull_request`
- generates `artifacts/report.json` and `artifacts/report.md`
- publishes markdown to job summary

Reusable action: `.github/actions/deploy-guard/action.yml`.

## LLM and security

By default, no external network calls are required. LLM usage is explicitly enabled via provider selection:

```bash
deploy-guard scan --path . --llm-provider dummy
```

Disable LLM:

```bash
deploy-guard scan --path . --no-llm
```

Before LLM prompt submission, redaction removes sensitive patterns:
- API keys / bearer tokens / private keys
- YAML keys: `password`, `secret`, `token`, `apiKey`, `private_key`, `client_secret`
- Terraform keys: `secret_key`, `access_key`, `private_key`, `client_secret`

## Adding a new rule

1. Add `RuleMeta` and rule logic to `deploy_guard/rules/core_rules.py`.
2. Register the rule in `build_registry()`.
3. Add or update tests.

Extension skeleton via entrypoints: `deploy_guard/rules/extensions.py`.

## Limitations / future work

- Helm templates with advanced Go templating are only partially analyzed (no full render pipeline yet).
- No `terraform plan` diff analysis yet (currently static HCL checks).
- Planned: OPA/Rego integration, SARIF export, automated PR comment bot.
