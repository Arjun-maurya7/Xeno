from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from model import Campaign as DBCampaign
from routes.utils import templates

router = APIRouter()

@router.get("/campaigns/create")
def add_campaign_form(request: Request):
    return templates.TemplateResponse("add_campaign.html", {"request": request})

@router.post("/campaigns/create")
def handle_add_campaign(
    name: str = Form(...),
    audience: str = Form(...),
    channel: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    campaign = DBCampaign(name=name, audience=audience, channel=channel, message=message)
    db.add(campaign)
    db.commit()
    return RedirectResponse(url="/campaigns", status_code=303)

@router.get("/campaigns")
def campaigns_list(request: Request, db: Session = Depends(get_db)):
    campaigns = db.query(DBCampaign).all()
    return templates.TemplateResponse("campaigns_list.html", {"request": request, "campaigns": campaigns})
