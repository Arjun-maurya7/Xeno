from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from model import Customer, Order
from datetime import date, timedelta

def get_segmented_customers(db: Session, min_spend: float = None, inactive_days: int = None, city: str = None):
    query = db.query(
        Customer,
        func.coalesce(func.sum(Order.amount), 0).label("total_spend"),
        func.max(Order.order_date).label("last_purchase"),
        func.count(Order.id).label("total_orders")
    ).outerjoin(Order).group_by(Customer.id)
    
    having_clauses = []
    if min_spend is not None and min_spend > 0:
        having_clauses.append(func.coalesce(func.sum(Order.amount), 0) >= min_spend)
    if inactive_days is not None and inactive_days > 0:
        threshold_date = date.today() - timedelta(days=inactive_days)
        having_clauses.append(
            or_(
                func.max(Order.order_date) <= threshold_date,
                func.max(Order.order_date) == None
            )
        )
        
    if having_clauses:
        query = query.having(and_(*having_clauses))
        
    if city and city.strip():
        query = query.filter(Customer.city.ilike(f"%{city.strip()}%"))
        
    results = query.all()
    
    customers_data = []
    for customer, total_spend, last_purchase, total_orders in results:
        customers_data.append({
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "city": customer.city,
            "total_spend": total_spend,
            "last_purchase": last_purchase.strftime('%Y-%m-%d') if last_purchase else "Never",
            "total_orders": total_orders
        })
    return customers_data
