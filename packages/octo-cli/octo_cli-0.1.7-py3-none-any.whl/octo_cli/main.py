from rich import print
from typer import Typer

from octo_cli.commands import new

app = Typer()
print("Welcome to [#F75E5B]OCTO[/]:octopus:!")

app.add_typer(new.app, name="new")
