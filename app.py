from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from sqlalchemy import text
from routes import customer, order, segment, campaign, analytics, ai, dashboard, webhook

app = FastAPI(title="Xeno CRM")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create all tables (safe no-op if they exist)
Base.metadata.create_all(bind=engine)

# ── Database migrations: add any missing columns to campaigns & orders ────────
with engine.connect() as conn:
    try:
        # Migrate campaigns table
        cursor = conn.execute(text("PRAGMA table_info(campaigns)"))
        campaign_columns = [row[1] for row in cursor.fetchall()]

        campaign_migrations = {
            "sent":      "ALTER TABLE campaigns ADD COLUMN sent INTEGER DEFAULT 0",
            "delivered": "ALTER TABLE campaigns ADD COLUMN delivered INTEGER DEFAULT 0",
            "opened":    "ALTER TABLE campaigns ADD COLUMN opened INTEGER DEFAULT 0",
            "clicked":   "ALTER TABLE campaigns ADD COLUMN clicked INTEGER DEFAULT 0",
            "failed":    "ALTER TABLE campaigns ADD COLUMN failed INTEGER DEFAULT 0",
            "status":    "ALTER TABLE campaigns ADD COLUMN status TEXT DEFAULT 'draft'",
            "conversions": "ALTER TABLE campaigns ADD COLUMN conversions INTEGER DEFAULT 0",
            "revenue":   "ALTER TABLE campaigns ADD COLUMN revenue FLOAT DEFAULT 0.0",
        }

        for col, sql in campaign_migrations.items():
            if col not in campaign_columns:
                conn.execute(text(sql))

        # Migrate orders table
        cursor = conn.execute(text("PRAGMA table_info(orders)"))
        order_columns = [row[1] for row in cursor.fetchall()]
        if "campaign_id" not in order_columns:
            conn.execute(text("ALTER TABLE orders ADD COLUMN campaign_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL"))

        # Reset any stuck 'sending' campaigns to 'draft' so they can be launched again
        conn.execute(text(
            "UPDATE campaigns SET status = 'draft', sent = 0, delivered = 0, opened = 0, clicked = 0, failed = 0, conversions = 0, revenue = 0.0 "
            "WHERE status = 'sending'"
        ))
        conn.commit()
    except Exception as e:
        print(f"Migration note: {e}")

# ── Register all routers ─────────────────────────────────────────────────────
app.include_router(dashboard.router)
app.include_router(customer.router)
app.include_router(order.router)
app.include_router(segment.router)
app.include_router(campaign.router)
app.include_router(analytics.router)
app.include_router(ai.router)
app.include_router(webhook.router)