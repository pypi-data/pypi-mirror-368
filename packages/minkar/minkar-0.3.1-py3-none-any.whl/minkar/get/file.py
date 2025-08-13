#!/usr/bin/env python3
from __future__ import annotations

import os
import random
import re
import zipfile
from pathlib import Path
from typing import List, Optional, Pattern

import typer

app = typer.Typer(add_completion=False, help="Create a zip archive from a directory with include/exclude patterns.")

def pat_list(value: Optional[str]) -> List[Pattern[str]]:
    return [re.compile(p.strip()) for p in value.split(",") if p.strip()] if value else []

def ignore(path: Path, ex: List[Pattern[str]], inc_dot: bool) -> bool:
    return (not inc_dot and path.name.startswith(".")) or any(r.search(str(path)) for r in ex)

def include(path: Path, inc: List[Pattern[str]]) -> bool:
    return not inc or any(r.search(str(path)) for r in inc)

def collect(root: Path, lim: int, inc_dot: bool, ex: List[Pattern[str]], inc: List[Pattern[str]]) -> List[Path]:
    res: List[Path] = []
    for cur_root, dirs, files in os.walk(root):
        cur = Path(cur_root)
        dep = len(cur.relative_to(root).parts)
        if 0 <= lim < dep:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not ignore(cur / d, ex, inc_dot)]
        for f in files:
            p = cur / f
            if ignore(p, ex, inc_dot) or not include(p, inc):
                continue
            res.append(p)
    return res

@app.callback(invoke_without_command=True)
def main(
    dir: Path = typer.Option(Path.cwd(), "--dir", "-d", exists=True, file_okay=False, resolve_path=True, help="Root directory."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Destination .zip file. Defaults to a random name in the current directory."),
    depth: Optional[int] = typer.Option(None, "--depth", help="Limit recursion depth. Omit for unlimited."),
    exclude: Optional[str] = typer.Option(None, "--exclude", "-e", help="Comma-separated regex patterns to skip matching paths."),
    match: Optional[str] = typer.Option(None, "--match", "-m", help="Comma-separated regex patterns to include."),
    include_dot_dirs: bool = typer.Option(False, "--include-dot-dirs", help="Include dot-prefixed directories and files."),
    flatten: bool = typer.Option(False, "--flatten", help="Store files without directories inside the archive."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output."),
) -> None:
    lim = -1 if depth is None else depth
    ex_pats = pat_list(exclude)
    inc_pats = pat_list(match)
    files = collect(dir, lim, include_dot_dirs, ex_pats, inc_pats)
    if output is None:
        output = Path(f"{random.randint(100_000_000, 999_999_999)}.zip")
    used_names: set[str] = set()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            if flatten:
                full_ext = "".join(p.suffixes)
                root_name = p.name[: -len(full_ext)] if full_ext else p.name
                candidate = p.name
                if candidate in used_names:
                    i = 2
                    while True:
                        candidate = f"{root_name}_{i}{full_ext}"
                        if candidate not in used_names:
                            break
                        i += 1
                arc = candidate
                used_names.add(arc)
            else:
                arc = p.relative_to(dir)
            zf.write(p, arc)
            if verbose:
                typer.echo(f"added {arc}")
    typer.echo(f"created {output} with {len(files)} file(s)")
