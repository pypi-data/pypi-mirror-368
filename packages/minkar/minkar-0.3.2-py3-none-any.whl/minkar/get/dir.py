from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Optional, Pattern, Tuple

import typer

app = typer.Typer(add_completion=False, help="Render a directory tree for a project.")

def compile_patterns(patterns: Optional[str]) -> List[Pattern[str]]:
    return [re.compile(p.strip()) for p in patterns.split(",") if p.strip()] if patterns else []

def skip(path: Path, regexes: List[Pattern[str]], include_dot: bool) -> bool:
    return (not include_dot and path.name.startswith(".")) or any(r.search(str(path)) for r in regexes)

def tree_spaces(root: Path, limit: int, files: bool, include_dot: bool, excl: List[Pattern[str]]) -> str:
    lines: List[str] = []
    for cur_root, dirs, fs in os.walk(root):
        cur_path = Path(cur_root)
        depth = len(cur_path.relative_to(root).parts)
        if 0 <= limit < depth:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not skip(cur_path / d, excl, include_dot)]
        indent = "    " * depth
        lines.append(f"{indent}{cur_path.name}/" if depth else f"{cur_path.name}/")
        if files:
            for f in fs:
                if skip(cur_path / f, excl, include_dot):
                    continue
                lines.append(f"{indent}    {f}")
    return "\n".join(lines)

def tree_bars(root: Path, limit: int, files: bool, include_dot: bool, excl: List[Pattern[str]]) -> str:
    def rec(dir_path: Path, prefix: str, depth: int) -> None:
        if 0 <= limit < depth:
            return
        entries: List[Tuple[Path, bool]] = []
        for e in sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            if skip(e, excl, include_dot):
                continue
            entries.append((e, e.is_dir()))
        for i, (e, is_dir) in enumerate(entries):
            last = i == len(entries) - 1
            conn = "└── " if last else "├── "
            lines.append(f"{prefix}{conn}{e.name}{'/' if is_dir else ''}")
            if is_dir:
                rec(e, prefix + ("    " if last else "│   "), depth + 1)
    lines: List[str] = [f"{root.name}/"]
    rec(root, "", 0)
    return "\n".join(lines)

def clip(text: str) -> None:
    try:
        import pyperclip  # type: ignore
        pyperclip.copy(text)
        typer.echo("tree copied to clipboard")
    except Exception:
        typer.echo("clipboard unavailable")

@app.callback(invoke_without_command=True)
def main(
    dir: Path = typer.Option(Path.cwd(), "--dir", "-d", exists=True, file_okay=False, resolve_path=True, help="Root directory."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Destination file."),
    bars: bool = typer.Option(False, "--bars", "-b", help="Use Unicode bar layout (├──, └──)."),
    depth: Optional[int] = typer.Option(None, "--depth", "-m", help="Limit recursion depth."),
    include_files: bool = typer.Option(False, "--include-files", "-f", help="Include files in output."),
    exclude: Optional[str] = typer.Option(None, "--exclude", "-e", help="Regex patterns (comma-separated) to skip paths."),
    include_dot_dirs: bool = typer.Option(False, "--include-dot-dirs", help="Include dot-prefixed directories."),
    stdout: bool = typer.Option(False, "--stdout", "-s", help="Print tree instead of copying/saving."),
) -> None:
    limit = -1 if depth is None else depth
    patterns = compile_patterns(exclude)
    tree = (
        tree_bars(dir, limit, include_files, include_dot_dirs, patterns)
        if bars
        else tree_spaces(dir, limit, include_files, include_dot_dirs, patterns)
    )
    if stdout:
        typer.echo(tree)
    elif output:
        output.write_text(tree, encoding="utf-8")
        typer.echo(f"tree saved to {output}")
    else:
        typer.echo(tree)
        clip(tree)
