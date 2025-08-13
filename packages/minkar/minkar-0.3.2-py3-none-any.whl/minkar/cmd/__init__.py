import typer

from .cmd import app as cmd_app

app = typer.Typer()
app.add_typer(cmd_app)
