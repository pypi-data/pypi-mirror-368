from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

import typer

app = typer.Typer(add_completion=False, help="Manage saved shell commands.")

STORE_PATH = Path.home() / ".minkar_commands.json"


def _load() -> List[Dict[str, str]]:
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(data: List[Dict[str, str]]) -> None:
    STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _index(data: List[Dict[str, str]], name: str) -> int:
    for i, item in enumerate(data):
        if item["name"] == name:
            return i
    raise typer.BadParameter(f"cmd '{name}' not found")


@app.command(help="Save a command under a name.")
def save(
    command: str = typer.Argument(..., help="Shell command text. Use '{*}' placeholders for positional values."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom name. Defaults to 'cmd{N}'."),
    overwrite: bool = typer.Option(False, "--overwrite", "-o", help="Overwrite existing command with the same name."),
) -> None:
    data = _load()
    cmd_name = name or f"cmd{len(data) + 1}"
    try:
        idx = _index(data, cmd_name)
        if not overwrite:
            raise typer.BadParameter(f"cmd '{cmd_name}' already exists")
        data[idx]["cmd"] = command
    except typer.BadParameter:
        data.append({"name": cmd_name, "cmd": command})
    _save(data)
    typer.echo(f"saved '{cmd_name}'")


@app.command(help="Delete a saved command by name.")
def delete(name: str = typer.Argument(..., help="Command name to delete.")) -> None:
    data = _load()
    idx = _index(data, name)
    data.pop(idx)
    _save(data)
    typer.echo(f"deleted '{name}'")


@app.command("delete-all", help="Delete all saved commands.")
def delete_all(confirm: bool = typer.Option(False, "--yes", "-y", help="Confirm deletion of all commands.")) -> None:
    if not confirm:
        raise typer.BadParameter("confirmation required --yes")
    _save([])
    typer.echo("all commands deleted")


@app.command(help="Edit the command text for an existing name.")
def edit(
    name: str = typer.Argument(..., help="Existing command name."),
    command: str = typer.Argument(..., help="New shell command text."),
) -> None:
    data = _load()
    idx = _index(data, name)
    data[idx]["cmd"] = command
    _save(data)
    typer.echo(f"updated '{name}'")


@app.command(help="Run a saved command.")
def run(
    name: str = typer.Argument(..., help="Saved command name to execute."),
    args: str = typer.Option("", "--args", "-a", help="Comma-separated values for '{*}' placeholders."),
    shell: str = typer.Option("auto", "--shell", "-s", help="Shell to use. 'auto' picks OS default (cmd.exe on Windows, /bin/sh on Unix). Examples: bash, zsh, powershell, pwsh, cmd."),
) -> None:
    data = _load()
    idx = _index(data, name)
    cmd = data[idx]["cmd"]

    if args.strip():
        for arg in args.split(","):
            cmd = cmd.replace("{*}", arg, 1)

    typer.echo(f"$ {cmd}")

    if shell.lower() == "auto":
        subprocess.run(cmd, shell=True, check=False)
        return

    exe = shell
    sh = shell.lower()
    if os.name == "nt":
        if sh in {"cmd", "cmd.exe"}:
            exe = os.environ.get("COMSPEC", "cmd.exe")
        elif sh in {"powershell", "powershell.exe"}:
            exe = "powershell"
        elif sh in {"pwsh", "pwsh.exe"}:
            exe = "pwsh"
    subprocess.run(cmd, shell=True, executable=exe, check=False)


@app.command("list", help="List saved commands.")
def list_() -> None:
    data = _load()
    if not data:
        typer.echo("no commands saved")
        raise typer.Exit()
    for i, item in enumerate(data, 1):
        typer.echo(f"{i}. {item['name']} -> {item['cmd']}")
