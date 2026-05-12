#!/usr/bin/env python3
"""Create a sanitized public artifact export for the IoT benchmark repository.

The private working repository contains manuscript drafts, local metadata, and
ignored credential files. This script builds a fresh, allowlisted export that is
safe to inspect before publishing as the public data/code artifact.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_OUTPUT = "_public_release/iot-benchmark-pack-public"

EXCLUDE_PATTERNS = [
    ".git/**",
    ".DS_Store",
    "**/.DS_Store",
    ".env",
    ".env.*",
    "_public_release/**",
    "__pycache__/**",
    "**/__pycache__/**",
    "*.pyc",
    "*.pyo",
    "*.log",
    "chat_snapshot*",
    "chat_snapshot*/**",
    "repo_tree.txt",
    "data_tree.txt",
    "firmware/secrets.h",
    "docs/paper_*",
    "docs/paper_*/**",
    "docs/*highlights*.md",
    "docs/archive/**",
    "docs/*.pptx",
    "docs/*.tikz",
]

TEXT_SUFFIXES = {
    "",
    ".csv",
    ".cff",
    ".h",
    ".ino",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
}

PRIVATE_IP_RE = re.compile(
    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"192\.168\.\d{1,3}\.\d{1,3}|"
    r"172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})\b"
)
ABS_USER_PATH_RE = re.compile(r"<local-path>,;:)\"'\]]+")
SERIAL_PORT_RE = re.compile(r"/dev/(?:cu|tty)\.[A-Za-z0-9_.-]+")
MAC_RE = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")

LITERAL_REPLACEMENTS = {
    "logger-host": "logger-host",
    "iperf-server": "iperf-server",
    "light.benchmark_device": "light.benchmark_device",
}


def repo_root() -> Path:
    out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True)
    return Path(out.strip())


def git_files(root: Path) -> list[Path]:
    out = subprocess.check_output(["git", "ls-files"], cwd=root, text=True)
    files = {Path(line) for line in out.splitlines() if line.strip()}

    # Include the export tooling even before it has been committed in the
    # private repo, so first-time exports are self-documenting.
    for extra_path in (
        Path(".zenodo.json"),
        Path("CITATION.cff"),
        Path("DATA_LICENSE.md"),
        Path("LICENSE"),
        Path("python/export_public_artifact.py"),
        Path("docs/public_artifact_export.md"),
    ):
        if (root / extra_path).exists():
            files.add(extra_path)

    return sorted(files)


def excluded(path: Path) -> bool:
    posix = path.as_posix()
    return any(fnmatch.fnmatch(posix, pattern) for pattern in EXCLUDE_PATTERNS)


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def sanitize_text(text: str) -> str:
    text = PRIVATE_IP_RE.sub("<private-ip>", text)
    text = ABS_USER_PATH_RE.sub("<local-path>", text)
    text = SERIAL_PORT_RE.sub("/dev/serial-port", text)
    text = MAC_RE.sub("<mac-address>", text)
    for old, new in LITERAL_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def copy_file(src: Path, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if is_text_file(src):
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dst)
            return False
        dst.write_text(sanitize_text(text), encoding="utf-8")
        return True

    shutil.copy2(src, dst)
    return False


def write_public_notes(out_dir: Path, copied: int, sanitized: int, excluded_count: int) -> None:
    notes = f"""# Public Artifact Export

This folder was generated from the private working repository by
`python/export_public_artifact.py`.

The export is intended to contain the data, firmware, and analysis scripts needed
to reproduce the reported measurements. It intentionally excludes manuscript
drafts, paper conversion files, private local environment files, and generated
chat snapshots.

Sanitization applied during export:

- private LAN IP addresses are replaced with `<private-ip>`
- absolute local user paths are replaced with `<local-path>`
- serial device names are replaced with `/dev/serial-port`
- local host/device labels are generalized
- the local Home Assistant entity id is replaced with `light.benchmark_device`

Export summary:

- copied files: {copied}
- text files sanitized: {sanitized}
- excluded tracked files: {excluded_count}

Before publishing, inspect this folder, initialize it as a fresh Git repository,
and create the public GitHub release or Zenodo archive from the fresh repository.
"""
    (out_dir / "PUBLIC_RELEASE_NOTES.md").write_text(notes, encoding="utf-8")


def write_manifest(
    out_dir: Path,
    copied_files: list[str],
    excluded_files: list[str],
    include_excluded_file_list: bool,
) -> None:
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generator": "python/export_public_artifact.py",
        "copied_file_count": len(copied_files),
        "excluded_file_count": len(excluded_files),
        "excluded_pattern_count": len(EXCLUDE_PATTERNS),
        "copied_files": copied_files,
    }
    if include_excluded_file_list:
        manifest["excluded_patterns"] = EXCLUDE_PATTERNS
        manifest["excluded_files"] = excluded_files
    (out_dir / "PUBLIC_EXPORT_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def ensure_safe_output(root: Path, out_dir: Path, force: bool, allow_delete_git_output: bool) -> None:
    out_dir = out_dir.resolve()
    if out_dir == root.resolve():
        raise SystemExit("Refusing to export into the repository root.")
    if root.resolve() in out_dir.parents and out_dir.name in {"", ".", ".."}:
        raise SystemExit("Refusing unsafe output path.")
    if out_dir.exists():
        if (out_dir / ".git").exists() and not allow_delete_git_output:
            raise SystemExit(
                f"Output contains a Git repository: {out_dir}. "
                "Refusing to delete it. Export to a separate staging directory, "
                "or pass --allow-delete-git-output if you intentionally want "
                "to replace this Git working copy."
            )
        if not force:
            raise SystemExit(f"Output exists: {out_dir}. Re-run with --force to replace it.")
        shutil.rmtree(out_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument("--force", action="store_true", help="Replace existing output directory")
    parser.add_argument("--dry-run", action="store_true", help="Show counts without copying")
    parser.add_argument(
        "--allow-delete-git-output",
        action="store_true",
        help="Allow --force to delete an output directory that contains .git",
    )
    parser.add_argument(
        "--include-excluded-file-list",
        action="store_true",
        help="Write excluded file names into the public manifest for audit purposes",
    )
    args = parser.parse_args()

    root = repo_root()
    out_dir = (root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    files = git_files(root)
    included = [p for p in files if not excluded(p)]
    excluded_files = [p.as_posix() for p in files if excluded(p)]

    if args.dry_run:
        print(f"Repository: {root}")
        print(f"Output: {out_dir}")
        print(f"Included files: {len(included)}")
        print(f"Excluded tracked files: {len(excluded_files)}")
        return

    ensure_safe_output(root, out_dir, args.force, args.allow_delete_git_output)
    out_dir.mkdir(parents=True, exist_ok=False)

    copied_files: list[str] = []
    sanitized_count = 0
    for rel in included:
        src = root / rel
        dst = out_dir / rel
        sanitized = copy_file(src, dst)
        sanitized_count += int(sanitized)
        copied_files.append(rel.as_posix())

    write_public_notes(out_dir, len(copied_files), sanitized_count, len(excluded_files))
    write_manifest(
        out_dir,
        copied_files,
        excluded_files,
        args.include_excluded_file_list,
    )
    print(f"Exported {len(copied_files)} files to {out_dir}")
    print(f"Sanitized text files: {sanitized_count}")
    print(f"Excluded tracked files: {len(excluded_files)}")


if __name__ == "__main__":
    main()
