from pydantic import BaseModel

from .column import Column


class Model(BaseModel):
    model_name: str
    classname: str
    is_duplicate: bool
    columns: list[Column] = []
