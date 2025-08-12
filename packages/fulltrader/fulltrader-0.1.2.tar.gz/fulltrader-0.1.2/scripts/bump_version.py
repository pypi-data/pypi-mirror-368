#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"
INIT_FILE = PROJECT_ROOT / "src" / "fulltrader" / "__init__.py"


def read_current_version() -> str:
    content = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r"^version\s*=\s*\"([^\"]+)\"", content, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("Não foi possível encontrar a versão em pyproject.toml")
    return match.group(1)


def write_new_version(new_version: str) -> None:
    # Atualiza pyproject.toml
    pyproject_content = PYPROJECT.read_text(encoding="utf-8")
    pyproject_content = re.sub(
        r"^(version\s*=\s*)\"([^\"]+)\"",
        rf"\1\"{new_version}\"",
        pyproject_content,
        count=1,
        flags=re.MULTILINE,
    )
    PYPROJECT.write_text(pyproject_content, encoding="utf-8")

    # Atualiza __version__ no pacote
    init_content = INIT_FILE.read_text(encoding="utf-8")
    init_content = re.sub(
        r"^(__version__\s*=\s*)\"([^\"]+)\"",
        rf"\1\"{new_version}\"",
        init_content,
        count=1,
        flags=re.MULTILINE,
    )
    INIT_FILE.write_text(init_content, encoding="utf-8")


def bump(part: str) -> str:
    current = read_current_version()
    try:
        major_str, minor_str, patch_str = current.split(".")
        major, minor, patch = int(major_str), int(minor_str), int(patch_str)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Versão atual inválida: {current}") from exc

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    elif part.startswith("set:"):
        return part.split(":", 1)[1]
    else:
        raise SystemExit("Uso: bump_version.py [patch|minor|major|set:X.Y.Z]")

    return f"{major}.{minor}.{patch}"


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit("Uso: bump_version.py [patch|minor|major|set:X.Y.Z]")

    part = argv[0]
    new_version = bump(part)
    write_new_version(new_version)
    print(new_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


