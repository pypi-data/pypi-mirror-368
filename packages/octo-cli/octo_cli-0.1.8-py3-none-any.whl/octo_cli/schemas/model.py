from pydantic import BaseModel

from octo_cli.schemas.column import Column


class Model(BaseModel):
    model_name: str
    classname: str
    is_duplicate: bool
    columns: list[Column] = []
