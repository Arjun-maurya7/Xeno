from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from model import Customer as DBCustomer
from schemas.customer import Customer, CustomerCreate
from services.segment_service import get_segmented_customers
from routes.utils import templates

router = APIRouter()

@router.post("/customer", response_model=Customer)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(DBCustomer).filter(DBCustomer.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_customer = DBCustomer(**customer.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.get("/customers/add")
def add_customer_form(request: Request):
    return templates.TemplateResponse("add_customer.html", {"request": request})

@router.post("/customers/add")
def handle_add_customer(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    city: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        customer_data = CustomerCreate(name=name, email=email, phone=phone, city=city)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_customer = db.query(DBCustomer).filter(DBCustomer.email == email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_customer = DBCustomer(**customer_data.model_dump())
    db.add(new_customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=303)

@router.get("/customers")
def customers_list(request: Request, db: Session = Depends(get_db)):
    customers_data = get_segmented_customers(db)
    return templates.TemplateResponse("customers_list.html", {"request": request, "customers": customers_data})

@router.get("/customer", response_model=list[Customer])
def get_customers(db: Session = Depends(get_db)):
    return db.query(DBCustomer).all()

@router.get("/customer/{id}", response_model=Customer)
def get_customer_by_id(id: int, db: Session = Depends(get_db)):
    customer = db.query(DBCustomer).filter(DBCustomer.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer does not exist")
    return customer

@router.put("/customer/{id}", response_model=Customer)
def update_customer(id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(DBCustomer).filter(DBCustomer.id == id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if customer.email != db_customer.email:
        email_exists = db.query(DBCustomer).filter(DBCustomer.email == customer.email).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already registered")

    for key, value in customer.model_dump().items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.delete("/customer/{id}")
def delete_customer(id: int, db: Session = Depends(get_db)):
    db_customer = db.query(DBCustomer).filter(DBCustomer.id == id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

@router.get("/customers/{id}")
def customer_detail_page(id: int, request: Request, db: Session = Depends(get_db)):
    db_customer = db.query(DBCustomer).filter(DBCustomer.id == id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    from model import Order as DBOrder
    orders = db.query(DBOrder).filter(DBOrder.customer_id == id).order_by(DBOrder.order_date.desc(), DBOrder.id.desc()).all()
    total_spend = sum(o.amount for o in orders)
    total_orders = len(orders)
    last_purchase = orders[0].order_date.strftime('%Y-%m-%d') if orders else "Never"
    
    from services.ai_service import generate_customer_persona
    persona = generate_customer_persona(db_customer.name, db_customer.city, total_spend, total_orders, orders)
    
    return templates.TemplateResponse(
        "customer_detail.html",
        {
            "request": request,
            "customer": db_customer,
            "orders": orders,
            "total_spend": total_spend,
            "total_orders": total_orders,
            "last_purchase": last_purchase,
            "persona": persona
        }
    )

