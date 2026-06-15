from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from model import Campaign as DBCampaign
from routes.utils import templates

router = APIRouter()

@router.get("/analytics")
def analytics_page(request: Request, db: Session = Depends(get_db)):
    campaigns = db.query(DBCampaign).all()
    return templates.TemplateResponse(request=request, name="analytics.html", context={"campaigns": campaigns})
