#!/usr/bin/env python3
"""Count added and removed lines in a unified diff file."""

from pathlib import Path
import argparse


def count_changed_lines(diff_path: Path) -> tuple[int, int]:
    added = 0
    removed = 0
    for line in diff_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1
    return added, removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("diff", type=Path)
    args = parser.parse_args()
    added, removed = count_changed_lines(args.diff)
    print(f"added={added} removed={removed}")


if __name__ == "__main__":
    main()
