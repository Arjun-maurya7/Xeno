from pydantic import BaseModel, Field
from datetime import date
from typing import Annotated

class OrderBase(BaseModel):
    amount: Annotated[
        float,
        Field(
            title="Amount of Order",
            description="Provide the amount of order",
            example=100
        )
    ]

    order_date: Annotated[
        date,
        Field(
            title="Order Date of Order",
            description="Provide the order date of order",
            example="2022-01-01"
        )
    ]

    customer_id: Annotated[
        int,
        Field(
            title="Customer ID of Order",
            description="Provide the customer id of order",
            example=1
        )
    ]


class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int

    model_config = {
        "from_attributes": True
    }