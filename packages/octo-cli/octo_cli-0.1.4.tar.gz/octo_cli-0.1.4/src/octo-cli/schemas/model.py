from pydantic import BaseModel

from schemas.column import Column


class Model(BaseModel):
    model_name: str
    classname: str
    is_duplicate: bool
    columns: list[Column] = []
