from pydantic import BaseModel
from typing import Optional

class ProcessQueryPayload(BaseModel):    
    query : str