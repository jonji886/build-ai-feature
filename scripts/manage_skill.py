#!/usr/bin/env python3
"""Install or package a portable Agent Skill without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
PAYLOAD_ENTRIES = ("SKILL.md", "agents", "assets", "references", "scripts")
AGENT_PATHS = {
    "codex": {"user": Path(".agents/skills"), "project": Path(".agents/skills")},
    "claude-code": {
        "user": Path(".claude/skills"),
        "project": Path(".claude/skills"),
    },
    "codebuddy": {
        "user": Path(".codebuddy/skills"),
        "project": Path(".codebuddy/skills"),
    },
}
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


def read_skill_name() -> str:
    content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"\A---\s*\n(?P<meta>.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        raise SystemExit("SKILL.md 缺少有效的 YAML frontmatter")
    name_match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", match.group("meta"), re.MULTILINE)
    if not name_match:
        raise SystemExit("SKILL.md frontmatter 缺少有效的 name")
    return name_match.group(1)


def payload_files() -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for entry_name in PAYLOAD_ENTRIES:
        entry = SKILL_ROOT / entry_name
        if not entry.exists():
            continue
        candidates = [entry] if entry.is_file() else sorted(entry.rglob("*"))
        for source in candidates:
            if not source.is_file():
                continue
            relative = source.relative_to(SKILL_ROOT)
            if any(part in IGNORED_PARTS for part in relative.parts) or source.suffix == ".pyc":
                continue
            files.append((source, relative))
    return files


def resolve_install_root(args: argparse.Namespace) -> Path:
    if args.target:
        return Path(args.target).expanduser().resolve()
    if args.agent == "generic":
        raise SystemExit("generic 安装必须提供 --target <skills-root>")
    relative = AGENT_PATHS[args.agent][args.scope]
    if args.scope == "user":
        return (Path.home() / relative).resolve()
    if not args.project:
        raise SystemExit("项目级安装必须提供 --project <project-path>")
    return (Path(args.project).expanduser().resolve() / relative).resolve()


def install(args: argparse.Namespace) -> int:
    name = read_skill_name()
    destination = resolve_install_root(args) / name
    files = payload_files()
    if destination.exists():
        raise SystemExit(f"目标已存在，未覆盖：{destination}")
    if not args.dry_run:
        for source, relative in files:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    print(json.dumps({
        "action": "install",
        "agent": args.agent,
        "destination": str(destination),
        "files": len(files),
        "dry_run": args.dry_run,
    }, ensure_ascii=False, indent=2))
    return 0


def package(args: argparse.Namespace) -> int:
    name = read_skill_name()
    output = Path(args.output).expanduser() if args.output else SKILL_ROOT / "dist" / f"{name}.zip"
    output = output.resolve()
    if output.exists():
        raise SystemExit(f"输出已存在，未覆盖：{output}")
    files = payload_files()
    if not args.dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for source, relative in files:
                archive.write(source, relative.as_posix())
    print(json.dumps({
        "action": "package",
        "output": str(output),
        "files": len(files),
        "layout": "SKILL.md at archive root",
        "dry_run": args.dry_run,
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install", help="安装到 Agent 的 Skill 目录")
    install_parser.add_argument(
        "--agent", choices=(*AGENT_PATHS.keys(), "generic"), required=True
    )
    install_parser.add_argument("--scope", choices=("user", "project"), default="user")
    install_parser.add_argument("--project", help="项目级安装对应的项目目录")
    install_parser.add_argument("--target", help="显式指定 Skill 根目录；会覆盖宿主默认目录")
    install_parser.add_argument("--dry-run", action="store_true")
    install_parser.set_defaults(handler=install)

    package_parser = subparsers.add_parser("package", help="生成可导入的 ZIP 包")
    package_parser.add_argument("--output", help="ZIP 输出路径；默认写入 dist/")
    package_parser.add_argument("--dry-run", action="store_true")
    package_parser.set_defaults(handler=package)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
