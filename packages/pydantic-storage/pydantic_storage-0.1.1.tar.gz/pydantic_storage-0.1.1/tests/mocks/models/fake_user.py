from pydantic import BaseModel


class FakeUser(BaseModel):
    id: int | None = None
    name: str
    email: str
