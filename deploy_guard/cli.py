from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from deploy_guard.reporting.json_report import write_json
from deploy_guard.reporting.markdown_report import build_markdown
from deploy_guard.rules.core_rules import build_registry
from deploy_guard.service import scan_path, should_fail


@click.group()
def main() -> None:
    """deploy-guard CLI."""


@main.command()
@click.option("--path", "path_", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--format", "fmt", type=click.Choice(["json", "md", "both"]), default="both")
@click.option("--output", type=click.Path(dir_okay=False), default="")
@click.option("--risk-threshold", default=70, type=int)
@click.option("--no-llm", is_flag=True, default=False)
@click.option("--llm-provider", type=click.Choice(["openai", "ollama", "dummy"]), default="dummy")
@click.option("--fail-on", type=click.Choice(["low", "medium", "high"]), default="high")
def scan(path_: str, fmt: str, output: str, risk_threshold: int, no_llm: bool, llm_provider: str, fail_on: str) -> None:
    try:
        report, md = scan_path(path_, threshold=risk_threshold, llm_enabled=not no_llm, llm_provider=llm_provider)
        out = Path(output) if output else None
        if fmt in {"json", "both"}:
            text = write_json(report, out)
            if fmt == "json":
                click.echo(text)
        if fmt in {"md", "both"}:
            if fmt == "both" and out:
                out.with_suffix(".md").write_text(md, encoding="utf-8")
            click.echo(md)
        sys.exit(1 if should_fail(report, fail_on) else 0)
    except Exception as exc:
        click.echo(f"deploy-guard error: {exc}", err=True)
        sys.exit(2)


@main.command()
@click.option("--report", "report_path", required=True, type=click.Path(exists=True, dir_okay=False))
def explain(report_path: str) -> None:
    data = json.loads(Path(report_path).read_text(encoding="utf-8"))
    click.echo(build_markdown(data))


@main.group()
def rules() -> None:
    """Manage rules."""


@rules.command("list")
def list_rules() -> None:
    reg = build_registry()
    for r in reg.list_rules():
        click.echo(f"{r.id}\t{r.severity.value}\t{r.category}\t{r.title}")


@rules.command("test")
@click.option("--path", "path_", required=True, type=click.Path(exists=True, file_okay=False))
def test_rules(path_: str) -> None:
    report, _ = scan_path(path_, llm_enabled=False)
    click.echo(json.dumps({"findings": report["findings"], "score": report["summary"]["score"]}, indent=2))
