from pydantic import BaseModel, HttpUrl

class SourceSchema(BaseModel):
    id: str
    name: str
    url: HttpUrl
