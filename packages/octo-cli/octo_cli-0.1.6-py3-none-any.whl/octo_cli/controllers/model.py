import typer
from rich.console import Console
from rich.prompt import Prompt

from octo_cli.schemas.column import Column

console = Console()


def parse_type(py_type: str) -> str:
    datatypes = {
        "bool": "Boolean",
        "str": ["String", "Text"],
        "float": ["Double", "Float", "Numeric"],
        "datetime": ["Date", "DateTime", "Time"],
        "int": ["BigInteger", "Integer", "SmallInteger"],
    }

    if py_type not in datatypes:
        console.print(f"[bold red]Python type '{py_type}' not supported![/bold red]")
        return ""

    sql_type = datatypes[py_type]
    if not isinstance(sql_type, str):
        sql_type = Prompt.ask(
            "Select SQL generic datatype",
            choices=sql_type,
        )

    return sql_type


class ModelController:
    @staticmethod
    def is_duplicate() -> bool:
        return typer.confirm("\nIs a duplicate table?", default=True)

    @staticmethod
    def get_columns() -> list[Column]:
        console.print("Type 'END' to finish attribute declaration")
        columns = []
        while True:
            column_name = typer.prompt("Column name")
            if column_name == "END":
                break

            column_type = typer.prompt("Column type (python type, ex: int, str)")

            column = Column(
                name=column_name,
                type=column_type,
                sql_type=parse_type(column_type),
            )
            columns.append(column)

        return columns
