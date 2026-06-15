from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from model import Order as DBOrder, Customer as DBCustomer
from schemas.order import Order
from routes.utils import templates
from datetime import date, datetime
import csv
import io

router = APIRouter()

@router.get("/orders/add")
def add_order_form(request: Request, db: Session = Depends(get_db)):
    customers = db.query(DBCustomer).all()
    return templates.TemplateResponse(request=request, name="add_order.html", context={"customers": customers})

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
    orders = db.query(DBOrder).order_by(DBOrder.id.desc()).all()
    return templates.TemplateResponse(request=request, name="orders_list.html", context={"orders": orders})

@router.get("/order/{id}", response_model=Order)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    order = db.query(DBOrder).filter(DBOrder.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/customers/{id}/orders", response_model=list[Order])
def get_orders_by_customer(id: int, db: Session = Depends(get_db)):
    return db.query(DBOrder).filter(DBOrder.customer_id == id).all()

# ── CSV Import ────────────────────────────────────────────────────────────────
@router.get("/orders/import")
def import_orders_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="import_orders.html",
        context={"success": None, "skipped": None, "error": None}
    )

@router.post("/orders/import")
async def handle_import_orders(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        return templates.TemplateResponse(
            request=request,
            name="import_orders.html",
            context={"success": None, "skipped": None, "error": "Invalid file type. Please upload a .csv file."}
        )
    try:
        content = await file.read()
        text_data = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text_data))

        required_cols = {"customer_email", "amount", "order_date"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            return templates.TemplateResponse(
                request=request,
                name="import_orders.html",
                context={"success": None, "skipped": None, "error": "CSV must have columns: customer_email, amount, order_date"}
            )

        success_count = 0
        skipped_count = 0

        for row in reader:
            email      = row.get("customer_email", "").strip()
            amount_str = row.get("amount", "").strip()
            date_str   = row.get("order_date", "").strip()

            if not email or not amount_str or not date_str:
                skipped_count += 1
                continue

            customer = db.query(DBCustomer).filter(DBCustomer.email == email).first()
            if not customer:
                skipped_count += 1
                continue

            try:
                amount     = float(amount_str)
                order_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                skipped_count += 1
                continue

            db.add(DBOrder(customer_id=customer.id, amount=amount, order_date=order_date))
            success_count += 1

        db.commit()
        return templates.TemplateResponse(
            request=request,
            name="import_orders.html",
            context={
                "success": f"Successfully imported {success_count} order(s).",
                "skipped": f"Skipped {skipped_count} row(s) — unknown email or bad format." if skipped_count else None,
                "error": None
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="import_orders.html",
            context={"success": None, "skipped": None, "error": f"Failed to parse CSV: {str(e)}"}
        )
