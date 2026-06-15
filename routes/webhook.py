"""
CRM Webhook Receipt API

This endpoint receives asynchronous delivery status callbacks
from the Channel Service and updates campaign statistics in the database.

This is the 'callback-driven loop' described in the Xeno assignment spec.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from model import Campaign as DBCampaign, CommunicationLog as DBCommunicationLog

router = APIRouter()
logger = logging.getLogger(__name__)


class DeliveryReceipt(BaseModel):
    campaign_id: int
    customer_id: int
    event: str   # "sent" | "delivered" | "opened" | "clicked" | "failed" | "converted" | "completed"
    amount: Optional[float] = None


@router.post("/webhook/receipt")
def handle_delivery_receipt(receipt: DeliveryReceipt, db: Session = Depends(get_db)):
    """
    Ingest a delivery event from the Channel Service and update
    the corresponding campaign's metrics and customer communication log.
    """
    event = receipt.event.lower()

    # If it is a global campaign completion/state update signal
    if receipt.customer_id == 0:
        campaign = db.query(DBCampaign).filter(DBCampaign.id == receipt.campaign_id).first()
        if campaign:
            campaign.status = event
            db.commit()
            logger.info(f"[Webhook] Campaign {receipt.campaign_id} status updated to {event}")
            return {"status": "ok", "campaign_id": receipt.campaign_id, "status_updated": event}
        return {"status": "ignored", "reason": "campaign not found"}

    campaign = db.query(DBCampaign).filter(DBCampaign.id == receipt.campaign_id).first()
    if not campaign:
        logger.warning(f"[Webhook] Received receipt for unknown campaign_id={receipt.campaign_id}")
        return {"status": "ignored", "reason": "campaign not found"}

    # Find or create CommunicationLog for this specific customer and campaign
    log_entry = db.query(DBCommunicationLog).filter(
        DBCommunicationLog.campaign_id == receipt.campaign_id,
        DBCommunicationLog.customer_id == receipt.customer_id
    ).first()

    if not log_entry:
        log_entry = DBCommunicationLog(
            campaign_id=receipt.campaign_id,
            customer_id=receipt.customer_id,
            status=event
        )
        db.add(log_entry)
    else:
        log_entry.status = event

    # Increment campaign aggregate statistics
    if event == "sent":
        campaign.sent = (campaign.sent or 0) + 1
        campaign.status = "sending"
    elif event == "delivered":
        campaign.delivered = (campaign.delivered or 0) + 1
    elif event == "opened":
        campaign.opened = (campaign.opened or 0) + 1
    elif event == "clicked":
        campaign.clicked = (campaign.clicked or 0) + 1
    elif event == "failed":
        campaign.failed = (campaign.failed or 0) + 1
    elif event == "converted":
        campaign.conversions = (campaign.conversions or 0) + 1
        amount = receipt.amount or 100.0
        campaign.revenue = round((campaign.revenue or 0.0) + amount, 2)

        # Create the attributed order in the database
        from model import Order as DBOrder
        from datetime import date
        new_order = DBOrder(
            customer_id=receipt.customer_id,
            campaign_id=receipt.campaign_id,
            amount=amount,
            order_date=date.today()
        )
        db.add(new_order)

    db.commit()
    logger.info(f"[Webhook] Campaign {receipt.campaign_id}, Customer {receipt.customer_id} updated: {event}")
    return {"status": "ok", "campaign_id": receipt.campaign_id, "customer_id": receipt.customer_id, "event": event}
