from typer import Typer
from .get import app as get_app
from .cmd import app as command_app

app = Typer()
app.add_typer(get_app, name="get", help="Collecting information about the project.")
app.add_typer(command_app, name="cmd", help="Manage saved commands.")

if __name__ == "__main__":
    app()
