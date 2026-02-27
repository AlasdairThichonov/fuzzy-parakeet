from __future__ import annotations

import os
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def summarize(self, prompt: str) -> tuple[str, list[str]]:
        raise NotImplementedError


class DummyProvider(LLMProvider):
    def summarize(self, prompt: str) -> tuple[str, list[str]]:
        return (
            "Risk is elevated due to security and reliability gaps.",
            [
                "Pin container images with digest.",
                "Restrict Terraform ingress and IAM wildcard access.",
                "Add probes, PDB and resource limits to workloads.",
            ],
        )


class OpenAIProvider(LLMProvider):
    def summarize(self, prompt: str) -> tuple[str, list[str]]:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.responses.create(model="gpt-4.1-mini", input=prompt)
        text = resp.output_text
        lines = [x.strip("- ") for x in text.splitlines() if x.strip()]
        return lines[0] if lines else "", lines[1:6]


class OllamaProvider(LLMProvider):
    def summarize(self, prompt: str) -> tuple[str, list[str]]:
        import requests

        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.1")
        r = requests.post(f"{host}/api/generate", json={"model": model, "prompt": prompt, "stream": False}, timeout=20)
        r.raise_for_status()
        text = r.json().get("response", "")
        lines = [x.strip("- ") for x in text.splitlines() if x.strip()]
        return lines[0] if lines else "", lines[1:6]


def get_provider(name: str) -> LLMProvider:
    if name == "dummy":
        return DummyProvider()
    if name == "openai":
        return OpenAIProvider()
    if name == "ollama":
        return OllamaProvider()
    raise ValueError(f"Unsupported provider: {name}")
