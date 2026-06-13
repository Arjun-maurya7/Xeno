from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from database import get_db
from model import Customer, Order, Campaign
from routes.utils import templates

router = APIRouter()

@router.get("/")
@router.get("/dashboard")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    # 1. Total Metrics
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_revenue = db.query(func.coalesce(func.sum(Order.amount), 0)).scalar() or 0.0
    active_campaigns = db.query(func.count(Campaign.id)).scalar() or 0
    
    # Calculate AOV
    aov = total_revenue / total_orders if total_orders > 0 else 0.0
    
    # 2. Recent Orders (limit 5)
    recent_orders = (
        db.query(Order)
        .options(joinedload(Order.customer))
        .order_by(Order.order_date.desc(), Order.id.desc())
        .limit(5)
        .all()
    )
    
    # 3. Top Spenders (limit 5)
    top_spenders_query = (
        db.query(
            Customer,
            func.coalesce(func.sum(Order.amount), 0).label("total_spend"),
            func.count(Order.id).label("total_orders")
        )
        .outerjoin(Order)
        .group_by(Customer.id)
        .order_by(func.coalesce(func.sum(Order.amount), 0).desc())
        .limit(5)
        .all()
    )
    
    top_spenders = []
    for customer, total_spend, total_orders_count in top_spenders_query:
        top_spenders.append({
            "id": customer.id,
            "name": customer.name,
            "city": customer.city,
            "total_spend": total_spend,
            "total_orders": total_orders_count
        })
        
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "aov": aov,
            "active_campaigns": active_campaigns,
            "recent_orders": recent_orders,
            "top_spenders": top_spenders
        }
    )
