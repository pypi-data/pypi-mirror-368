from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Pattern, Tuple

import typer

app = typer.Typer(add_completion=False, help="Merge source files and output them as requested.")

POPULAR_EXTS: set[str] = {
    "py", "js", "ts", "java", "kt", "go",
    "rs", "c", "cpp", "h", "cs", "php",
    "rb", "swift",
}


def compile_lang_patterns(value: Optional[str]) -> List[Pattern[str]]:
    if value is None:
        return [re.compile(fr"^(?:{ext})$") for ext in POPULAR_EXTS]
    if value.strip() == "*":
        return [re.compile(r".*")]
    return [re.compile(p.strip()) for p in value.split(",") if p.strip()]


def compile_exclude(patterns: Optional[str]) -> List[Pattern[str]]:
    if not patterns:
        return []
    return [re.compile(p.strip()) for p in patterns.split(",") if p.strip()]


def match_any(text: str, regexes: List[Pattern[str]]) -> bool:
    return any(r.search(text) for r in regexes)


def iter_source_files(
    root: Path,
    depth_limit: int,
    lang_patterns: List[Pattern[str]],
    include_dot_dirs: bool,
    exclude_patterns: List[Pattern[str]],
) -> List[Path]:
    if depth_limit == 0:
        files: List[Path] = []
        for p in root.iterdir():
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if match_any(p.name, exclude_patterns) or match_any(str(rel), exclude_patterns):
                continue
            if match_any(p.suffix.lstrip("."), lang_patterns):
                files.append(p)
        return sorted(files, key=lambda p: p.name.lower())
    collected: List[Tuple[int, Path]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current_path = Path(dirpath)
        depth = len(current_path.relative_to(root).parts)
        if 0 <= depth_limit < depth:
            dirnames[:] = []
            continue
        dirnames[:] = [
            d for d in dirnames
            if (include_dot_dirs or not d.startswith(".")) and not match_any(d, exclude_patterns)
        ]
        for fname in filenames:
            file_path = current_path / fname
            rel = file_path.relative_to(root)
            if match_any(file_path.parent.name, exclude_patterns) or match_any(file_path.name, exclude_patterns) or match_any(str(rel), exclude_patterns):
                continue
            if match_any(file_path.suffix.lstrip("."), lang_patterns):
                collected.append((depth, file_path))
    collected.sort(key=lambda t: (t[0], t[1].as_posix().lower()))
    return [p for _, p in collected]


def build_merged_text(
    root: Path,
    depth_limit: int,
    lang_patterns: List[Pattern[str]],
    include_dot_dirs: bool,
    exclude_patterns: List[Pattern[str]],
    verbose: bool,
) -> Tuple[str, Dict[str, int], int, int, Dict[str, List[Tuple[str, int, int]]]]:
    blocks: List[str] = []
    ext_counts: Dict[str, int] = {}
    details: DefaultDict[str, List[Tuple[str, int, int]]] = defaultdict(list)
    total_lines = 0
    total_chars = 0
    for file in iter_source_files(root, depth_limit, lang_patterns, include_dot_dirs, exclude_patterns):
        rel_path = file.relative_to(root)
        try:
            content = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        ext = file.suffix.lstrip(".")
        lines = content.count("\n") + 1
        chars = len(content)
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        details[ext].append((str(rel_path), lines, chars))
        total_lines += lines
        total_chars += chars
        blocks.append(f"# {rel_path}\n{content}\n")
        if verbose:
            typer.echo(f"Done: {rel_path} | {lines} lines, {chars} chars")
    return "\n".join(blocks), ext_counts, total_lines, total_chars, details


def format_report(ext_counts: Dict[str, int], lines: int, chars: int) -> str:
    total_files = sum(ext_counts.values())
    summary = ", ".join(f"{ext}: {cnt}" for ext, cnt in sorted(ext_counts.items()))
    return f"📊 {total_files} file(s) ({summary}); {lines} lines, {chars} characters."


@app.callback(invoke_without_command=True)
def main(
    dir: Path = typer.Option(Path.cwd(), "--dir", "-d", exists=True, file_okay=False, resolve_path=True, help="Root directory."),
    langs: Optional[str] = typer.Option(None, "--langs", "-l", help="Regex patterns for extensions, '*' or 'all'."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Destination file."),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Enable recursion (unlimited)."),
    depth: Optional[int] = typer.Option(None, "--depth", help="Limit recursion depth; requires --recursive."),
    exclude: Optional[str] = typer.Option(None, "--exclude", "-e", help="Regex patterns for directories/files to skip."),
    include_dot_dirs: bool = typer.Option(False, "--include-dot-dirs", help="Include dot-prefixed directories."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output."),
    stdout: bool = typer.Option(False, "--stdout", "-s", help="Print merged text instead of copying."),
) -> None:
    if langs and "all" in langs:
        langs = langs.replace("all", "*")
    depth_limit = -1 if recursive and depth is None else (depth or 0)
    lang_patterns = compile_lang_patterns(langs)
    exclude_patterns = compile_exclude(exclude)
    merged_text, ext_counts, total_lines, total_chars, details = build_merged_text(
        root=dir,
        depth_limit=depth_limit,
        lang_patterns=lang_patterns,
        include_dot_dirs=include_dot_dirs,
        exclude_patterns=exclude_patterns,
        verbose=verbose,
    )
    if stdout:
        typer.echo(merged_text)
    elif output:
        output.write_text(merged_text, encoding="utf-8")
        typer.echo(f"Saved to {output}.")
    else:
        try:
            import pyperclip  # type: ignore
            pyperclip.copy(merged_text)
            typer.echo("Text copied to clipboard.")
        except Exception:
            typer.echo("Clipboard unavailable – use --stdout or --output instead.")
            raise typer.Exit(1)
    typer.echo(format_report(ext_counts, total_lines, total_chars))
    if verbose:
        for ext in sorted(details):
            ext_total_lines = sum(ln for _, ln, _ in details[ext])
            ext_total_chars = sum(ch for _, _, ch in details[ext])
            typer.echo(f"\n[{ext}] - {ext_total_lines} lines, {ext_total_chars} chars")
            for path, ln, ch in sorted(details[ext], key=lambda t: t[2], reverse=True):
                typer.echo(f"  {path} – {ln} lines, {ch} chars")
