from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from model import Order as DBOrder, Customer as DBCustomer
from schemas.order import Order
from routes.utils import templates
from datetime import date

router = APIRouter()

@router.get("/orders/add")
def add_order_form(request: Request, db: Session = Depends(get_db)):
    customers = db.query(DBCustomer).all()
    return templates.TemplateResponse(
        "add_order.html",
        {
            "request": request,
            "customers": customers
        }
    )

@router.post("/orders/add")
def handle_add_order(
    customer_id: int = Form(...),
    amount: float = Form(...),
    order_date: date = Form(...),
    db: Session = Depends(get_db)
):
    order = DBOrder(customer_id=customer_id, amount=amount, order_date=order_date)
    db.add(order)
    db.commit()
    return RedirectResponse(url="/orders", status_code=303)

@router.get("/orders")
def orders_list(request: Request, db: Session = Depends(get_db)):
    orders = db.query(DBOrder).all()
    return templates.TemplateResponse("orders_list.html", {"request": request, "orders": orders})

@router.get("/order/{id}", response_model=Order)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    order = db.query(DBOrder).filter(DBOrder.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/customers/{id}/orders", response_model=list[Order])
def get_orders_by_customer(id: int, db: Session = Depends(get_db)):
    orders = db.query(DBOrder).filter(DBOrder.customer_id == id).all()
    return orders
