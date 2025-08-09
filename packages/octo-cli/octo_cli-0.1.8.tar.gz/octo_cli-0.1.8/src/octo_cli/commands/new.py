import os

from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console
from typer import Typer

from octo_cli.controllers.model import ModelController
from octo_cli.schemas.model import Model

app = Typer()
console = Console()


@app.command()
def model(name: str):
    controller = ModelController

    console.print(f"\nCreating new model: {name}")

    config = Model(
        model_name=name,
        classname=name.title().replace("_", ""),
        is_duplicate=controller.is_duplicate(),
    )

    env = Environment(
        loader=PackageLoader("octo_cli"),
        autoescape=select_autoescape(),
    )

    template = env.get_template("model.py.j2")

    if config.is_duplicate:
        result = template.render(config.model_dump())

        console.print(result, markup=False)
        return

    config.columns = controller.get_columns()
    result = template.render(config.model_dump())

    console.print(result, markup=False)

    try:
        os.mkdir("models")
        console.print("New directory '/models' created.")
    except FileExistsError:
        pass

    with open(f"models/{name}.py", "w") as file:
        file.write(result)
