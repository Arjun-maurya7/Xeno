from pydantic import BaseModel, Field
from typing import Annotated

class CampaignBase(BaseModel):
    name: Annotated[
        str,
        Field(
            title="Campaign Name",
            description="Provide the name of the campaign",
            example="Summer Discount"
        )
    ]
    audience: Annotated[
        str,
        Field(
            title="Audience Group",
            description="Provide the target audience group description",
            example="High Value Customers"
        )
    ]
    channel: Annotated[
        str,
        Field(
            title="Communication Channel",
            description="Provide the channel for the campaign (e.g. Email, SMS)",
            example="Email"
        )
    ]
    message: Annotated[
        str,
        Field(
            title="Message Text",
            description="Provide the text of the campaign message",
            example="Get 20% Off Today"
        )
    ]


class CampaignCreate(CampaignBase):
    pass


class Campaign(CampaignBase):
    id: int

    model_config = {
        "from_attributes": True
    }
