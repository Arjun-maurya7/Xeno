"""
Channel Service — Stubbed external messaging provider.

Per the Xeno assignment spec:
  "Stub the channel yourself as a separate service and model the full
   lifecycle of a communication."

This service simulates delivery for ANY channel (Email, SMS, WhatsApp, RCS)
by sending asynchronous HTTP callbacks to the CRM webhook receipt endpoint.

Delivery lifecycle: sent ➔ delivered/failed ➔ opened ➔ clicked ➔ converted
"""

import asyncio
import random
import logging
import httpx

logger = logging.getLogger(__name__)

# ── Realistic delivery, open, click, and conversion rates per channel ──────────
CHANNEL_RATES = {
    "email":    {"deliver": 0.92, "open": 0.35, "click": 0.08, "conversion": 0.10},
    "sms":      {"deliver": 0.97, "open": 0.85, "click": 0.20, "conversion": 0.12},
    "whatsapp": {"deliver": 0.96, "open": 0.78, "click": 0.25, "conversion": 0.15},
    "rcs":      {"deliver": 0.90, "open": 0.55, "click": 0.15, "conversion": 0.11},
}
DEFAULT_RATES = {"deliver": 0.90, "open": 0.50, "click": 0.12, "conversion": 0.10}


async def send_callback(campaign_id: int, customer_id: int, event: str, base_url: str, amount: float = None):
    """
    Sends an HTTP POST webhook callback back to the CRM Receipt API.
    Includes robust retry logic with exponential backoff.
    """
    url = f"{base_url}/webhook/receipt"
    payload = {
        "campaign_id": campaign_id,
        "customer_id": customer_id,
        "event": event
    }
    if amount is not None:
        payload["amount"] = amount

    max_retries = 3
    backoff = 0.5

    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(url, json=payload, timeout=5.0)
                if response.status_code == 200:
                    return True
                logger.warning(
                    f"[Channel] Callback failed (status={response.status_code}) for "
                    f"campaign={campaign_id} customer={customer_id} event={event}. Retrying..."
                )
            except Exception as e:
                logger.warning(
                    f"[Channel] Callback error ({e}) for campaign={campaign_id} "
                    f"customer={customer_id} event={event}. Retrying..."
                )
            await asyncio.sleep(backoff)
            backoff *= 2

    logger.error(
        f"[Channel] Permanent callback failure for campaign={campaign_id} "
        f"customer={customer_id} event={event}"
    )
    return False


async def simulate_campaign_delivery(
    campaign_id: int,
    campaign_name: str,
    channel: str,
    message: str,
    customer_ids: list[int],
    base_url: str,
):
    """
    Fully async delivery simulation. For each customer in the target audience,
    models the complete communication lifecycle and triggers asynchronous HTTP callbacks.
    """
    ch = channel.strip().lower()
    rates = CHANNEL_RATES.get(ch, DEFAULT_RATES)

    logger.info(
        f"[Channel] Starting simulation callback loop for campaign '{campaign_name}' "
        f"(id={campaign_id}, channel={channel}, recipients={len(customer_ids)})"
    )

    # ── 1. SENT — immediate ───────────────────────────────────────────────────
    sent_tasks = [send_callback(campaign_id, cid, "sent", base_url) for cid in customer_ids]
    await asyncio.gather(*sent_tasks)
    await asyncio.sleep(1.0)

    # ── 2. DELIVERED / FAILED ─────────────────────────────────────────────────
    delivered_cids = []
    delivery_tasks = []

    for cid in customer_ids:
        is_delivered = random.random() < rates["deliver"]
        if is_delivered:
            delivered_cids.append(cid)
            delivery_tasks.append(send_callback(campaign_id, cid, "delivered", base_url))
        else:
            delivery_tasks.append(send_callback(campaign_id, cid, "failed", base_url))

    if delivery_tasks:
        await asyncio.gather(*delivery_tasks)
    await asyncio.sleep(1.0)

    # ── 3. OPENED ─────────────────────────────────────────────────────────────
    opened_cids = []
    open_tasks = []

    for cid in delivered_cids:
        is_opened = random.random() < rates["open"]
        if is_opened:
            opened_cids.append(cid)
            open_tasks.append(send_callback(campaign_id, cid, "opened", base_url))

    if open_tasks:
        await asyncio.gather(*open_tasks)
    await asyncio.sleep(1.0)

    # ── 4. CLICKED ────────────────────────────────────────────────────────────
    clicked_cids = []
    click_tasks = []

    for cid in opened_cids:
        is_clicked = random.random() < rates["click"]
        if is_clicked:
            clicked_cids.append(cid)
            click_tasks.append(send_callback(campaign_id, cid, "clicked", base_url))

    if click_tasks:
        await asyncio.gather(*click_tasks)
    await asyncio.sleep(1.0)

    # ── 5. CONVERTED (Attributes order conversions) ───────────────────────────
    conversion_tasks = []

    for cid in clicked_cids:
        is_converted = random.random() < rates["conversion"]
        if is_converted:
            # Generate random order amount between $30 and $300
            order_amount = round(random.uniform(30.0, 300.0), 2)
            conversion_tasks.append(send_callback(campaign_id, cid, "converted", base_url, amount=order_amount))

    if conversion_tasks:
        await asyncio.gather(*conversion_tasks)

    # Final status update call to ensure status is marked as completed
    await send_callback(campaign_id, 0, "completed", base_url)

    logger.info(f"[Channel] Simulation complete for campaign={campaign_id}")
