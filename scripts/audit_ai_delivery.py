#!/usr/bin/env python3
"""常见 AI 功能交付产物的建议性盘点。"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs"}
DOC_NAMES = {"readme.md", "spec.md", "agents.md"}


def git_changes(project: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--untracked-files=all"], cwd=project, check=True,
            capture_output=True, text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    return [line[3:].strip() for line in result.stdout.splitlines() if len(line) > 3]


def any_path(project: Path, patterns: tuple[str, ...]) -> bool:
    return any(any(project.glob(pattern)) for pattern in patterns)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="项目目录")
    args = parser.parse_args()
    project = Path(args.project).resolve()
    if not project.is_dir():
        parser.error(f"不是目录: {project}")

    changes = git_changes(project)
    changed_code = [p for p in changes if Path(p).suffix.lower() in CODE_SUFFIXES]
    changed_tests = [p for p in changes if "test" in Path(p).name.lower() or "tests" in Path(p).parts]
    changed_docs = [p for p in changes if Path(p).suffix.lower() == ".md"]
    changed_evals = [p for p in changes if "eval" in p.lower()]

    inventory = {
        "project": str(project),
        "artifacts": {
            "project_instructions": any_path(project, ("AGENTS.md", "**/AGENTS.md")),
            "requirements": any_path(project, ("SPEC.md", "docs/spec*.md", "requirements*.md")),
            "readme": (project / "README.md").exists(),
            "architecture_or_adr": any_path(project, ("docs/architecture*.md", "docs/*design*.md", "docs/adr/*.md")),
            "tests": any_path(project, ("tests/**", "test/**", "**/*_test.py", "**/*.test.*")),
            "evaluations": any_path(project, ("evals/**", "evaluations/**", "**/*eval*.py")),
        },
        "changes": {
            "all": changes,
            "code": changed_code,
            "tests": changed_tests,
            "documentation": changed_docs,
            "evaluations": changed_evals,
        },
        "advisories": [],
    }
    advisories = inventory["advisories"]
    if changed_code and not changed_tests:
        advisories.append("代码发生了变更但没有测试变更；请核实该风险是否已被覆盖。")
    if changed_code and not changed_docs:
        advisories.append("代码发生了变更但没有文档变更；请核实行为或契约是否发生变化。")
    if changed_code and not changed_evals:
        advisories.append("代码发生了变更但没有评估变更；请核实 AI 行为或发布基线是否发生变化。")
    if not inventory["artifacts"]["requirements"]:
        advisories.append("未找到显式的需求/规格说明产物。")
    if not inventory["artifacts"]["tests"]:
        advisories.append("未找到自动化测试产物。")

    print(json.dumps(inventory, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
