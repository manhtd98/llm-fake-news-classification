from pydantic import BaseModel


class QueryDocument(BaseModel):
    query: str
    topk: int
