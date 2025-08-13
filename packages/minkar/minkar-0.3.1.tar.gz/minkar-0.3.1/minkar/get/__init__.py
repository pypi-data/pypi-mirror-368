from typer import Typer
from .code import app as code_app
from .dir  import app as dir_app
from .file import app as file_app

app = Typer()
app.add_typer(code_app, name="code")
app.add_typer(dir_app,  name="dir")
app.add_typer(file_app, name="file")
