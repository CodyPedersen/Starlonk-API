from typing import Optional
from pydantic import BaseModel

# Currently unused
class Process(BaseModel):
    id: str
    status: str
    time_created: Optional[str]
    time_updated: Optional[str]