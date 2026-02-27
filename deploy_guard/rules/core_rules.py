# mypy: disable-error-code="misc"
from __future__ import annotations

from typing import Any

from deploy_guard.models import Finding, RuleMeta, Severity
from deploy_guard.rules.engine import RuleRegistry


def _mk(meta: RuleMeta, file: str, resource: str, message: str) -> Finding:
    return Finding(
        rule_id=meta.id,
        title=meta.title,
        severity=meta.severity,
        category=meta.category,
        score_impact=meta.score_impact,
        description=meta.description,
        remediation=meta.remediation,
        references=meta.references,
        file=file,
        line=None,
        resource=resource,
        message=message,
    )


def _workload_docs(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [d for d in docs if d.get("kind") in {"Deployment", "StatefulSet"}]


def _res(doc: dict[str, Any]) -> str:
    name = doc.get("metadata", {}).get("name", "unknown")
    return str(name)


def build_registry() -> RuleRegistry:
    reg = RuleRegistry()

    rules: list[tuple[RuleMeta, Any]] = [
        (RuleMeta("K8S-SEC-001", "Container runs as root", Severity.HIGH, "Kubernetes Security", 10, "running as root", "Set runAsNonRoot=true", ["https://kubernetes.io/docs/concepts/security/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "runAsNonRoot is not true") for d in _workload_docs(c.docs) if d.get("spec", {}).get("template", {}).get("spec", {}).get("securityContext", {}).get("runAsNonRoot") is not True]),
        (RuleMeta("K8S-SEC-002", "Privileged container", Severity.CRITICAL, "Kubernetes Security", 15, "privileged true", "Disable privileged mode", ["https://kubernetes.io/docs/tasks/configure-pod-container/security-context/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "container privileged=true") for d in c.docs if "'privileged': True" in str(d)]),
        (RuleMeta("K8S-SEC-003", "Service account token automount", Severity.MEDIUM, "Kubernetes Security", 6, "token automount", "Set automountServiceAccountToken=false", ["https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "automountServiceAccountToken not disabled") for d in _workload_docs(c.docs) if d.get("spec", {}).get("template", {}).get("spec", {}).get("automountServiceAccountToken") is not False]),
        (RuleMeta("K8S-SEC-004", "Ingress without TLS", Severity.HIGH, "Kubernetes Security", 8, "no tls", "Configure TLS section", ["https://kubernetes.io/docs/concepts/services-networking/ingress/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "Ingress has no TLS") for d in c.docs if d.get("kind") == "Ingress" and not d.get("spec", {}).get("tls")]),
        (RuleMeta("K8S-REL-001", "Missing readiness probe", Severity.HIGH, "Kubernetes Reliability", 8, "no readiness", "Add readinessProbe", ["https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "No readinessProbe in pod spec") for d in _workload_docs(c.docs) if "readinessProbe" not in str(d)]),
        (RuleMeta("K8S-REL-002", "Missing liveness probe", Severity.MEDIUM, "Kubernetes Reliability", 6, "no liveness", "Add livenessProbe", ["https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "No livenessProbe in pod spec") for d in _workload_docs(c.docs) if "livenessProbe" not in str(d)]),
        (RuleMeta("K8S-REL-003", "No PodDisruptionBudget", Severity.MEDIUM, "Kubernetes Reliability", 5, "no pdb", "Add PDB", ["https://kubernetes.io/docs/tasks/run-application/configure-pdb/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "No PDB found for workload") for d in _workload_docs(c.docs) if not any(x.get("kind") == "PodDisruptionBudget" for x in c.docs)]),
        (RuleMeta("K8S-REL-004", "Single replica", Severity.MEDIUM, "Kubernetes Reliability", 4, "single replica", "Use >=2 replicas", ["https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "replicas < 2") for d in _workload_docs(c.docs) if d.get("spec", {}).get("replicas", 1) < 2]),
        (RuleMeta("K8S-SCALE-001", "No CPU requests/limits", Severity.HIGH, "Kubernetes Scalability", 8, "no resources", "Define resources.requests and resources.limits", ["https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "resources block missing") for d in _workload_docs(c.docs) if "resources" not in str(d)]),
        (RuleMeta("K8S-SCALE-002", "No HPA", Severity.MEDIUM, "Kubernetes Scalability", 4, "no hpa", "Add HorizontalPodAutoscaler", ["https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "Workload has no matching HPA") for d in _workload_docs(c.docs) if not any(x.get("kind") == "HorizontalPodAutoscaler" for x in c.docs)]),
        (RuleMeta("K8S-SCALE-003", "Image tag latest", Severity.HIGH, "Supply Chain / CI Hygiene", 8, "latest tag", "Pin image version", ["https://kubernetes.io/docs/concepts/containers/images/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "image uses :latest") for d in c.docs if ":latest" in str(d)]),
        (RuleMeta("K8S-SCALE-004", "Image digest not pinned", Severity.MEDIUM, "Supply Chain / CI Hygiene", 5, "no digest", "Use image@sha256", ["https://slsa.dev/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "image not pinned by digest") for d in c.docs if "image" in str(d) and "sha256:" not in str(d)]),
        (RuleMeta("TF-SEC-001", "Public S3 bucket", Severity.CRITICAL, "Terraform Security", 15, "public s3", "Set ACL private and block public access", ["https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket"]),
         lambda c, m: [_mk(m, t["__file"], "aws_s3_bucket", "bucket ACL appears public") for t in c.tf_blocks if "public-read" in str(t)]),
        (RuleMeta("TF-SEC-002", "Open security group", Severity.CRITICAL, "Terraform Security", 15, "0.0.0.0/0", "Restrict ingress CIDRs", ["https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group"]),
         lambda c, m: [_mk(m, t["__file"], "aws_security_group", "Ingress allows 0.0.0.0/0") for t in c.tf_blocks if "0.0.0.0/0" in str(t)]),
        (RuleMeta("TF-SEC-003", "IAM wildcard", Severity.HIGH, "Terraform Security", 10, "iam wildcard", "Use least privilege actions/resources", ["https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"]),
         lambda c, m: [_mk(m, t["__file"], "aws_iam_policy", "Policy includes wildcard *") for t in c.tf_blocks if '"*"' in str(t) or "*" in str(t.get("data", {}))]),
        (RuleMeta("TF-BLAST-001", "No deletion protection", Severity.HIGH, "Terraform Blast Radius", 10, "deletion protection", "Enable deletion protection", ["https://docs.aws.amazon.com/"]),
         lambda c, m: [_mk(m, t["__file"], "critical resource", "deletion protection not found") for t in c.tf_blocks if "aws_db_instance" in str(t) and "deletion_protection" not in str(t)]),
        (RuleMeta("TF-BLAST-002", "Unpinned module source", Severity.MEDIUM, "Terraform Blast Radius", 6, "module pin", "Pin module ref/version", ["https://developer.hashicorp.com/terraform/language/modules/sources"]),
         lambda c, m: [_mk(m, t["__file"], "module", "module source has no ref") for t in c.tf_blocks if "module" in t and "?ref=" not in str(t.get("module"))]),
        (RuleMeta("TF-BLAST-003", "No required_providers version", Severity.MEDIUM, "Supply Chain / CI Hygiene", 5, "provider pin", "Set exact provider versions", ["https://developer.hashicorp.com/terraform/language/providers/requirements"]),
         lambda c, m: [_mk(m, t["__file"], "terraform", "required_providers version missing") for t in c.tf_blocks if "required_providers" in str(t) and "version" not in str(t)]),
        (RuleMeta("SCH-001", "Mutable image registry tag", Severity.MEDIUM, "Supply Chain / CI Hygiene", 5, "mutable tag", "Use immutable tag and digest", ["https://slsa.dev/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "image tag appears mutable") for d in c.docs if any(x in str(d) for x in [":dev", ":main", ":snapshot"])]),
        (RuleMeta("SCH-002", "K8s Secret manifest present", Severity.MEDIUM, "Supply Chain / CI Hygiene", 7, "secret manifest", "Use external secret manager", ["https://kubernetes.io/docs/concepts/configuration/secret/"]),
         lambda c, m: [_mk(m, d["__file"], _res(d), "Raw Secret manifest detected") for d in c.docs if d.get("kind") == "Secret"]),
    ]

    for meta, fn in rules:
        reg.register(meta, lambda c, _fn=fn, _m=meta: _fn(c, _m))
    return reg
