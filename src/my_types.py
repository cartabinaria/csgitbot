from pydantic import BaseModel

class Autor(BaseModel):
    name: str
    email: str