from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, session
from models.customer import Customer

app = FastAPI()

Customers = [
    Customer(
        id=1,
        name="Arjun",
        email="arjunmaurya9023@gmail.com",
        phone="7054267380",
        city="Pune"
    )
]

# Database Setup
engine = create_engine("sqlite:///users.db")

@app.post("/customer")
async def create_customer(customer: Customer):
    Customers.append(customer)

    return {
        "message": "Customer created",
        "data": customer.model_dump()
    }

@app.get("/customer")
def get_customers():
    return Customers

@app.get("/customer/{id}")
def get_customer_by_id(id: int):
    for customer in Customers:
        if customer.id == id:
            return customer

    return {"message": "Customer does not exist"}

@app.put("/customer/{id}")
def update_customer(id: int, customer: Customer):
    for i in range(len(Customers)):
        if Customers[i].id == id:
            Customers[i] = customer
            return {
                "message": "Customer information updated successfully",
                "data": customer
            }

    return {"message": "Customer not found"}
    
@app.delete("/customer/{id}")
def delete_customer(id: int):
    for i in range(len(Customers)):
        if Customers[i].id == id:
            del Customers[i]
            return {"message": "Customer deleted successfully"}

    return {"message": "Customer not found"}