from pydantic import BaseModel

class ProcessQueryPayload(BaseModel):    
    query : str