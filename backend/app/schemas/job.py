from pydantic import BaseModel, ConfigDict
from uuid import UUID

class JobRead(BaseModel):                 # public view of a posting — no embedding, no hash
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    company: str | None
    location: str | None
    url: str
 
class JobMatch(BaseModel):                # a search result for the API: posting + per-match data
    model_config = ConfigDict(from_attributes=True)
    job: JobRead
    rank: int
    score: float
    explanation: str
 
