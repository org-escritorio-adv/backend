from datetime import date

from pydantic import BaseModel


class Movement(BaseModel):
    date: date
    description: str
