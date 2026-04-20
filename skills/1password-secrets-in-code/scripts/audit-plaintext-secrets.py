#!/usr/bin/env python3
"""Scan repository text files for likely hardcoded secrets.

Outputs newline-delimited JSON records to stdout.
Diagnostics (if any) go to stderr.
Exit code:
- 0: completed, no findings
- 1: completed with findings
- 2: usage or runtime error
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    severity: str
    suggestion: str


RULES: list[Rule] = [
    Rule(
        name="github_pat",
        pattern=re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
        severity="high",
        suggestion="Move token to 1Password and reference as op://<vault>/<item>/<field>",
    ),
    Rule(
        name="openai_key",
        pattern=re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
        severity="high",
        suggestion="Store API key in 1Password and load via op run or SDK resolve",
    ),
    Rule(
        name="aws_access_key_id",
        pattern=re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        severity="high",
        suggestion="Rotate key and use IAM+1Password reference pattern",
    ),
    Rule(
        name="generic_password_assignment",
        pattern=re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*[\"'][^\"']{6,}[\"']"),
        severity="medium",
        suggestion="Replace literal password with op:// reference",
    ),
    Rule(
        name="bearer_token_literal",
        pattern=re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*"),
        severity="medium",
        suggestion="Avoid embedding bearer tokens; resolve from 1Password at runtime",
    ),
]

TEXT_EXTENSIONS = {
    ".env",
    ".txt",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".sh",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".turbo",
    ".pnpm-store",
    ".idea",
    ".vscode",
}


def iter_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name.startswith(".env"):
            yield path


def find_matches(path: Path, rules: Iterable[Rule], root: Path) -> Iterator[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        print(f"warn: failed to read {path}: {exc}", file=sys.stderr)
        return

    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in rules:
            if rule.pattern.search(line):
                yield {
                    "file": str(path.relative_to(root)),
                    "line": line_number,
                    "rule": rule.name,
                    "severity": rule.severity,
                    "snippet": line[:240],
                    "suggestion": rule.suggestion,
                }


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    if not root.exists() or not root.is_dir():
        print("error: root path must be an existing directory", file=sys.stderr)
        return 2

    findings: list[dict] = []
    for file_path in iter_files(root):
        findings.extend(find_matches(file_path, RULES, root))

    for finding in findings:
        print(json.dumps(finding, ensure_ascii=False))

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
