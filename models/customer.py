from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated

class Customer(BaseModel):
    id: int

    name: Annotated[
        str,
        Field(
            max_length=50,
            title="Name of Customer",
            description="Provide customer name in less than 50 characters",
            example="Arjun"
        )
    ]

    email: Annotated[
        EmailStr,
        Field(
            title="Email Address of Customer",
            description="Provide the email address of customer",
            example="arjunmaurya9026@gmail.com"
        )
    ]

    phone: Annotated[
        str,
        Field(
            pattern=r"^\d{10}$",
            title="Phone Number of Customer",
            description="Provide a valid 10-digit phone number",
            example="7054267380"
        )
    ]

    city: Annotated[
        str,
        Field(
            max_length=25,
            title="City of Customer",
            description="Provide the city name of customer",
            example="Pune"
        )
    ]
    @field_validator("city")
    def validate_city(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("City name should contain only letters")
        return value
    