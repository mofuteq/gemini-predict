from pydantic import BaseModel


class Race(BaseModel):
    place: str
    number: int
    name: str
