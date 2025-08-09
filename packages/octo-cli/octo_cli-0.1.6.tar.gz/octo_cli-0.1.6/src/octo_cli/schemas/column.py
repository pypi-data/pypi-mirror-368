from pydantic import BaseModel


class Column(BaseModel):
    name: str
    type: str
    sql_type: str
