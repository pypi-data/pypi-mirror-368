from pydantic import BaseModel


class HealthzResponse(BaseModel):
    message:str
    

    
