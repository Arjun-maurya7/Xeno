from pydantic import BaseModel
from datetime import datetime

class CommunicationBase(BaseModel):
    customer_id: int
    campaign_id: int
    status: str

class CommunicationCreate(CommunicationBase):
    pass

class Communication(CommunicationBase):
    id: int
    sent_at: datetime

    model_config = {
        "from_attributes": True
    }
