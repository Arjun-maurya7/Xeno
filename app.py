from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from database import engine, Base
from sqlalchemy import text
from routes import customer, order, segment, campaign, analytics, ai, dashboard
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Xeno CRM")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create tables
Base.metadata.create_all(bind=engine)

# Database Schema migrations/updates for Campaign metrics
with engine.connect() as conn:
    try:
        cursor = conn.execute(text("PRAGMA table_info(campaigns)"))
        columns = [row[1] for row in cursor.fetchall()]
        if columns and "sent" not in columns:
            # Under SQLAlchemy 2.0, we execute the migrations and commit them
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN sent INTEGER DEFAULT 120"))
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN delivered INTEGER DEFAULT 110"))
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN opened INTEGER DEFAULT 85"))
            conn.execute(text("ALTER TABLE campaigns ADD COLUMN clicked INTEGER DEFAULT 38"))
            try:
                conn.commit()
            except Exception:
                pass
    except Exception as e:
        print(f"Migration error: {e}")

# Register modular routers
app.include_router(dashboard.router)
app.include_router(customer.router)
app.include_router(order.router)
app.include_router(segment.router)
app.include_router(campaign.router)
app.include_router(analytics.router)
app.include_router(ai.router)