from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from database import get_db
from services.segment_service import get_segmented_customers
from routes.utils import templates

router = APIRouter()

@router.get("/segments")
def segments_page(request: Request):
    return templates.TemplateResponse(
        "segments.html",
        {
            "request": request,
            "customers": [],
            "min_spend": None,
            "inactive_days": None,
            "city": None
        }
    )

@router.post("/segments")
def generate_segment(
    request: Request,
    min_spend: float = Form(0.0),
    inactive_days: int = Form(None),
    city: str = Form(None),
    db: Session = Depends(get_db)
):
    customers_data = get_segmented_customers(db, min_spend=min_spend, inactive_days=inactive_days, city=city)
    return templates.TemplateResponse(
        "segments.html",
        {
            "request": request,
            "customers": customers_data,
            "min_spend": min_spend,
            "inactive_days": inactive_days,
            "city": city
        }
    )
