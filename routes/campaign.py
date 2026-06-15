import logging
from fastapi import APIRouter, Depends, Request, Form, BackgroundTasks, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from model import Campaign as DBCampaign, Customer as DBCustomer
from routes.utils import templates
from services.channel_service import simulate_campaign_delivery

router = APIRouter()
logger = logging.getLogger(__name__)

# ── Estimate audience size based on target audience string ───────────────────
def estimate_audience_size(db: Session, audience_str: str) -> int:
    """Return total customer count as a rough audience size proxy."""
    count = db.query(DBCustomer).count()
    return max(count, 1)  # at least 1


# ── Campaign Create ───────────────────────────────────────────────────────────
@router.get("/campaigns/create")
def add_campaign_form(request: Request):
    return templates.TemplateResponse(request=request, name="add_campaign.html")


@router.post("/campaigns/create")
def handle_add_campaign(
    name: str = Form(...),
    audience: str = Form(...),
    channel: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    campaign = DBCampaign(
        name=name, audience=audience, channel=channel,
        message=message, status="draft",
        sent=0, delivered=0, opened=0, clicked=0, failed=0,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return RedirectResponse(url="/campaigns", status_code=303)


# ── Campaign List ─────────────────────────────────────────────────────────────
@router.get("/campaigns")
def campaigns_list(request: Request, db: Session = Depends(get_db)):
    campaigns = db.query(DBCampaign).order_by(DBCampaign.id.desc()).all()
    return templates.TemplateResponse(
        request=request, name="campaigns_list.html", context={"campaigns": campaigns}
    )


# ── Launch Campaign (triggers Channel Service) ────────────────────────────────
@router.post("/campaigns/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        campaign = db.query(DBCampaign).filter(DBCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Treat NULL/empty status as 'draft' — safe to launch
        current_status = (campaign.status or "draft").strip().lower()
        if current_status in ("sending", "completed"):
            return JSONResponse(
                {"status": "error", "message": f"Campaign is already {current_status}."},
                status_code=400,
            )

        # Reset stats to 0 and mark as sending
        campaign.status = "sending"
        campaign.sent = 0
        campaign.delivered = 0
        campaign.opened = 0
        campaign.clicked = 0
        campaign.failed = 0
        campaign.conversions = 0
        campaign.revenue = 0.0
        db.commit()

        # Fetch all customers in the database to receive this campaign
        customers = db.query(DBCustomer).all()
        audience_size = len(customers)
        if audience_size == 0:
            return JSONResponse(
                {"status": "error", "message": "No customers found to send the campaign to."},
                status_code=400,
            )

        # Clear any existing communication logs for this campaign (in case of re-launch)
        from model import CommunicationLog as DBCommunicationLog
        db.query(DBCommunicationLog).filter(DBCommunicationLog.campaign_id == campaign.id).delete()

        # Pre-populate CommunicationLog entries for each customer
        logs = []
        for customer in customers:
            log_entry = DBCommunicationLog(
                campaign_id=campaign.id,
                customer_id=customer.id,
                status="sending"
            )
            logs.append(log_entry)
        db.add_all(logs)
        db.commit()

        # Get dynamic base URL from the incoming request (e.g., http://127.0.0.1:8000)
        base_url = str(request.base_url).rstrip("/")

        # Dispatch to the Channel Service asynchronously
        customer_ids = [c.id for c in customers]
        background_tasks.add_task(
            simulate_campaign_delivery,
            campaign_id=campaign.id,
            campaign_name=campaign.name,
            channel=campaign.channel,
            message=campaign.message,
            customer_ids=customer_ids,
            base_url=base_url
        )

        logger.info(f"[Campaign] Launched campaign_id={campaign_id} to {audience_size} recipients via {campaign.channel}")
        return JSONResponse({"status": "launched", "campaign_id": campaign_id, "audience_size": audience_size})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Campaign] Launch failed for campaign_id={campaign_id}: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


# ── Campaign Stats API (for live polling) ────────────────────────────────────
@router.get("/campaigns/{campaign_id}/stats")
def get_campaign_stats(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(DBCampaign).filter(DBCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {
        "id": campaign.id,
        "status": campaign.status,
        "sent": campaign.sent,
        "delivered": campaign.delivered,
        "opened": campaign.opened,
        "clicked": campaign.clicked,
        "failed": campaign.failed,
    }


# ── Generate Message with Gemini (AI assist) ──────────────────────────────────
@router.post("/campaigns/generate-message")
async def generate_campaign_message_route(request: Request):
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            data = await request.json()
            prompt = data.get("prompt", "")
        else:
            # Fallback to form data (e.g. if older JS version is cached in user's browser)
            data = await request.form()
            prompt = data.get("prompt", "")

        if not prompt:
            return JSONResponse({"detail": "Prompt is required"}, status_code=400)

        from services.ai_service import generate_campaign_message
        message = generate_campaign_message(prompt)
        return JSONResponse({"message": message})
    except Exception as e:
        logger.error(f"[Campaign] AI message generation failed: {e}")
        return JSONResponse({"detail": str(e)}, status_code=500)
