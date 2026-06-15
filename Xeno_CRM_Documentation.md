# Xeno CRM - Complete Technical Architecture & System Documentation

Welcome to the technical documentation of **Xeno CRM**. This document is formatted for Obsidian and is designed to give you a deep, comprehensive understanding of how every component in this project works. Whether you need to explain the system during a technical placement interview or scale it further, this guide covers everything.

---

## 📂 1. Project Directory Structure & Modular Design

Xeno CRM follows a clean, modular architecture separating the Presentation Layer (HTML templates and static assets), the API Router Layer (fastapi routes), the Data Access Layer (SQLAlchemy models), and the Services/Business Logic Layer.

```text
CRM/
│
├── app.py                      # Application entry point & service startup
├── database.py                 # SQLite database engine & session pool setup
├── model.py                    # Unified database models (SQLAlchemy ORM)
├── requirements.txt            # Python environment dependencies
├── .env                        # Environment variables (GEMINI_API_KEY)
│
├── routes/                     # API routers (endpoints)
│   ├── utils.py                # Shared router utilities (e.g., Jinja templates)
│   ├── dashboard.py            # KPI metrics & leaderboard logic
│   ├── customer.py             # Customer CRUD & Profile Page
│   ├── order.py                # Order CRUD & listings
│   ├── segment.py              # Query-based customer segmentation
│   ├── campaign.py             # Campaign CRUD
│   ├── analytics.py            # Campaign CTR metrics
│   └── ai.py                   # AI-powered operations (Gemini integration)
│
├── services/                   # Business logic & external service integrations
│   ├── segment_service.py      # Customer filtering & spend aggregation logic
│   └── ai_service.py           # Gemini API parser & generator
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Premium vanilla CSS styling system
│   └── js/
│       └── app.js              # Centralized AJAX logic (AI generation actions)
│
└── templates/                  # Jinja2 HTML rendering templates
    ├── dashboard.html          # CRM statistics & recent activity
    ├── customer_detail.html    # Profile page, buying persona & order timeline
    ├── customers_list.html     # Interactive directory
    ├── add_customer.html       # Customer creation form
    ├── orders_list.html        # Order transactions list
    ├── add_order.html          # Order creation form
    ├── segments.html           # Manual segments filter
    ├── campaigns_list.html     # Saved campaigns
    ├── add_campaign.html       # Campaign composer
    └── analytics.html          # Campaign CTR metric cards
```

---

## 🗄️ 2. Data Access Layer (Database & ORM Models)

Xeno CRM uses **SQLite** as its relational database and **SQLAlchemy** as the Object Relational Mapper (ORM). Models are configured in `model.py` and derive from a shared declarative `Base` declared in `database.py`.

### Database Schema Entity Relationship (ER) Diagram
- **Customer (1) ── (N) Order**: One customer can place multiple orders. Declared via a foreign key relationship with cascading deletes (`ondelete="CASCADE"`).
- **Campaign (Standalone)**: Stores campaign information, including synthetic tracking analytics (sent, delivered, opened, clicked) for CTR analysis.

```python
# database.py
from sqlalchemy import create_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./crm.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Models (`model.py`)
1. **`Customer`**:
   - `id`: Primary key.
   - `name`, `email`, `phone`, `city`: Text/String columns.
   - `orders`: Defined as a relationship referencing the `Order` model. `cascade="all, delete-orphan"` ensures that deleting a customer automatically deletes all their orders.
2. **`Order`**:
   - `id`: Primary key.
   - `customer_id`: Foreign Key targeting `customers.id`.
   - `amount`: Float representation of transaction value.
   - `order_date`: Date object.
3. **`Campaign`**:
   - `id`: Primary key.
   - `name`, `audience`, `channel` (email/sms/whatsapp), `message`.
   - `sent`, `delivered`, `opened`, `clicked`: Synthetic counters used to calculate CTR (Click-Through Rate).

---

## ⚙️ 3. Services & Business Logic Layer

By separating business logic from raw route handlers, the code remains clean, maintainable, and testable.

### Customer Segmentation (`services/segment_service.py`)
This service aggregates metrics to compute dynamic fields: **Total Spend**, **Last Purchase Date**, and **Total Orders Count**.
*   **The SQL aggregation logic**:
    It queries the `Customer` table, left-joins the `Order` table, groups by the customer's ID, and utilizes database-level aggregations (`func.sum`, `func.max`, `func.count`) to compile metrics.
*   **Handling Null comparisons**:
    Customers with zero orders return `NULL` for sums/dates. We use `func.coalesce(func.sum(Order.amount), 0)` to guarantee numeric comparisons work properly.
    Additionally, inactive days checks construct a threshold date (`date.today() - timedelta(days=inactive_days)`). To safely include inactive customers who have never placed an order, we check:
    `or_(func.max(Order.order_date) <= threshold, func.max(Order.order_date) == None)`.

### Gemini AI Service (`services/ai_service.py`)
Integrates the `google-generativeai` package using `gemini-1.5-flash` to process two complex requirements:
1.  **AI Segment Parser (`parse_segment_prompt`)**:
    Takes a natural language request (e.g., *"Customers who spent more than $5000 and haven't bought in 30 days"*) and prompts Gemini to output a structured JSON response:
    ```json
    {
      "min_spend": 5000,
      "inactive_days": 30
    }
    ```
    This JSON is parsed and fed directly into `get_segmented_customers()` to query the database.
2.  **AI Customer Persona Generator (`generate_customer_persona`)**:
    Constructs a prompt with the customer's shopping metrics (total spent, location, count, recent orders list) and instructs Gemini to return a concise, 2-sentence marketing persona profile.

---

## 🌐 4. API Endpoints & Routes Layer

Each API domain operates inside its own `APIRouter` module, avoiding circular dependencies and keeping routing isolated.

| Endpoint | Method | File | Description |
| :--- | :--- | :--- | :--- |
| `/` or `/dashboard` | `GET` | `routes/dashboard.py` | Renders Dashboard metrics, recent orders, and top spenders |
| `/customers` | `GET` | `routes/customer.py` | Customer list directory |
| `/customers/add` | `GET`/`POST` | `routes/customer.py` | Form rendering and submission for new customers |
| `/customers/{id}` | `GET` | `routes/customer.py` | Customer Profile page, timeline, and AI persona generator |
| `/orders` | `GET` | `routes/order.py` | Order history log |
| `/orders/add` | `GET`/`POST` | `routes/order.py` | Forms and creation database operations for orders |
| `/segments` | `GET`/`POST` | `routes/segment.py` | Filter form based segmentation tool |
| `/campaigns` | `GET` | `routes/campaign.py` | List of composed campaigns |
| `/campaigns/create` | `GET`/`POST` | `routes/campaign.py` | Creates and saves a marketing campaign |
| `/analytics` | `GET` | `routes/analytics.py` | Renders CTR analytical cards |
| `/ai-segment` | `GET`/`POST` | `routes/ai.py` | Natural language text prompt to query database |
| `/campaigns/generate-message` | `POST` | `routes/ai.py` | AJAX callback to generate win-back copy with Gemini |

---

## 🎨 5. Frontend & CSS Theme Architecture

The visual theme uses modern **Vanilla CSS** centered on variables and glassmorphism design:
*   **CSS Variables (`static/css/style.css`)**:
    Defines modern color tokens (`--bg-color: #0f172a`, `--card-bg: #1e293b`, `--primary: #3b82f6`) that ensure consistency across the dark theme UI.
*   **AI Persona Card Glow**:
    Designed using custom gradient border overlays and box-shadow glows:
    `box-shadow: 0 0 25px rgba(167, 139, 250, 0.15)`
*   **Vertical Timeline**:
    Uses absolute positioning to align a pseudo-element line (`timeline::before`) and bullet markers (`timeline-badge`), establishing a clean vertical purchase trail.

---

## 🎓 6. Technical Placement Interview Guide (Q&A)

Here are the key questions technical interviewers might ask you about this codebase, along with structural answers:

### Q1: Why did you choose FastAPI over traditional frameworks like Django or Flask?
*   **Answer**:
    "FastAPI is built directly on ASGI (Asynchronous Server Gateway Interface), making it significantly faster than WSGI frameworks like Flask. It features native integration with Pydantic for automated data validation and parsing, and automatically generates interactive OpenAPI/Swagger documentation. By using FastAPI, I was able to decouple routers cleanly, enforce structured schemas, and handle requests asynchronously."

### Q2: How did you implement the AI Customer Segment tool? Detail the data flow.
*   **Answer**:
    1. The user inputs a natural language prompt (e.g. *"customers in Pune with total spending above $2000"*).
    2. The `/ai-segment` route sends this string to `services/ai_service.py`.
    3. We instruct the Gemini API (`gemini-1.5-flash`) to analyze the prompt and output a strictly structured JSON containing key-value configurations (`min_spend`, `inactive_days`, `city`).
    4. The JSON is parsed, and we extract these variables.
    5. We pass these variables into `segment_service.get_segmented_customers(db, min_spend, inactive_days, city)`.
    6. The database returns the matching customer entities, which are then rendered on the results page.

### Q3: Explain how you resolved the SQL "Null Comparison" bug in your inactive customer queries.
*   **Answer**:
    "If a customer has never placed an order, their aggregate transaction value is `NULL`. A standard SQL query comparing `MAX(order_date) <= threshold_date` will discard these records because comparisons with `NULL` result in unknown/false states in SQL.
    To fix this, I adjusted the query filters in SQLAlchemy to explicitly check for `NULL` order dates using an `or_` clause:
    `or_(func.max(Order.order_date) <= threshold_date, func.max(Order.order_date) == None)`.
    This ensures customers who have never placed an order are correctly classified as inactive instead of being discarded."

### Q4: How is database migration handled in this project?
*   **Answer**:
    "FastAPI creates tables defined in `model.py` using `Base.metadata.create_all(bind=engine)` at startup. For updating existing tables (like adding campaign metrics tracking columns), I implemented a migration script block using SQLAlchemy raw SQL execution:
    1. Connect to the engine and run a SQLite table information check: `PRAGMA table_info(campaigns)`.
    2. Fetch the column list and check if our metrics columns (sent, delivered, opened, clicked) are present.
    3. If they are absent, run `ALTER TABLE campaigns ADD COLUMN ...` statements, and issue a connection transaction commit. This ensures database schema updates run safely at startup without losing existing data."

### Q5: What is the purpose of Jinja2Templates, and how do you avoid circular imports in a modular structure?
*   **Answer**:
    "In a modular FastAPI setup, multiple route modules need to render templates. If each route module imports the main `app` instance to access rendering functions, it causes circular import cycles.
    To prevent this, I created a utility router module `routes/utils.py` that instantiates `templates = Jinja2Templates(directory="templates")`. Each router (e.g. `routes/customer.py`) imports `templates` from this utility file, decoupling route definition from the main `app.py` entrypoint."
