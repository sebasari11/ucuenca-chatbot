from pydantic import BaseModel


class IngestResponse(BaseModel):
    message: str
    resource_id: int
